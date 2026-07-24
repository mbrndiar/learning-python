# 📦 Chapter 6: Modules and Packages

**Semantic ID:** `module.modules-and-packages` · **Prerequisites:**
`module.function-contracts-and-scope`

## 📍 Where this fits

Chapters 1-5 built every program as a single file, top to bottom. That stops
scaling once code needs to be reused across files, organized into related
groups, or given a boundary between "what callers should use" and
"internal detail." This chapter introduces modules and packages: how
`import` finds and caches code, how a directory becomes a package, how
absolute and relative imports resolve, and how a file's `__name__`
distinguishes "run directly" from "imported." This is the first chapter to
use `import` as its own subject rather than as an incidental tool for
reaching `math` or `random`.

## 🎯 Learning objectives

After this chapter, you should be able to:

- explain that a module is an ordinary object, and that `import` caches it
  in `sys.modules` so repeated imports do not re-run its top-level code;
- use all four import forms (`import x`, `import x as y`, `from x import
  y`, `from x import y as z`) and explain how each affects the local
  namespace;
- lay out a package with `__init__.py`, distinguish absolute imports from
  package-relative (dotted) imports, and explain why relative imports only
  work when a module is loaded as part of a package;
- run a package as a program with `python -m`, and explain why that differs
  from running a `.py` file by its bare path;
- explain what `__name__ == "__main__"` means and use it to guard
  script-only code inside an importable module;
- explain that importing a module always runs its top-level code once, as
  an import-time side effect, independent of any guarded block;
- re-export selected names and use `__all__` to document (not enforce) a
  small public API.

## 🧠 Motivation and mental model

Every `import` you have already written (`import math`, `from datetime
import date`) quietly relied on machinery this chapter now makes explicit:
Python finds a module, runs its top-level code exactly once, and stores the
resulting object so later imports reuse it instead of re-running it. A
package is the same idea one level up -- a directory of related modules
with its own `__init__.py` that runs once, the first time anything inside
it is imported. Once imports and packages are explicit, "public API" stops
being an abstract phrase: it is the specific set of names a module or
package chooses to re-export and document with `__all__`, distinct from
everything else that merely happens to be reachable.

## 1️⃣ Module objects, the import cache, and import forms

A module is not special syntax handed to you by the language -- it is an
ordinary object, produced by running a file's top-level code once and
keeping the result. `import math` is doing exactly that:

```python
import math

print("type(math):", type(math))
print("math.pi:", math.pi)
```

```text
type(math): <class 'module'>
math.pi: 3.141592653589793
```

`math` is bound to a module object. `math.pi` and `math.sqrt` are looked up
as attributes on it, the same way `some_list.append` is an attribute lookup
on a list object.

### The import cache: `sys.modules`

The first `import math` anywhere in a process runs `math`'s top-level code
and stores the resulting object in `sys.modules`, keyed by module name.
Every later `import math` -- in this file or any other module in the same
process -- reuses that cached object instead of re-running it:

```python
import sys

assert sys.modules["math"] is math
print("Cached module is the same object:", sys.modules["math"] is math)
```

```text
Cached module is the same object: True
```

`sys.modules["math"] is math` is `True`: both names refer to the identical
module object, not two separate copies.

### Four import forms bind names differently

```python
import random as rng               # import ... as ...: chosen local name
from datetime import date          # from ... import ...: direct name
from datetime import timedelta as delta  # combine both
```

Together with the plain `import math` above, these are the four forms:
`import x`, `import x as y`, `from x import y`, and `from x import y as z`.
Every form still imports (and caches) the target module the same way --
only the *local name(s)* bound in the importing file differ.

### Namespacing avoids collisions; direct imports can be shadowed

```python
def sqrt(value):
    return f"custom sqrt of {value}"


print("Local sqrt(9):", sqrt(9))
print("math.sqrt(9):", math.sqrt(9))
```

```text
Local sqrt(9): custom sqrt of 9
math.sqrt(9): 3.0
```

Because `math` was imported as a whole module, this file's own `sqrt` and
`math.sqrt` coexist without conflict -- that is what namespacing buys.
Had the file instead written `from math import sqrt`, the `def` above
would have silently replaced the imported name, and reaching the original
would require going back through the module (`math.sqrt`).

Run the complete companion:

```bash
python lessons/06_modules_and_packages/01_modules_and_imports.py
```

