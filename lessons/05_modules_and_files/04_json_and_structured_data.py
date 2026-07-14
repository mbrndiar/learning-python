"""
Lesson 5.4: JSON and Structured Data

JSON stores dictionaries, lists, strings, numbers, booleans and null in a
language-independent text format. Converting at the boundary keeps the rest of
an application working with ordinary Python values.
"""

import json
import tempfile
from pathlib import Path


def save_tasks(path: Path, tasks: list[dict[str, object]]) -> None:
    """Write tasks as readable UTF-8 JSON."""
    path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")


def load_tasks(path: Path) -> list[dict[str, object]]:
    """Load a list of task dictionaries and reject an unexpected top level."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Task data must be a JSON array of objects")
    return data


if __name__ == "__main__":
    tasks = [
        {"id": 1, "title": "Learn JSON", "done": False},
        {"id": 2, "title": "Validate boundaries", "done": True},
    ]

    text = json.dumps(tasks)
    print("JSON text:", text)
    print("Decoded value:", json.loads(text))

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "tasks.json"
        save_tasks(path, tasks)
        print("\nFile contents:")
        print(path.read_text(encoding="utf-8"))
        print("Loaded tasks:", load_tasks(path))
