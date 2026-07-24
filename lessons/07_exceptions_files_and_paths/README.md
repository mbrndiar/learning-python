# 🧯 Chapter 7: Exceptions, Files, and Paths

**Semantic ID:** `module.exceptions-files-and-paths` · **Prerequisites:**
`module.modules-and-packages`

## 📍 Where this fits

Chapter 6 organized code across files and packages, but every example so
far assumed things went right. Real programs read files that might not
exist, parse text that might be malformed, and depend on resources that
must be released whether or not something fails along the way. This
chapter introduces exception flow first -- how an error propagates and how
to handle it deliberately -- then uses that flow immediately to work safely
with paths, text files, and binary files, and to understand the bounded
guarantee `with` provides.

## 🎯 Learning objectives

After this chapter, you should be able to:

- trace how a raised exception propagates through nested function calls
  until a matching `except` catches it, using its recorded traceback;
- write a narrow `except` clause (or a tuple of types) instead of a bare
  `except:`, and explain what a bare `except` risks hiding;
- use a `try`/`except`/`else`/`finally` statement and explain what each
  clause guarantees;
- re-raise the current exception with a bare `raise`, and translate one
  exception into another with `raise NewError(...) from original`;
- build and inspect `pathlib.Path` values, iterate a directory with
  `iterdir()`/`glob()`/`rglob()`, and read file metadata;
- open files in text and binary modes, explain what an explicit encoding
  and the `newline` parameter each control, and close a file by hand with
  `try`/`finally` before relying on `with`;
- implement `__enter__`/`__exit__` on a class so it works with `with`, and
  explain the resource-lifetime guarantee `with` provides;
- adapt a `.close()`-only object with `contextlib.closing`, and explain why
  an active `memoryview` prevents its exporting buffer from being resized.

## 🧠 Motivation and mental model

An exception is not a special kind of crash -- it is Python's ordinary way
of saying "this call could not produce the value or effect you asked for,"
and the language gives you tools to say precisely which failures you
expected and what should happen next. Files and paths are the first place
in this course where failure is routine rather than exceptional: a path
might not exist, a permission might be missing, a byte sequence might not
decode. Learning exception flow first, before touching the filesystem,
means every file operation in this chapter can be explained in terms of a
mechanism you already understand, instead of introducing `try`/`except`
as an afterthought bolted onto file-handling examples.

## 1️⃣ Traceback propagation, narrow except, else, finally, and chaining

Raising an exception immediately stops normal execution and unwinds the
call stack, one frame at a time, until a matching `except` is found:

```python
import traceback


def inner():
    raise ValueError("something inner went wrong")


def middle():
    inner()  # no try here -- ValueError simply keeps propagating outward


def outer():
    try:
        middle()
    except ValueError as error:
        frames = traceback.extract_tb(error.__traceback__)
        print("Frames the exception passed through:", [frame.name for frame in frames])


outer()
```

```text
Frames the exception passed through: ['outer', 'middle', 'inner']
```

`error.__traceback__` records every frame the exception passed through on
its way up -- `middle` and `inner` both appear, even though `outer` is the
only place with a `try`/`except`.

### A narrow `except` names exactly what it can recover from

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


print(safe_divide(10, 2))
print(safe_divide(10, 0))
```

```text
5.0
None
```

This handler recovers from exactly `ZeroDivisionError`. Any other
exception -- a `TypeError` from a non-numeric argument, say -- still
propagates normally. A bare `except:` (or `except Exception:`) would also
swallow those unrelated bugs, letting them fail silently instead of
surfacing as real defects.

### `else` runs only on success; `finally` always runs

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("division by zero")
else:
    print(f"= {result}")
finally:
    print("(checked)")
```

```text
= 5.0
(checked)
```

`else` runs only if the `try` block raised nothing -- code that should run
on success, but that should not itself be caught by the `except` clauses,
belongs here. `finally` runs unconditionally, after whichever branch ran,
for cleanup that must always happen (even if a `return` occurs inside the
`try` or `except` block).

