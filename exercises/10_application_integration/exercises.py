"""
Exercises: 10 Application Integration

Implement the JSON, SQLite and route-parsing functions below, then run this
file directly to check your work.
"""

import json
import sqlite3
import tempfile
from pathlib import Path


def encode_task(task):
    """Return a deterministic JSON string for one task dictionary."""
    # TODO: implement this function
    raise NotImplementedError


def decode_task(payload):
    """Decode payload and require a JSON object with id, title and done keys."""
    # TODO: implement this function
    raise NotImplementedError


def initialize_database(path):
    """Create a tasks table with id, title and done columns."""
    # TODO: implement this function
    raise NotImplementedError


def add_task(path, title):
    """Insert an unfinished task using a parameterized query and return its ID."""
    # TODO: implement this function
    raise NotImplementedError


def list_tasks(path):
    """Return tasks ordered by ID as dictionaries with real booleans."""
    # TODO: implement this function
    raise NotImplementedError


def parse_task_path(path):
    """Return the integer ID from '/tasks/<id>', otherwise return None."""
    # TODO: implement this function
    raise NotImplementedError


if __name__ == "__main__":
    task = {"id": 1, "title": "Integrate pieces", "done": False}
    assert encode_task(task) == '{"done": false, "id": 1, "title": "Integrate pieces"}'
    assert decode_task(encode_task(task)) == task
    print("JSON boundary: OK")

    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "tasks.db"
        initialize_database(database)
        assert add_task(database, "First") == 1
        assert add_task(database, "Second") == 2
        assert list_tasks(database) == [
            {"id": 1, "title": "First", "done": False},
            {"id": 2, "title": "Second", "done": False},
        ]
    print("SQLite storage: OK")

    assert parse_task_path("/tasks/42") == 42
    assert parse_task_path("/tasks/not-a-number") is None
    assert parse_task_path("/other/42") is None
    print("Route parsing: OK")

    print("\nAll checks passed!")
