"""
Solutions: 10 Application Integration
"""

import json
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


def encode_task(task):
    return json.dumps(task, sort_keys=True)


def decode_task(payload):
    data = json.loads(payload)
    if not isinstance(data, dict) or set(data) != {"id", "title", "done"}:
        raise ValueError("Expected a task JSON object")
    return data


def initialize_database(path):
    # sqlite3's transaction context commits or rolls back; closing owns the
    # separate responsibility of releasing the connection afterward.
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )


def add_task(path, title):
    with closing(sqlite3.connect(path)) as connection, connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)",
            (title,),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not return an ID")
        return cursor.lastrowid


def list_tasks(path):
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()
    return [
        {"id": task_id, "title": title, "done": bool(done)}
        for task_id, title, done in rows
    ]


def parse_task_path(path):
    parts = [part for part in path.split("/") if part]
    if len(parts) != 2 or parts[0] != "tasks":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


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