See [`01_modules_and_imports.py`](01_modules_and_imports.py) for the full
sequence, including `dir()` used to list a module's bound names.

> **Try one change:** change `import math` to `import math as m` and use
> `m.pi` instead. Predict whether `sys.modules` still uses the key
> `"math"`. Only the local name changes; the cache key and the module
> object itself do not.

## 2️⃣ Package layout, `__init__.py`, and import resolution

A module is one `.py` file; a **package** is a directory that groups
related modules and is marked by an `__init__.py` file (even an empty
one). This lesson uses a small `example_package/` alongside it:

```text
example_package/
    __init__.py      # runs once, on first import; re-exports the API
    __main__.py       # runs when the package itself is executed
    greetings.py      # the public module: hello(), shout_hello()
    _formatting.py    # an internal module: leading underscore = detail
```

### Absolute imports and re-exports

```python
from example_package import shout_hello
from example_package.greetings import hello

print(hello("ada lovelace"))
print(shout_hello("grace hopper"))
```

```text
Hello, Ada Lovelace!
HELLO, GRACE HOPPER!
```

`from example_package.greetings import hello` names the full dotted path.
`example_package/__init__.py` also re-exports `hello` and `shout_hello`
with `from .greetings import hello, shout_hello`, so `from example_package
import shout_hello` reaches the same function without naming the internal
`greetings` module. Prefer a package's re-exported form when one is
documented.

### Relative imports only resolve inside a package

Inside `example_package/greetings.py`:

```python
from ._formatting import _shout, _titlecase
```

The leading dot means "look inside this package," not "search `sys.path`
for a top-level module named `_formatting`." Relative imports are valid
**only** in a module Python loaded as part of a package -- through
`import` or `python -m`, both of which set that module's `__package__`.
Running a file directly by its bare path (`python path/to/module.py`) sets
`__package__` to `None`, and any relative import inside that file then
raises `ImportError: attempted relative import with no known parent
package`. That constraint is exactly why package-internal modules are
launched with `python -m package.module`.

### Running a package with `python -m`

`example_package/__main__.py` defines a guarded block that a package
runner can execute:

```python
from example_package import hello

if __name__ == "__main__":
    print(hello("package runner"))
```

Run it rooted at this lesson's directory:

```bash
(cd lessons/06_modules_and_packages && python -m example_package)
```

```text
Hello, Package Runner!
```

`python -m example_package` imports the package (running `__init__.py`)
and then runs `__main__.py` as `__main__`, resolving its own absolute
import of `example_package` correctly. Running
`python lessons/06_modules_and_packages/example_package/__main__.py`
directly would instead raise an import error, because that file's own
`from example_package import hello` needs `example_package`'s *parent*
directory on `sys.path` -- something `-m` arranges from the current
working directory, but a bare file path does not.

Run the complete companion:

```bash
python lessons/06_modules_and_packages/02_packages_and_resolution.py
```

See [`02_packages_and_resolution.py`](02_packages_and_resolution.py) and
[`example_package/`](example_package/) for the full package layout.

> **Try one change:** run
> `python lessons/06_modules_and_packages/example_package/__main__.py`
> instead of the `python -m` command above and read the traceback. Confirm
> it names the same absolute-import boundary this section describes.

## 3️⃣ Scripts vs. modules, guarded entry points, and public APIs

Every module has a `__name__`. When Python runs a file directly, as the
program's entry point, that file's `__name__` is the string `"__main__"`.
When the same file is instead imported, its `__name__` is its module name.
The code runs identically either way -- only that one name differs.

### Import-time side effects run once, in file order

`greeting_module.py`, a sibling of this lesson, prints at its top level:

```python
print("greeting_module: top-level code is executing (import-time side effect)")


def get_greeting(name: str) -> str:
    return f"Greetings, {name}!"
```

Importing it the first time runs that print immediately:

```python
import greeting_module
```

```text
greeting_module: top-level code is executing (import-time side effect)
```

A second `import greeting_module` elsewhere in the same process reuses the
cached module object from Section 1 and prints nothing further -- only
`get_greeting("Ada")` (a plain call) produces new output afterward.

### A guarded entry point runs only on direct execution

`greeting_module.py` also ends with:

```python
if __name__ == "__main__":
    print("greeting_module: running as a script ->", get_greeting("Direct Run"))
```

