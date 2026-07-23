"""
Solutions: Chapter 7 - Exceptions, Files, and Paths

Reference solutions for exercises/07_exceptions_files_and_paths/exercises.py.

Run this file directly:

    python exercises/07_exceptions_files_and_paths/solutions.py
"""

import tempfile
from contextlib import closing
from pathlib import Path


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line + "\n")


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle]


def write_bytes(path, data):
    with open(path, "wb") as handle:
        handle.write(data)


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def directory_inventory(root):
    root = Path(root)
    entries = []
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            entries.append((relative, "directory", None))
        else:
            entries.append((relative, "file", path.stat().st_size))
    return sorted(entries, key=lambda entry: entry[0])


def parse_positive_int(text):
    try:
        value = int(text)
    except ValueError as error:
        raise ValueError(f"not a valid integer: {text!r}") from error
    if value <= 0:
        raise ValueError(f"expected a positive integer, got {value}")
    return value


class TrackingResource:
    def __init__(self):
        self.used = False
        self.closed = False

    def use(self):
        self.used = True
        return "resource used"

    def close(self):
        self.closed = True


def use_resource(resource, *, fail=False):
    with closing(resource):
        result = resource.use()
        if fail:
            raise RuntimeError("simulated failure inside the block")
        return result


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
    assert isinstance(error.__cause__, ValueError)
try:
    parse_positive_int("-5")
    raise AssertionError("expected ValueError for a non-positive value")
except ValueError as error:
    assert error.__cause__ is None
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
