# 📦 Module 5: Modules and Files

Organizing code across files, using the standard library, and handling paths,
files, structured data, time, and errors robustly.

## 🎯 Learning objectives

After this module, you should be able to import code without accidental side
effects, distinguish import packages from installable distributions, work safely
with paths, directories, and files, represent real instants deliberately,
exchange structured JSON data, handle expected errors, and implement
deterministic cleanup.

## 🧩 Modules, packages, and imports

A **module** is a single `.py` file.  A **package** is a directory that groups
related modules; it is traditionally marked by an `__init__.py` file (regular
package).  Modern Python also supports namespace packages without one, but for
learning purposes treat every package as a folder that contains `__init__.py`.

```
example_package/          ← package (directory)
    __init__.py           ← marks the directory as a package; can re-export names
    greetings.py          ← public module
    _formatting.py        ← internal module (leading underscore = not public API)
```

Importing executes a module's top-level code exactly once per process.
Subsequent imports return the cached object from `sys.modules` without
re-running the file.

```python
import math
from pathlib import Path

print(math.sqrt(25))
```

### Absolute vs. relative imports

An **absolute import** names the full path from a root on `sys.path`:

```python
from myapp.greetings import hello          # full dotted path
from myapp import hello                    # via __init__.py re-export
```

A **relative import** uses a leading dot to mean "this package":

```python
# inside myapp/greetings.py
from ._formatting import _shout            # sibling module in myapp/
from .utils.text import truncate           # sub-package sibling
```

The dot is essential.  Without it:

```python
from _formatting import _shout             # searches sys.path, not the package
```

Python looks for a top-level module named `_formatting` instead of the sibling
file, which will either import the wrong thing or raise `ImportError`.

Relative imports work **only** when a file is loaded as part of a package—via
`import` or `python -m`.  Running a package module directly with
`python path/to/package/module.py` sets `__package__` to `None`, which breaks
relative imports.  That is why package-internal modules are run from the
repository root as:

```bash
python -m myapp.module
```

### Package-level re-exports

`__init__.py` can import names from its own modules so callers get a shorter
import path:

```python
# myapp/__init__.py
from .greetings import hello, shout_hello

__all__ = ["hello", "shout_hello"]
```

Callers can then write `from myapp import hello` instead of
`from myapp.greetings import hello`.

### Public/internal naming and `__all__`

Names beginning with `_` (e.g. `_helper`, `_formatting`) signal "internal—not
part of the public API" by convention.  Python does not enforce this; they can
still be imported explicitly.  It is a signal to readers and tools.

`__all__` lists the names that `from module import *` exposes.  It is
**not** access control—names outside `__all__` are still importable explicitly.
Its main purpose is to document the public surface and keep wildcard imports
predictable.  Wildcard imports (`from module import *`) are still discouraged
even when `__all__` is present because they obscure where names come from.

Prefer explicit imports and avoid `from module import *`. Place demonstrations
behind `if __name__ == "__main__":` so importing the module does not run them.
Python searches locations in `sys.path`; run commands from the documented
project directory rather than modifying the path inside source code.

An **import package** is a namespace used by `import`. A **distribution package**
is an installable project described by metadata and may contain one or more
import packages. Module 9 builds an example distribution and explains
`pyproject.toml`, editable installation, wheels, and source distributions.

When a package import works from one directory but fails from another, first
check how the program was launched. From the repository root,
`PYTHONPATH=capstones/comparative/solution python -m comparative_kv --help`
asks Python to resolve a package module; running a deeply nested file path
directly can give it a different import context.

## 📁 Paths, files, and encodings

`pathlib.Path` provides cross-platform path operations:

```python
from pathlib import Path

path = Path("notes.txt")
path.write_text("Hello\n", encoding="utf-8")
text = path.read_text(encoding="utf-8")
```

For larger files, use `with path.open(...) as file` and iterate line by line.
Text mode decodes bytes into strings; binary mode (`"rb"`/`"wb"`) leaves bytes
unchanged. State an encoding for persistent text. File modes include read
`"r"`, overwrite `"w"`, append `"a"`, and exclusive create `"x"`.

`Path.mkdir(parents=True)` creates a directory tree. `iterdir()` visits direct
children, while `glob()` and `rglob()` match patterns. Filesystems do not promise
the order needed by most user-facing contracts, so explicitly sort paths when
stable output matters. Check `is_file()` or `is_dir()` when the distinction is
part of the contract, and use `stat()` for metadata.

Derive a path from `__file__` when a resource belongs beside the source module;
use a relative path when the current working directory is intentionally part of
the command contract. `resolve()` can produce an absolute path and follow
symlinks, but a resolved prefix comparison is not by itself a complete security
or authorization boundary.

Use `Path.rename()` or `Path.replace()` for filesystem renaming semantics and
`shutil.copy2()` or `shutil.move()` when copy/move behavior is intended.
Temporary examples should work inside `TemporaryDirectory` so cleanup is
deterministic and does not touch a learner's real files.

