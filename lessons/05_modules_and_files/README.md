# 📦 Module 5: Modules and Files

Organizing code across files, using the standard library, and handling
files and errors robustly.

## 🎯 Learning objectives

After this module, you should be able to import code without accidental side
effects, organize modules, work safely with paths and files, exchange structured
JSON data, handle expected errors, and implement deterministic cleanup.

## 🧩 Modules, packages, and imports

A module is normally one `.py` file. A package groups importable modules in a
directory; modern namespace packages do not always require `__init__.py`,
although regular packages commonly include it. Importing executes a module's
top-level code once per process and caches the resulting module object.

```python
import math
from pathlib import Path

print(math.sqrt(25))
```

Prefer explicit imports and avoid `from module import *`. Place demonstrations
behind `if __name__ == "__main__":` so importing the module does not run them.
Python searches locations in `sys.path`; run commands from the documented
project directory rather than modifying the path inside source code.

When a package import works from one directory but fails from another, first
check how the program was launched. From the repository root,
`python -m project.task_manager.cli` asks Python to resolve a package module;
running a deeply nested file path directly can give it a different import
context.

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
- **`02_files_and_exceptions.py`** - reading from and writing to files
  with `open()` and the `with` statement, and handling errors gracefully
  with `try`/`except`.
- **`03_custom_exceptions_and_context_managers.py`** - defining your own
  exception classes (subclassing `Exception`) and writing your own
  context managers (the objects that power the `with` statement), using
  both classes and `contextlib.contextmanager`.
- **`04_json_and_structured_data.py`** - serializing dictionaries and lists,
  writing readable JSON files, and validating decoded top-level structures.

## ▶️ Running

```bash
python lessons/05_modules_and_files/01_modules.py
python lessons/05_modules_and_files/02_files_and_exceptions.py
python lessons/05_modules_and_files/03_custom_exceptions_and_context_managers.py
python lessons/05_modules_and_files/04_json_and_structured_data.py
```

Once you've read through all four files, practice what you learned in
[`exercises/05_modules_and_files/`](../../exercises/05_modules_and_files/README.md).

## ⚠️ Common mistakes

- Running substantial work at import time.
- Assuming the current working directory is the source file's directory.
- Omitting an encoding for persistent text.
- Catching `Exception` and silently continuing.
- Opening a resource without ensuring it will be closed.

## ❓ Review questions

1. Why protect demonstration code with a `__main__` check?
2. How do text and binary file modes differ?
3. When do `else` and `finally` execute in a `try` statement?
4. Why should exception handlers be narrow?
5. What protocol makes an object usable in a `with` statement?
6. Why must decoded JSON still be validated?
