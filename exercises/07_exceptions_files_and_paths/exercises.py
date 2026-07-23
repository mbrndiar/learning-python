"""
Exercises: Chapter 7 - Exceptions, Files, and Paths

Implement each function/class below, then run this file directly to check
your work.

    python exercises/07_exceptions_files_and_paths/exercises.py

Each starter raises NotImplementedError until you implement it.
"""

import tempfile
from pathlib import Path


def safe_divide(a, b):
    """Return a / b, or None if `b` is zero.

    Catch ZeroDivisionError instead of checking `b == 0` directly.
    """
    # TODO: implement this function
    raise NotImplementedError


def write_lines(path, lines):
    """Write each string in `lines` to the file at `path`, one per line."""
    # TODO: implement this function
    raise NotImplementedError


def read_lines(path):
    """Return a list of lines from the file at `path`, without trailing
    newline characters."""
    # TODO: implement this function
    raise NotImplementedError


def write_bytes(path, data):
    """Write `data` to `path` unchanged, using binary mode."""
    # TODO: open path with "wb" and write the bytes
    raise NotImplementedError


def read_bytes(path):
    """Return the exact bytes stored at `path`, using binary mode."""
    # TODO: open path with "rb" and return its bytes
    raise NotImplementedError


def directory_inventory(root):
    """Return deterministic metadata for file and directory descendants.

    Return `(relative_path, kind, size)` tuples sorted by POSIX-style
    relative path. Use "directory" with size None and "file" with its byte
    size. Do not include *root* itself.
    """
    # TODO: recursively inspect root with pathlib and return sorted results
    raise NotImplementedError


def parse_positive_int(text):
    """Parse `text` as an integer and require it to be positive.

    Raise ValueError chained from the original int() failure (using
    `raise ... from error`) when `text` is not a valid integer at all.
    Raise a plain ValueError (no chaining needed) when the parsed value is
    zero or negative.
    """
    # TODO: implement this function
    raise NotImplementedError


class TrackingResource:
    """Support object for the learner-owned `use_resource` function."""

    def __init__(self):
        self.used = False
        self.closed = False

    def use(self):
        self.used = True
        return "resource used"

    def close(self):
        self.closed = True


def use_resource(resource, *, fail=False):
    """Use `resource` and guarantee close() on success or failure."""
    # TODO: adapt the provided .close()-only object with closing()
    raise NotImplementedError


assert safe_divide(10, 2) == 5
assert safe_divide(10, 0) is None
print("safe_divide: OK")

with tempfile.TemporaryDirectory(prefix="files_exercise_") as directory:
    root = Path(directory)
    text_path = root / "lines.txt"
    write_lines(text_path, ["alpha", "beta", "gamma"])
    assert read_lines(text_path) == ["alpha", "beta", "gamma"]
    print("write_lines/read_lines: OK")

    binary_path = root / "payload.bin"
    binary_payload = b"\x00Python\xff"
    write_bytes(binary_path, binary_payload)
    assert read_bytes(binary_path) == binary_payload
    print("write_bytes/read_bytes: OK")

with tempfile.TemporaryDirectory(prefix="inventory_exercise_") as directory:
    root = Path(directory)
    (root / "empty").mkdir()
    archive = root / "notes" / "archive"
    archive.mkdir(parents=True)
    (root / "notes" / "todo.txt").write_text("learn\n", encoding="utf-8")
    (archive / "done.txt").write_text("done\n", encoding="utf-8")
    assert directory_inventory(root) == [
        ("empty", "directory", None),
        ("notes", "directory", None),
        ("notes/archive", "directory", None),
        ("notes/archive/done.txt", "file", 5),
        ("notes/todo.txt", "file", 6),
    ]
print("directory_inventory: OK")

assert parse_positive_int("42") == 42
try:
    parse_positive_int("abc")
    raise AssertionError("expected ValueError for non-numeric text")
except ValueError as error:
    assert isinstance(error.__cause__, ValueError), (
        "Task: chain the translated error to the original int() failure"
    )
try:
    parse_positive_int("-5")
    raise AssertionError("expected ValueError for a non-positive value")
except ValueError as error:
    assert error.__cause__ is None, (
        "Task: the non-positive check needs no chaining -- there is no "
        "earlier exception to chain from"
    )
print("parse_positive_int: OK")

resource = TrackingResource()
assert use_resource(resource) == "resource used"
assert resource.used is True
assert resource.closed is True

resource_after_failure = TrackingResource()
try:
    use_resource(resource_after_failure, fail=True)
except RuntimeError:
    pass
else:
    raise AssertionError("use_resource() must propagate RuntimeError")
assert resource_after_failure.used is True
assert resource_after_failure.closed is True
print("use_resource: OK")

print("\nAll checks passed!")
