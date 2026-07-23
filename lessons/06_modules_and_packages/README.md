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

## 🧩 Progressive syntax and mechanism

1. **Modules are objects.** `import math` binds the name `math` to a module
   object; `type(math)` is `<class 'module'>`, and `math.sqrt` is looked up
   as an attribute like any other.
2. **The import cache.** The first `import` of a given module name runs its
   top-level code and stores the result in `sys.modules`; every later
   import of that name in the same process reuses the cached object.
3. **Import forms.** `import x` (namespaced), `import x as y` (renamed),
   `from x import y` (direct name), `from x import y as z` (renamed
   direct) -- namespacing avoids collisions; direct imports drop the
   prefix and can be shadowed by a later same-named definition.
4. **Package layout.** A directory becomes a package when it contains
   `__init__.py` (even empty); the file runs once, on first import, and can
   re-export names so callers reach `package.name` instead of
   `package.module.name`.
5. **Absolute versus relative imports.** An absolute import names a full
   dotted path from a location Python already searches; a relative import
   (`from .sibling import thing`) means "inside this package" and only
   works in a module loaded as part of a package -- never in a file run
   directly by its path.
6. **`python -m package.module`.** Runs a module as part of its package,
   setting up relative imports correctly; this differs from
   `python path/to/module.py`, which sets `__package__` to `None` and
   breaks any relative import inside that file.
7. **`__name__` and guarded entry points.** A module's `__name__` is
   `"__main__"` only when Python ran it directly; `if __name__ ==
   "__main__":` lets one file work both as an importable library and a
   runnable script.
8. **Re-exports and `__all__`.** A module or package can re-export a name
   defined elsewhere so callers depend on one stable path; `__all__`
   documents (and controls only for `import *`) the intended public names.

## 📖 Read-predict-run-modify workflow

Work through the three lesson files in order, predicting each output
before running:

```bash
python lessons/06_modules_and_packages/01_modules_and_imports.py
python lessons/06_modules_and_packages/02_packages_and_resolution.py
(cd lessons/06_modules_and_packages && python -m example_package)
python lessons/06_modules_and_packages/03_scripts_modules_and_public_apis.py
python lessons/06_modules_and_packages/greeting_module.py
```

### Expected output highlights

- `01_modules_and_imports.py`: `sys.modules["math"] is math` is `True` --
  the second lookup reuses the same cached object rather than re-importing.
- After `02_packages_and_resolution.py`, the explicit
  `python -m example_package` command prints `Hello, Package Runner!`.
- `03_scripts_modules_and_public_apis.py`: importing `greeting_module`
  prints its top-level side-effect line exactly once, even though the file
  is imported twice; the following direct-run command additionally prints
  its guarded `__main__` block's output.

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
