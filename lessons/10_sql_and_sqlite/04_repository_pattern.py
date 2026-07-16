"""
Lesson 10.4: A Small Repository Boundary

A repository can keep SQL and row mapping out of application logic. Introduce
this boundary when it removes a real dependency or supports interchangeable
tests; do not add layers merely because an application contains a database.
"""

import sqlite3
from collections.abc import Iterable
from contextlib import closing
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool


class TaskRepository(Protocol):
    """The small capability the application actually needs."""

    def add(self, title: str) -> Task:
        """Store and return a new task."""

    def find(self, task_id: int) -> Task | None:
        """Return one task, or None when it does not exist."""

    def list_all(self) -> list[Task]:
        """Return tasks in stable ID order."""


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL CHECK (title <> ''),
            done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
        )
        """
    )
    connection.commit()


def row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=int(row["id"]),
        title=str(row["title"]),
        done=bool(row["done"]),
    )


class SQLiteTaskRepository:
    """SQLite adapter; its caller owns the injected connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, title: str) -> Task:
        with self._connection:
            cursor = self._connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,),
            )
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not generate an ID")
        return Task(cursor.lastrowid, title, False)

    def find(self, task_id: int) -> Task | None:
        row = self._connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
        return None if row is None else row_to_task(row)

    def list_all(self) -> list[Task]:
        rows = self._connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            ORDER BY id
            """
        ).fetchall()
        return [row_to_task(row) for row in rows]


def add_tasks(
    repository: TaskRepository,
    titles: Iterable[str],
) -> list[Task]:
    """Application logic receives its dependency instead of opening SQLite."""

    for title in titles:
        repository.add(title)
    return repository.list_all()


def assert_repository_contract(repository: TaskRepository) -> None:
    """Illustrate checks that every repository implementation should pass."""

    first = repository.add("Contract task")
    assert first == Task(1, "Contract task", False)
    assert repository.find(first.id) == first
    assert repository.find(999) is None
    assert repository.list_all() == [first]


if __name__ == "__main__":
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)
        repository = SQLiteTaskRepository(database)
        assert_repository_contract(repository)

    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)
        repository = SQLiteTaskRepository(database)
        print(add_tasks(repository, ["Read the schema", "Test the boundary"]))