Reached through `import greeting_module` above, this block does **not**
run, because `greeting_module.__name__` is `"greeting_module"`, not
`"__main__"`. Running the same file directly gives it `__name__ ==
"__main__"` instead:

```bash
python lessons/06_modules_and_packages/greeting_module.py
```

```text
greeting_module: top-level code is executing (import-time side effect)
greeting_module: running as a script -> Greetings, Direct Run!
```

Both lines print this time: the unconditional top-level print runs first
(as it always does), and the guarded block now also runs.

### Re-exports and `__all__` document a small public API

`facade.py`, another sibling, re-exports one function and declares its
intended public surface:

```python
from greeting_module import get_greeting

__all__ = ["get_greeting"]
```

```python
import facade
from facade import get_greeting

print(get_greeting("Grace"))
print(facade.__all__)
```

```text
Greetings, Grace!
['get_greeting']
```

A caller depending on `facade` sees one small, named surface without
knowing which module originally defined `get_greeting` -- the same idea as
`example_package/__init__.py` re-exporting `hello` in Section 2, applied to
a single sibling module. `__all__` only changes what `from facade import
*` would expose; it does not block `from facade import get_greeting` or
`greeting_module.get_greeting` directly.

Run the complete companion:

```bash
python lessons/06_modules_and_packages/03_scripts_modules_and_public_apis.py
```

See
[`03_scripts_modules_and_public_apis.py`](03_scripts_modules_and_public_apis.py),
[`greeting_module.py`](greeting_module.py), and [`facade.py`](facade.py)
for the full sequence.

> **Try one change:** add a second function to `greeting_module.py` (for
> example `def internal_helper(): ...`) without adding it to `facade.py`'s
> `__all__` or re-exporting it. Predict whether `from facade import *`
> can reach it, and whether `greeting_module.internal_helper()` still can.

## 🔁 Transition to Chapter 7

This chapter packaged code across files and gave it an import boundary.
Chapter 7, Exceptions, Files, and Paths, uses that same file-crossing
mindset for a different resource: things outside the Python process
entirely -- paths, files, and the operating system -- and the exception
flow needed to handle when those interactions fail.

## ⚠️ Common mistakes

- Expecting a second `import` of the same module to re-run its top-level
  code; it reuses the cached object instead.
- Using a relative import (`from .sibling import x`) in a file run directly
  by its path, which raises `ImportError: attempted relative import with no
  known parent package`.
- Running a package-internal module as `python path/to/module.py` instead
  of `python -m package.module`, then being surprised when its relative
  imports fail.
- Assuming `__all__` restricts what can be imported; it only changes what
  `from module import *` exposes.
- Assuming a leading underscore (`_formatting`) enforces privacy; it is a
  convention, and the name remains importable explicitly.

## 🧾 Summary

- A module is an ordinary object, cached in `sys.modules` after its first
  import so top-level code runs exactly once per process.
- Four import forms control whether a name is namespaced, renamed, or
  imported directly.
- A package is a directory with `__init__.py`; absolute imports name a full
  path, relative imports mean "this package," and `python -m` is the normal
  way to run a package-internal module correctly.
- `__name__ == "__main__"` distinguishes "run directly" from "imported,"
  which is how one file can be both a library and a script.
- Re-exports and `__all__` document a small public surface without making
  anything else inaccessible.

## ❓ Review questions (closed notes)

1. What object does `import math` bind `math` to, and where is it cached?
2. Name the four import forms and how each changes the local namespace.
3. Why does a relative import fail in a file run directly by its path?
4. What does `python -m package.module` do differently from
   `python path/to/package/module.py`?
5. When is a module's `__name__` equal to `"__main__"`?
6. Does `__all__` prevent a name from being imported? What does it actually
   control?

## 📚 Authoritative references

- [The import system](https://docs.python.org/3/reference/import.html)
- [Modules](https://docs.python.org/3/tutorial/modules.html)
- [Packages](https://docs.python.org/3/tutorial/modules.html#packages)
- [`sys.modules`](https://docs.python.org/3/library/sys.html#sys.modules)
- [`__main__` -- Top-level script environment](https://docs.python.org/3/library/__main__.html)
- [`python -m`](https://docs.python.org/3/using/cmdline.html#cmdoption-m)

Once you can answer the review questions and have run all three lesson
files, continue to
[`exercises/06_modules_and_packages/`](../../exercises/06_modules_and_packages/README.md).