### Bare `raise` re-raises; `raise ... from ...` chains

```python
def parse_amount(text):
    try:
        return int(text)
    except ValueError as error:
        raise ValueError(f"amount must be a whole number: {text!r}") from error


try:
    parse_amount("many")
except ValueError as error:
    print("Translated error:", error)
    print("original cause:", type(error.__cause__).__name__, "-", error.__cause__)
```

```text
Translated error: amount must be a whole number: 'many'
original cause: ValueError - invalid literal for int() with base 10: 'many'
```

A bare `raise` inside an `except` block (used for logging or partial
cleanup) re-raises the exception being handled, unchanged, with its
original traceback intact. `raise NewError(...) from original` instead
attaches `original` as `__cause__`, so readers see both the translated
error raised on purpose and the low-level error that triggered it.

Run the complete companion:

```bash
python lessons/07_exceptions_files_and_paths/01_exception_flow.py
```

See [`01_exception_flow.py`](01_exception_flow.py) for the full sequence,
including multiple `except` clauses handling distinct failures distinctly.

> **Try one change:** in `parse_amount`, change `raise ValueError(...) from
> error` to plain `raise ValueError(...)` (no `from`). Predict what
> `error.__cause__` becomes; Python still records the earlier exception as
> `__context__` automatically, but only `from` promotes it to an explicit
> `__cause__`.

## 2️⃣ `Path`, relative and absolute paths, iteration, and metadata

`pathlib.Path` represents a filesystem location as a value. Building one
does not touch the filesystem or change the process's working directory:

```python
from pathlib import Path

relative_path = Path("project") / "data" / "report.txt"
print(relative_path.as_posix())
print(relative_path.is_absolute())
```

```text
project/data/report.txt
False
```

`/` between `Path` segments joins them, unrelated to numeric division. A
relative path used for I/O resolves against `Path.cwd()` (wherever the
caller started Python) unless anchored to `__file__` (this script's own
location) instead -- `Path.cwd() / relative_path` and
`Path(__file__).resolve().parent / relative_path` are both absolute, but
for different reasons.

### Metadata: `exists`, `is_dir`, `is_file`, `stat`

```python
draft = data / "draft.txt"
draft.write_text("alpha\n", encoding="utf-8")

print(draft.is_file())
print(draft.stat().st_size)
```

```text
True
6
```

`stat()` exposes details such as `st_size` (byte count) and timestamps.
A missing path raises `FileNotFoundError` from `.stat()`, the same
exception vocabulary Section 1 covered -- `Path` never silently returns a
placeholder for something that is not there.

### Iteration: `iterdir`, `glob`, `rglob`

```python
children = sorted(path.name for path in project.iterdir())
direct_text = sorted(path.name for path in data.glob("*.txt"))
```

```text
['data', 'notes.md']
['draft.txt']
```

`iterdir()` lists immediate children only; `glob()` matches a pattern in
one directory; `rglob()` matches the same pattern recursively. Filesystems
make no ordering promise, so this lesson sorts wherever output or
comparisons need a deterministic order.

### Everything here runs inside a cleaned-up temporary directory

```python
import tempfile

temporary = tempfile.TemporaryDirectory(prefix="paths_lesson_")
try:
    root = Path(temporary.name)
    ...
finally:
    temporary.cleanup()

print("Temporary tree removed:", not root.exists())
```

```text
Temporary tree removed: True
```

`cleanup()` removes the directory and everything inside it; the `finally`
clause (Section 1) guarantees that cleanup runs even if an earlier step in
the `try` block had failed.

Run the complete companion:

```bash
python lessons/07_exceptions_files_and_paths/02_paths_and_directories.py
```

See
[`02_paths_and_directories.py`](02_paths_and_directories.py) for the full
sequence, including the missing-path `FileNotFoundError` check.

> **Try one change:** change `data.glob("*.txt")` to `data.glob("*.csv")`
> and predict the new sorted list. `glob()` only matches the given
> directory; `rglob()` would also find a same-named file nested deeper.

## 3️⃣ Open modes, encodings, newline behavior, and bytes

