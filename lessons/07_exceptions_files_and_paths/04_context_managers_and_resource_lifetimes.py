"""
Chapter 7, Lesson 4: Context Managers and Resource Lifetimes

Purpose: understand `with` as a bounded, guaranteed-cleanup pattern built on
`__enter__`/`__exit__`; use `contextlib.closing` to adapt an object that
only offers `.close()`; and see why an active `memoryview` prevents its
exporting buffer from being resized.

Prerequisites: Lessons 1-3 (exception flow, paths, files). This lesson
covers only class-based context managers; the `@contextmanager` decorator
(building one from a generator function) is Chapter 10, once generators
have been taught.

Read this file top to bottom, predict each output, then run it:

    python lessons/07_exceptions_files_and_paths/04_context_managers_and_resource_lifetimes.py
"""

import tempfile
from contextlib import closing
from pathlib import Path

# Step 1: `with` replaces the manual try/finally from Lesson 3 with one
# guarantee: whatever object follows `with` has its cleanup method called
# when the block ends, whether it ended normally or by raising. `open()`
# already returns such an object. Lesson 3 wrote the equivalent explicit
# try/finally pattern; this lesson now replaces that repetition with `with`.
with tempfile.TemporaryDirectory(prefix="context_lesson_") as directory:
    root = Path(directory)
    sample_path = root / "sample.txt"

    with open(sample_path, "w", encoding="utf-8") as handle:
        handle.write("first line\n")
    print("File closed after the with block:", handle.closed)

    # Step 2: a class becomes usable with `with` by implementing
    # `__enter__` (runs at the start of the block, returns the value bound
    # by `as`) and `__exit__` (runs at the end, always -- on success and on
    # failure alike).
    class ManagedFile:
        """A minimal re-implementation of what `open()` guarantees."""

        def __init__(self, path, mode):
            self.path = path
            self.mode = mode
            self.file = None

        def __enter__(self):
            self.file = open(self.path, self.mode, encoding="utf-8")
            return self.file  # the value `as file` receives

        def __exit__(self, exc_type, exc_value, traceback):
            # Python calls __exit__ whether the block finished normally or
            # raised -- cleanup belongs here, not only after the with
            # statement's normal path.
            if self.file:
                self.file.close()
            # A truthy return here would suppress the active exception.
            # Returning False (or None) preserves it after cleanup runs --
            # the safer default, used here.
            return False

    with ManagedFile(sample_path, "a") as handle:
        handle.write("second line\n")
    print("ManagedFile closed:", handle.closed)

    # Step 3: __exit__ runs even when the block raises. This block writes a
    # line, then raises on purpose; the file is still closed afterward.
    try:
        with ManagedFile(sample_path, "a") as handle:
            handle.write("third line\n")
            raise RuntimeError("simulated failure inside the block")
    except RuntimeError as error:
        print("Caught after cleanup already ran:", error)
    print("ManagedFile closed even after an error:", handle.closed)

    print("\nFinal file contents:")
    print(sample_path.read_text(encoding="utf-8"))

    # Step 4: `contextlib.closing` adapts any object with a plain
    # `.close()` method (but no __enter__/__exit__ of its own) into a
    # context manager, guaranteeing that close() runs at the end of the
    # block.
    class LegacyResource:
        """Pretend this older class predates the context manager protocol."""

        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    legacy = LegacyResource()
    with closing(legacy):
        print("\nLegacy resource closed inside the block?", legacy.closed)
    print("Legacy resource closed after the block:", legacy.closed)

    # Step 5: a memoryview exposes another object's buffer without copying
    # it. The view keeps its exporter alive and prevents operations that
    # would resize that buffer until the view is released.
    payload = bytearray(b"binary-data")
    view = memoryview(payload)
    print("\nmemoryview of the first 6 bytes:", bytes(view[:6]))
    payload[0:6] = b"BINARY"
    print("Same memoryview after mutating payload:", bytes(view[:6]))
    try:
        payload.extend(b"!")
    except BufferError:
        print("Resize blocked while memoryview is active")

    # The memoryview did not copy the data -- it shows payload's current
    # bytes, live. Releasing it ends that exported view and permits resize.
    view.release()
    payload.extend(b"!")
    print("Resize after release:", payload)

# --- One-variable experiment -------------------------------------------
# In Step 3, remove the `raise RuntimeError(...)` line and predict whether
# `handle.closed` still prints True. __exit__ runs at the end of every
# `with` block, not only when an exception occurs -- Step 2 already showed
# that on the success path.
