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

## 🧩 Progressive syntax and mechanism

1. **Propagation.** Raising an exception unwinds the call stack, frame by
   frame, until a matching `except` is found; `error.__traceback__` records
   every frame it passed through.
2. **Narrow `except`.** Name the specific exception type(s) a handler can
   recover from; a bare `except:` or `except Exception:` also hides
   unrelated bugs instead of letting them surface.
3. **`else` and `finally`.** `else` runs only if the `try` block raised
   nothing; `finally` runs unconditionally, for cleanup that must always
   happen.
4. **Bare `raise` and chaining.** A bare `raise` inside an `except` block
   re-raises the exception being handled, unchanged; `raise NewError(...)
   from original` attaches `original` as `__cause__`, documenting a
   deliberate translation.
5. **`Path` values.** `pathlib.Path` represents a location without
   touching the filesystem until you call a method; `/` joins segments;
   relative paths resolve against `Path.cwd()` unless anchored to
   `__file__`.
6. **Directory iteration and metadata.** `iterdir()` lists immediate
   children; `glob()`/`rglob()` match patterns non-recursively/recursively;
   `stat()` exposes size and timestamps; a missing path raises
   `FileNotFoundError` rather than returning a placeholder.
7. **Files, modes, and ownership.** `open(path, mode, encoding=...)` for
   text, `"rb"`/`"wb"` for binary (no encoding); explicit `try`/`finally`
   closes a file by hand before `with` automates the same guarantee.
8. **Newlines.** Text mode translates platform line endings to `"\n"` on
   read (and back on write) unless `newline=""` disables that translation.
9. **`with`, `__enter__`/`__exit__`, and `closing`.** `with` guarantees
   `__exit__` (or `close()`, via `contextlib.closing`) runs whether the
   block succeeded or raised; an active `memoryview` keeps its exporter
   alive and blocks resizing until `release()`.

## 📖 Read-predict-run-modify workflow

Work through the four lesson files in order, predicting each output
before running:

```bash
python lessons/07_exceptions_files_and_paths/01_exception_flow.py
python lessons/07_exceptions_files_and_paths/02_paths_and_directories.py
python lessons/07_exceptions_files_and_paths/03_text_and_binary_files.py
python lessons/07_exceptions_files_and_paths/04_context_managers_and_resource_lifetimes.py
```

### Expected output highlights

- `01_exception_flow.py`: the frames the exception passed through print as
  `['outer', 'middle', 'inner']` -- the traceback records the full path,
  not just where it was caught.
- `02_paths_and_directories.py`: `Temporary tree removed: True` at the end
  confirms the whole directory was cleaned up automatically.
- `03_text_and_binary_files.py`: `Translated newlines` collapses every
  line ending to `"\n"`, while the `newline=""` read preserves the exact
  line-ending sequences (`\r\n`, `\n`, `\r`) in the returned text.
- `04_context_managers_and_resource_lifetimes.py`: `handle.closed` is
  `True` even in Step 3, where the `with` block raised on purpose --
  `__exit__` still ran before the exception reached the `except` clause
  outside it.

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