`open()` returns a file object that must be closed to release the
underlying OS resource and guarantee buffered writes reach disk. Before
`with` (Section 4), that is the caller's job:

```python
file = open(manual_path, "w", encoding="utf-8")
try:
    file.write("Opened and closed by hand.\n")
finally:
    file.close()
print("File closed manually:", file.closed)
```

```text
File closed manually: True
```

This explicit `try`/`finally` is the same pattern Section 1 used for
`finally` -- `with` in Section 4 is a convenience over it, not unrelated
magic. `"w"` creates or truncates a file; `"a"` appends; `"r"` (the
default) reads.

### Newline translation applies to text mode only

```python
mixed_path.write_bytes(b"first\r\nsecond\nthird\r")

handle = open(mixed_path, encoding="utf-8")
translated = handle.read()
handle.close()

handle = open(mixed_path, encoding="utf-8", newline="")
untranslated = handle.read()
handle.close()

print(translated.splitlines())
print(repr(untranslated))
```

```text
['first', 'second', 'third']
'first\r\nsecond\nthird\r'
```

Text mode translates `"\r\n"`, `"\n"`, and `"\r"` to `"\n"` on read by
default. `newline=""` disables that translation, so `read()` preserves the
exact line-ending sequences found on disk -- it still decodes bytes to
`str` using the given encoding; only the newline handling changes.

### Binary mode transfers bytes unchanged

```python
binary_payload = b"\x00Python\xff"
handle = open(binary_path, "wb")
handle.write(binary_payload)
handle.close()

handle = open(binary_path, "rb")
binary_contents = handle.read()
handle.close()

print(binary_contents)
assert binary_contents == binary_payload
```

```text
b'\x00Python\xff'
```

No `encoding` parameter exists for `"wb"`/`"rb"`, because there is no text
to decode -- bytes go in and the identical bytes come back out.

Run the complete companion:

```bash
python lessons/07_exceptions_files_and_paths/03_text_and_binary_files.py
```

See [`03_text_and_binary_files.py`](03_text_and_binary_files.py) for the
full sequence, including writing, appending, and rereading a text file.

> **Try one change:** remove `newline=""` from the `untranslated` read
> above and predict how `repr(untranslated)` changes. The file on disk
> does not change; only what `read()` hands back changes.

## 4️⃣ `with`, `__enter__`/`__exit__`, `closing`, and memoryview lifetime

`with` replaces the manual `try`/`finally` from Section 3 with one
guarantee: the object following `with` has its cleanup method called when
the block ends, whether it ended normally or by raising.

```python
with open(sample_path, "w", encoding="utf-8") as handle:
    handle.write("first line\n")
print("File closed after the with block:", handle.closed)
```

```text
File closed after the with block: True
```

### A class becomes usable with `with` via `__enter__`/`__exit__`

Chapter 9 teaches classes, `self`, and `__init__` in depth. Here they are a
bounded preview used only to hand-write the two methods required by the `with`
protocol.

```python
class ManagedFile:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.path, self.mode, encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()
        return False
```

`__enter__` runs at the start of the block and returns the value bound by
`as`; `__exit__` runs at the end -- on success and on failure alike.
Returning a truthy value from `__exit__` would suppress an active
exception; returning `False` (or `None`) preserves it after cleanup runs.

### `__exit__` runs even when the block raises

```python
try:
    with ManagedFile(sample_path, "a") as handle:
        handle.write("third line\n")
        raise RuntimeError("simulated failure inside the block")
except RuntimeError as error:
    print("Caught after cleanup already ran:", error)
print("ManagedFile closed even after an error:", handle.closed)
```

```text
Caught after cleanup already ran: simulated failure inside the block
ManagedFile closed even after an error: True
```

`handle.closed` is `True` even though the `with` block raised on purpose:
`__exit__` ran and closed the file before the exception reached the
`except` clause outside it.

### `contextlib.closing` adapts a `.close()`-only object

