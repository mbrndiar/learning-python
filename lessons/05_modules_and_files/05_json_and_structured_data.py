"""
Lesson 5.5: JSON and Structured Data

JSON stores dictionaries, lists, strings, numbers, booleans and null in a
language-independent text format. Converting at the boundary keeps the rest of
an application working with ordinary Python values.
"""

import json
import tempfile
from pathlib import Path


def validate_task(item: object) -> dict[str, object]:
    """Return one task after validating its required fields and value types."""
    # json.loads() guarantees valid JSON syntax, not the application-specific
    # shape that the rest of the program expects.
    if not isinstance(item, dict):
        raise ValueError("Each task must be a JSON object")

    task_id = item.get("id")
    title = item.get("title")
    done = item.get("done")
    if (
        not isinstance(task_id, int)
        # bool subclasses int in Python, so isinstance(True, int) is True.
        # Reject it explicitly because a boolean is not a meaningful task ID.
        or isinstance(task_id, bool)
        or not isinstance(title, str)
        or not isinstance(done, bool)
    ):
        raise ValueError("Each task needs integer id, string title, and boolean done")
    return item


def save_tasks(path: Path, tasks: list[dict[str, object]]) -> None:
    """Write tasks as readable UTF-8 JSON."""
    # indent affects only the textual representation. The decoded Python values
    # are the same whether the JSON is compact or human-readable.
    path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")


def load_tasks(path: Path) -> list[dict[str, object]]:
    """Load tasks and validate both the top level and required item fields."""
    # Treat decoded data as untrusted boundary input until every required layer
    # has been validated.
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Task data must be a JSON array")
    return [validate_task(item) for item in data]


if __name__ == "__main__":
    tasks = [
        {"id": 1, "title": "Learn JSON", "done": False},
        {"id": 2, "title": "Validate boundaries", "done": True},
    ]

    text = json.dumps(tasks)
    print("JSON text:", text)
    print("Decoded value:", json.loads(text))

    # TemporaryDirectory removes the directory and its JSON file when the with
    # block ends, keeping this runnable lesson from leaving artifacts behind.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "tasks.json"
        save_tasks(path, tasks)
        print("\nFile contents:")
        print(path.read_text(encoding="utf-8"))
        print("Loaded tasks:", load_tasks(path))
