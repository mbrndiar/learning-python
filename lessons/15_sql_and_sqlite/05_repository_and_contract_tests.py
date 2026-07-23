"""
Chapter 15, Lesson 5: Repository and Contract Tests

Purpose: keep application logic dependent on one narrow TaskRepository
Protocol, then run the same behavior contract against an in-memory adapter and
a SQLite adapter. The composition code owns the SQLite connection.

Prerequisite: Chapter 11 protocols/DI and Lessons 1-4 of this chapter.

Run from the repository root:

    python lessons/15_sql_and_sqlite/05_repository_and_contract_tests.py
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool


class TaskRepository(Protocol):
    """The persistence capability required by application logic."""

    def add(self, title: str) -> Task:
        """Store and return a new task."""

    def find(self, task_id: int) -> Task | None:
        """Return one task, or None when it does not exist."""

    def list_all(self) -> list[Task]:
        """Return every task in stable ID order."""

    def set_done(self, task_id: int, done: bool) -> bool:
        """Update one task and report whether it existed."""


# Step 1: the in-memory adapter has no SQL. It is useful when a caller needs a
# fast local implementation of the same observable capability.
class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, title: str) -> Task:
        task = Task(self._next_id, title, False)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def find(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list_all(self) -> list[Task]:
        return [self._tasks[task_id] for task_id in sorted(self._tasks)]

    def set_done(self, task_id: int, done: bool) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        self._tasks[task_id] = replace(task, done=done)
        return True


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


# Step 2: the SQLite adapter owns SQL, row mapping, and operation transaction
# boundaries. Its caller injected and still owns the Connection lifetime.
class SQLiteTaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, title: str) -> Task:
        with self._connection:
            cursor = self._connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,),
            )
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not generate a task ID")
        return Task(cursor.lastrowid, title, False)

    def find(self, task_id: int) -> Task | None:
        row = self._connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return None if row is None else row_to_task(row)

    def list_all(self) -> list[Task]:
        rows = self._connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()
        return [row_to_task(row) for row in rows]

    def set_done(self, task_id: int, done: bool) -> bool:
        with self._connection:
            cursor = self._connection.execute(
                "UPDATE tasks SET done = ? WHERE id = ?",
                (int(done), task_id),
            )
        return cursor.rowcount == 1


# Step 3: application logic sees only TaskRepository, not sqlite3.
def complete_first_open_task(repository: TaskRepository) -> Task | None:
    """Complete and return the first open task, or None when none remain."""
    first_open = next((task for task in repository.list_all() if not task.done), None)
    if first_open is None:
        return None
    if not repository.set_done(first_open.id, True):
        return None
    return replace(first_open, done=True)


# Step 4: one contract describes observable behavior for every fresh adapter.
# It does not assert private data structures, SQL text, or performance.
def assert_repository_contract(repository: TaskRepository) -> None:
    first = repository.add("Read the contract")
    second = repository.add("Implement the adapter")

    assert first == Task(1, "Read the contract", False)
    assert second == Task(2, "Implement the adapter", False)
    assert repository.find(first.id) == first
    assert repository.find(999) is None
    assert repository.list_all() == [first, second]
    assert repository.set_done(999, True) is False

    completed = complete_first_open_task(repository)
    assert completed == Task(1, "Read the contract", True)
    assert repository.find(first.id) == completed


if __name__ == "__main__":
    memory_repository = InMemoryTaskRepository()
    assert_repository_contract(memory_repository)
    print("in-memory repository contract: OK")

    # Composition owns setup and close; the repository receives the ready
    # connection and never hides its lifetime.
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)
        sqlite_repository = SQLiteTaskRepository(database)
        assert_repository_contract(sqlite_repository)
    print("SQLite repository contract: OK")