```python
from contextlib import closing

legacy = LegacyResource()  # only defines .close(), no __enter__/__exit__
with closing(legacy):
    print("closed inside the block?", legacy.closed)
print("closed after the block:", legacy.closed)
```

```text
closed inside the block? False
closed after the block: True
```

`closing()` guarantees `close()` runs at the end of the block for any
object that offers `.close()` but does not implement the context manager
protocol itself.

### An active `memoryview` blocks resizing its exporter

```python
payload = bytearray(b"binary-data")
view = memoryview(payload)
try:
    payload.extend(b"!")
except BufferError:
    print("Resize blocked while memoryview is active")

view.release()
payload.extend(b"!")
```

```text
Resize blocked while memoryview is active
```

A `memoryview` exposes another object's buffer without copying it, keeping
that exporter alive; resizing the buffer while a view is active raises
`BufferError`. Releasing the view ends the exported reference and permits
resizing again.

Run the complete companion:

```bash
python lessons/07_exceptions_files_and_paths/04_context_managers_and_resource_lifetimes.py
```

See
[`04_context_managers_and_resource_lifetimes.py`](04_context_managers_and_resource_lifetimes.py)
for the full sequence.

> **Try one change:** in the `ManagedFile` example, remove the
> `raise RuntimeError(...)` line and predict whether `handle.closed` still
> prints `True`. `__exit__` runs at the end of every `with` block, not only
> when an exception occurs.

## 🔁 Transition to Chapter 8

This chapter validated failure at the boundary between Python and the
filesystem. Chapter 8, Structured Data and Time, validates a different
boundary -- between Python values and the JSON text (or timestamp text)
exchanged with other systems -- using the same exception-handling and
file-reading tools this chapter just taught.

## ⚠️ Common mistakes

- Using a bare `except:` (or `except Exception:`) that also hides
  programming errors unrelated to the failure being handled.
- Forgetting that `finally` runs even when a `return` happens inside the
  `try` or `except` block.
- Assuming `newline=""` changes what is written to disk; it only changes
  whether `read()` translates line endings it finds there.
- Opening a binary file with `"r"`/`"w"` instead of `"rb"`/`"wb"`, which
  raises when the content is not valid text in the assumed encoding.
- Returning a truthy value from `__exit__`, which silently suppresses the
  exception that was propagating through the `with` block.
- Forgetting to release a `memoryview` before resizing its exporting buffer,
  which raises `BufferError`.

## 🧾 Summary

- Exceptions propagate until a narrow `except` catches them; `else` and
  `finally` express "only on success" and "always" respectively.
- A bare `raise` re-raises unchanged; `raise ... from ...` documents an
  intentional translation and keeps the original error visible.
- `pathlib.Path` models a location; metadata and iteration methods raise
  ordinary exceptions (like `FileNotFoundError`) rather than hiding
  failure.
- Text mode needs an explicit encoding and applies newline translation
  unless disabled; binary mode transfers bytes unchanged.
- `with` guarantees `__exit__`/`close()` runs whether the block succeeded
  or raised; `closing()` extends that guarantee to `.close()`-only objects.

## ❓ Review questions (closed notes)

1. What does an exception's `__traceback__` record, and how is that
   different from where it was ultimately caught?
2. Why is a bare `except:` usually the wrong choice?
3. What is the difference between what `else` and `finally` guarantee?
4. What does `raise ... from ...` attach to the new exception, and how does
   that differ from a bare `raise`?
5. Why does an explicit `encoding` matter even though `open()` runs
   without one?
6. What guarantee does `with` provide that manual `try`/`finally` also
   provides, and what does it save you from writing?

## 📚 Authoritative references

- [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [`try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
- [`pathlib` -- Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
- [`open()`](https://docs.python.org/3/library/functions.html#open)
- [`with` statement context managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
- [`contextlib.closing`](https://docs.python.org/3/library/contextlib.html#contextlib.closing)
- [`memoryview`](https://docs.python.org/3/library/stdtypes.html#memoryview)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/07_exceptions_files_and_paths/`](../../exercises/07_exceptions_files_and_paths/README.md).
