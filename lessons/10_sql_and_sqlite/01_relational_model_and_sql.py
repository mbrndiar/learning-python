"""
Lesson 10.1: Relational Model and SQL

Relational databases store rows in tables governed by a schema. This lesson
uses broadly portable SQL ideas while sqlite3 supplies the concrete database
and Python DB-API parameter syntax.
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    """A domain value rather than a database-driver row."""

    id: int
    title: str
    done: bool
    priority: int


def create_schema(connection: sqlite3.Connection) -> None:
    # PRIMARY KEY, NOT NULL, DEFAULT and CHECK are common relational concepts.
    # Exact data types and generated-key declarations vary across SQL engines.
    connection.execute(
        """
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL CHECK (title <> ''),
            done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
            priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 5)
        )
        """
    )
    connection.commit()


def insert_task(connection: sqlite3.Connection, task: Task) -> None:
    # Parameterization is portable practice, but placeholder spelling is not:
    # sqlite3 uses ?, while other drivers may use %s or named parameters.
    with connection:
        connection.execute(
            """
            INSERT INTO tasks (id, title, done, priority)
            VALUES (?, ?, ?, ?)
            """,
            (task.id, task.title, int(task.done), task.priority),
        )


def update_task_status(
    connection: sqlite3.Connection,
    task_id: int,
    done: bool,
) -> bool:
    with connection:
        cursor = connection.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (int(done), task_id),
        )
    return cursor.rowcount == 1


def delete_task(connection: sqlite3.Connection, task_id: int) -> bool:
    with connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
    return cursor.rowcount == 1


def row_to_task(row: sqlite3.Row) -> Task:
    """Translate storage values into the application's domain types."""

    return Task(
        id=int(row["id"]),
        title=str(row["title"]),
        done=bool(row["done"]),
        priority=int(row["priority"]),
    )


def list_open_tasks(
    connection: sqlite3.Connection,
    minimum_priority: int,
    limit: int,
) -> list[Task]:
    # Filtering and ordering are portable ideas. LIMIT is SQLite's spelling;
    # some engines use FETCH FIRST or TOP instead.
    rows = connection.execute(
        """
        SELECT id, title, done, priority
        FROM tasks
        WHERE done = ? AND priority >= ?
        ORDER BY priority DESC, id ASC
        LIMIT ?
        """,
        (0, minimum_priority, limit),
    ).fetchall()
    return [row_to_task(row) for row in rows]


if __name__ == "__main__":
    # The code that opens a resource also owns closing it. A connection's
    # transaction context commits or rolls back, but does not close it.
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)

        insert_task(database, Task(1, "Learn relational constraints", False, 3))
        insert_task(database, Task(2, "Map rows to domain values", False, 2))
        insert_task(database, Task(3, "Review O'Brien's notes", False, 5))

        assert update_task_status(database, 2, True)
        assert list_open_tasks(database, minimum_priority=3, limit=2) == [
            Task(3, "Review O'Brien's notes", False, 5),
            Task(1, "Learn relational constraints", False, 3),
        ]
        assert delete_task(database, 2)

        print(list_open_tasks(database, minimum_priority=1, limit=10))
