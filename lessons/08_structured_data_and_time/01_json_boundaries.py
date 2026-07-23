"""
Chapter 8, Lesson 1: JSON Boundaries

Purpose: distinguish JSON's value model from Python's, convert between
them with `dump`/`load`/`dumps`/`loads`, validate decoded data at the
boundary, produce deterministic output, and handle malformed input.

Prerequisites: Chapter 7 (exception flow, paths, files). JSON files are
read and written with the same `open()`/`Path` tools that chapter already
taught.

Read this file top to bottom, predict each output, then run it:

    python lessons/08_structured_data_and_time/01_json_boundaries.py
"""

import json
import tempfile
from pathlib import Path

# Step 1: JSON has exactly six value kinds: object, array, string, number,
# boolean, and null. Python's richer type system maps onto them, but not
# one-to-one -- a Python tuple becomes a JSON array (indistinguishable from
# a list on the way back), and JSON has no separate int/float distinction
# the way Python does (a whole-looking JSON number decodes to int only
# when it has no decimal point or exponent).
python_value = {
    "name": "Ada",
    "tags": ("core", "admin"),  # tuple -> JSON array
    "score": 9.5,
    "attempts": 3,
    "active": True,
    "notes": None,
}
text = json.dumps(python_value)
print("JSON text:", text)

decoded = json.loads(text)
print("Decoded value:", decoded)
print("Tags decoded as:", type(decoded["tags"]).__name__)  # list, not tuple
assert isinstance(decoded["tags"], list)  # the tuple/list distinction did not survive


# Step 2: `dumps`/`loads` work with in-memory strings; `dump`/`load` work
# directly with an open file, saving you from an intermediate string.
# `indent` only affects the textual layout -- the decoded Python value is
# identical whether the JSON is compact or spread across multiple lines.
def save_tasks(path: Path, tasks: list) -> None:
    """Write tasks as readable, deterministic UTF-8 JSON."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_tasks_raw(path: Path):
    """Load and decode JSON without validating its shape yet."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# Step 3: validation. json.loads()/json.load() only guarantee valid JSON
# *syntax* -- they say nothing about whether the decoded value has the
# shape your program actually needs. Treat decoded data as untrusted
# boundary input until every required field and type has been checked.
def validate_task(item: object) -> dict:
    """Return one task after validating its required fields and types."""
    if not isinstance(item, dict):
        raise ValueError("each task must be a JSON object")

    task_id = item.get("id")
    title = item.get("title")
    done = item.get("done")
    if (
        not isinstance(task_id, int)
        # bool is a subclass of int in Python, so isinstance(True, int) is
        # True. Reject it explicitly -- a boolean is not a meaningful ID.
        or isinstance(task_id, bool)
        or not isinstance(title, str)
        or not isinstance(done, bool)
    ):
        raise ValueError("each task needs an integer id, string title, boolean done")
    return item


def load_tasks(path: Path) -> list:
    """Load tasks and validate both the top level and each item's fields."""
    data = load_tasks_raw(path)
    if not isinstance(data, list):
        raise ValueError("task data must be a JSON array")
    return [validate_task(item) for item in data]


tasks = [
    {"id": 2, "title": "Validate boundaries", "done": True},
    {"id": 1, "title": "Learn JSON", "done": False},
]

with tempfile.TemporaryDirectory(prefix="json_lesson_") as directory:
    path = Path(directory) / "tasks.json"
    save_tasks(path, tasks)
    print("\nFile contents (sort_keys=True gives deterministic key order):")
    print(path.read_text(encoding="utf-8"))
    print("Loaded and validated:", load_tasks(path))

    # Step 4: malformed input. A syntax error raises json.JSONDecodeError
    # (a subclass of ValueError); a shape error raises the ValueError this
    # lesson's own validate_task() raises. Both are ordinary exceptions,
    # handled the way Chapter 7 taught.
    malformed_path = Path(directory) / "malformed.json"
    malformed_path.write_text(
        '{"id": 1, "title": "oops"', encoding="utf-8"
    )  # missing }
    try:
        load_tasks_raw(malformed_path)
    except json.JSONDecodeError as error:
        print("\nExpected syntax error:", error)

    wrong_shape_path = Path(directory) / "wrong_shape.json"
    wrong_shape_path.write_text(
        json.dumps([{"id": "not-a-number", "title": "x", "done": False}]),
        encoding="utf-8",
    )
    try:
        load_tasks(wrong_shape_path)
    except ValueError as error:
        print("Expected shape error:", error)

# --- One-variable experiment -------------------------------------------
# Change validate_task's `task_id` field to accept a string instead of an
# int, and predict which of the two malformed-input checks above (syntax
# or shape) would then pass instead of raising. Only the shape check
# depends on validate_task's rules -- the syntax check depends on json's
# own parser and is unaffected by validation logic.
