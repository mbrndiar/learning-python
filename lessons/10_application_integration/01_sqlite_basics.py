"""
Lesson 10.1: SQLite Basics

sqlite3 provides a transactional relational database in Python's standard
library. Parameter placeholders keep values separate from SQL syntax.
"""

import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path


def initialize_database(path: str | Path) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            # Legacy sqlite3 transaction mode does not begin a transaction for
            # DDL automatically, so make this schema change explicit.
            connection.execute("BEGIN")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                )
                """
            )


def add_task(path: str | Path, title: str) -> int:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, 0)",
                (title,),
            )
            if cursor.lastrowid is None:
                raise RuntimeError("SQLite did not return a task ID")
            return cursor.lastrowid


def list_tasks(path: str | Path) -> list[dict[str, object]]:
    with closing(sqlite3.connect(path)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()
    return [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "tasks.db"
        initialize_database(database)
        add_task(database, "Learn parameterized SQL")
        add_task(database, "Close database connections")
        print(list_tasks(database))
