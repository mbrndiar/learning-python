# 🧯 Exercises: Chapter 7 - Exceptions, Files, and Paths

**Prerequisites:** completed
[`lessons/07_exceptions_files_and_paths/`](../../lessons/07_exceptions_files_and_paths/README.md).

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/07_exceptions_files_and_paths/exercises.py

# Compile-check without running:
python -m py_compile exercises/07_exceptions_files_and_paths/exercises.py

# Check the reference solution:
python exercises/07_exceptions_files_and_paths/solutions.py
```

## Tasks

1. **`safe_divide(a, b)`** - divide two numbers, catching
   `ZeroDivisionError` instead of checking `b == 0` directly.
2. **`write_lines(path, lines)`** / **`read_lines(path)`** - write a list
   of strings to a text file and read them back, one per line.
3. **`write_bytes(path, data)`** / **`read_bytes(path)`** - preserve exact
   byte content with binary `"wb"`/`"rb"` modes.
4. **`directory_inventory(root)`** - recursively classify descendants and
   return deterministic relative paths plus file sizes.
5. **`parse_positive_int(text)`** - parse and validate an integer, chaining
   a translated `ValueError` to the original parse failure with `raise ...
   from ...`, but raising a plain `ValueError` for a value that parsed
   successfully but failed the positivity check.
6. **`use_resource(resource, *, fail=False)`** - adapt the provided
   `.close()`-only object with `contextlib.closing`, use it, and guarantee
   closure whether the operation succeeds or raises.

## Constraints

- No custom exception class is defined in this chapter's exercises --
  every raised error is a built-in (`ValueError`, `RuntimeError`,
  `ZeroDivisionError`). Authoring your own exception type is Chapter 9,
  once inheritance has been taught.
- Each starter initially raises `NotImplementedError`, so the checks stop
  at the first incomplete task with a focused traceback.
- File-based tasks run inside a `tempfile.TemporaryDirectory`, so the
  checks leave nothing behind regardless of whether they pass.

## Edge cases exercised

- `parse_positive_int` is checked on three inputs: a valid positive
  integer, unparseable text (must chain `__cause__` to the original
  `ValueError` from `int()`), and a parseable but non-positive integer
  (must raise `ValueError` with `__cause__` left `None`, since there is no
  earlier exception to chain from).
- `use_resource` is checked on both the success path and a deliberate
  `RuntimeError` path. The provided resource must be used and closed either
  way, and the error must still propagate rather than being suppressed.
- `directory_inventory` is checked against a tree with an empty directory,
  a nested directory, and files at two different depths, asserting an
  already-sorted, deterministic result.