References: [`pathlib`](https://docs.python.org/3/library/pathlib.html),
[`shutil`](https://docs.python.org/3/library/shutil.html), and
[`tempfile`](https://docs.python.org/3/library/tempfile.html).

## 🕐 Dates, times, and clocks

`date` represents a calendar date, `time` a time of day, `datetime` their
combination, and `timedelta` a duration. A naive `datetime` has no time-zone
information and cannot identify a real instant without an external convention.
An aware value includes an offset or zone:

```python
from datetime import datetime, timezone

instant = datetime.fromisoformat("2026-07-17T21:00:00+00:00")
utc_instant = instant.astimezone(timezone.utc)
```

Use `zoneinfo.ZoneInfo` for named IANA zones when civil-time rules matter. Those
rules can change offsets at daylight-saving transitions, so adding a fixed
duration and asking for the same local wall time are different operations.

ISO 8601 is a family of representations; APIs should state the accepted shape
and timezone requirement rather than saying only "ISO date." Unix timestamps
are numeric offsets from the epoch, conventionally seconds in Python—always
state the unit and convert with an explicit timezone. Use `time.monotonic()` for
elapsed durations because the wall clock can be corrected while a program runs.

`zoneinfo` uses the system IANA time-zone database when available and can use
the first-party `tzdata` package otherwise. Code that requires a named zone
should surface `ZoneInfoNotFoundError` with actionable configuration guidance
rather than silently substituting a fixed offset.

References: [`datetime`](https://docs.python.org/3/library/datetime.html),
[`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html), and
[`time`](https://docs.python.org/3/library/time.html).

## 🚨 Exceptions

Exceptions separate normal results from failure. Catch the narrowest exception
you can handle, and keep the protected `try` block small:

```python
try:
    count = int(raw_count)
except ValueError as error:
    raise ValueError("count must be a whole number") from error
else:
    print(f"Accepted {count}")
finally:
    print("cleanup that must always happen")
```

`else` runs only if no exception occurs; `finally` runs whether the operation
succeeds, fails, or returns. Do not use bare `except:` to hide programmer
errors or interrupts. Custom exceptions should describe domain failures and
usually inherit from `Exception` or a suitable existing subclass.

`raise NewError(...) from error` preserves the original failure as the cause.
Use it when translating a low-level exception into language meaningful to the
caller without losing the evidence needed for debugging.

A context manager's `__enter__` and `__exit__` methods define setup and
cleanup. `with` is preferable to manual `try/finally` for files, locks,
database transactions, and other managed resources. Returning a truthy value
from `__exit__` suppresses the active exception; returning falsey lets it
propagate. Suppression should therefore be deliberate and rare.

## 🧾 JSON

JSON represents dictionaries, lists, strings, numbers, booleans and `null` as
portable text. `json.dumps()`/`json.loads()` work with strings, while
`json.dump()`/`json.load()` work with file objects. Decoding only proves that
the JSON syntax is valid. Checking that the top level is a list is only the first
step: applications must also validate required fields and their types before
treating transport data as domain data.

## 📚 Concepts covered

- **`01_modules.py`** - importing standard-library modules (`math`,
  `random`, `datetime`) and organizing your own code into modules.
- **`02_packages.py`** – module vs. package, absolute and relative imports,
  package-level re-exports via `__init__.py`, the `_name` convention,
  `__all__`, import caching, and why package modules are run with
  `python -m package.module`.
  Uses `example_package/` (next to this file) as a concrete, runnable example.
- **`03_files_and_exceptions.py`** - reading from and writing to files
  with `open()` and the `with` statement, and handling errors gracefully
  with `try`/`except`.
- **`04_custom_exceptions_and_context_managers.py`** - defining your own
  exception classes (subclassing `Exception`) and writing your own
  context managers (the objects that power the `with` statement), using
  both classes and `contextlib.contextmanager`.
- **`05_json_and_structured_data.py`** - serializing dictionaries and lists,
  writing readable JSON files, and validating decoded top-level structures.
- **`06_directories_and_paths.py`** - current-working-directory versus
  source-relative paths, directory creation and traversal, deterministic
  globbing, file metadata, rename/replace/copy/move operations, cleanup, and
  path-security boundaries.
- **`07_dates_and_times.py`** - dates, times, datetimes, timedeltas, naive versus
  aware values, UTC and IANA zones, ISO 8601/RFC 3339, Unix timestamps, DST,
  and monotonic duration measurement.

## ▶️ Running

```bash
python lessons/05_modules_and_files/01_modules.py
python lessons/05_modules_and_files/02_packages.py
python lessons/05_modules_and_files/03_files_and_exceptions.py
python lessons/05_modules_and_files/04_custom_exceptions_and_context_managers.py
python lessons/05_modules_and_files/05_json_and_structured_data.py
python lessons/05_modules_and_files/06_directories_and_paths.py
python lessons/05_modules_and_files/07_dates_and_times.py
```

Once you've read through all seven files, practice what you learned in
[`exercises/05_modules_and_files/`](../../exercises/05_modules_and_files/README.md).

## ⚠️ Common mistakes

- Running substantial work at import time.
- Assuming the current working directory is the source file's directory.
- Depending on filesystem iteration order without sorting.
- Treating `resolve()` as proof that an untrusted path is authorized.
- Omitting an encoding for persistent text.
- Mixing naive and aware datetimes or omitting timestamp units.
- Measuring elapsed duration with an adjustable wall clock.
- Catching `Exception` and silently continuing.
- Opening a resource without ensuring it will be closed.

## ❓ Review questions

1. Why protect demonstration code with a `__main__` check?
2. What is the difference between an import package and a distribution package?
3. How do text and binary file modes differ?
4. Why should directory results be sorted when order is part of the output?
5. Why is resolving a path not the same as authorizing it?
6. How do naive and aware datetimes differ?
7. Why must a timestamp contract state its unit?
8. When should elapsed time use a monotonic clock?
9. When do `else` and `finally` execute in a `try` statement?
10. Why should exception handlers be narrow?
11. What protocol makes an object usable in a `with` statement?
12. Why must decoded JSON still be validated?
13. What is the difference between a module and a package?
14. Why does `from .api import X` behave differently from `from api import X`?
15. Why are package modules run with `python -m package.module` rather than
   directly as `python path/to/module.py`?
16. What does `__all__` control, and is it a form of access control?
