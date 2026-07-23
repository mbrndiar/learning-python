"""
Chapter 15, Lesson 2: Relational Schema and CRUD

Purpose: place data invariants in a relational schema, then implement
parameterized create, read, update, and delete operations. SQL parameters carry
values only; identifiers and SQL syntax remain trusted program structure.

Prerequisite: Lesson 1's Connection, Cursor, and row-mapping lifecycle.

Run from the repository root:

    python lessons/15_sql_and_sqlite/02_relational_schema_and_crud.py
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    id: int
    project_id: int
    title: str
    priority: int
    done: bool


# Step 1: enable foreign keys immediately after connect and before a
# transaction. SQLite configures this per connection; changing the pragma while
# a transaction is open has no effect.
def create_schema(connection: sqlite3.Connection) -> None:
    """Create constrained projects and tasks tables."""
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        BEGIN;
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE CHECK (name <> '')
        );

        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL CHECK (title <> ''),
            priority INTEGER NOT NULL
                CHECK (
                    typeof(priority) = 'integer'
                    AND priority BETWEEN 1 AND 5
                ),
            done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
            UNIQUE (project_id, title),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        COMMIT;
        """
    )


# Step 2: parameters keep data separate from SQL text. Named placeholders are
# useful when field names clarify a multi-value statement.
def add_project(connection: sqlite3.Connection, name: str) -> int:
    """Insert one project and return its SQLite-generated ID."""
    with connection:
        cursor = connection.execute(
            "INSERT INTO projects (name) VALUES (:name)",
            {"name": name},
        )
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not generate a project ID")
    return cursor.lastrowid


def add_task(
    connection: sqlite3.Connection,
    project_id: int,
    title: str,
    priority: int,
) -> int:
    """Insert an unfinished task and return its SQLite-generated ID."""
    with connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (project_id, title, priority)
            VALUES (?, ?, ?)
            """,
            (project_id, title, priority),
        )
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not generate a task ID")
    return cursor.lastrowid


def row_to_task(row: sqlite3.Row) -> Task:
    """Convert SQLite storage values into explicit domain types."""
    return Task(
        id=int(row["id"]),
        project_id=int(row["project_id"]),
        title=str(row["title"]),
        priority=int(row["priority"]),
        done=bool(row["done"]),
    )


# Step 3: read operations define their columns and deterministic ordering.
# A placeholder can represent minimum_priority or limit because those are
# values. It cannot represent a column name or DESC because those are syntax.
def list_tasks(
    connection: sqlite3.Connection,
    *,
    minimum_priority: int,
    limit: int,
) -> list[Task]:
    """Return tasks ordered by priority descending, then ID ascending."""
    rows = connection.execute(
        """
        SELECT id, project_id, title, priority, done
        FROM tasks
        WHERE priority >= ?
        ORDER BY priority DESC, id ASC
        LIMIT ?
        """,
        (minimum_priority, limit),
    ).fetchall()
    return [row_to_task(row) for row in rows]


# Step 4: UPDATE and DELETE cursors expose affected-row counts. Returning a bool
# preserves the important "target was absent" path instead of claiming success.
def set_task_done(
    connection: sqlite3.Connection,
    task_id: int,
    done: bool,
) -> bool:
    """Update one task and report whether it existed."""
    with connection:
        cursor = connection.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (int(done), task_id),
        )
    return cursor.rowcount == 1


def delete_task(connection: sqlite3.Connection, task_id: int) -> bool:
    """Delete one task and report whether it existed."""
    with connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
    return cursor.rowcount == 1


if __name__ == "__main__":
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)

        course_id = add_project(database, "Course")
        high_id = add_task(database, course_id, "Read O'Brien's notes", 5)
        low_id = add_task(database, course_id, "Map storage rows", 2)

        assert list_tasks(database, minimum_priority=1, limit=10) == [
            Task(high_id, course_id, "Read O'Brien's notes", 5, False),
            Task(low_id, course_id, "Map storage rows", 2, False),
        ]
        assert set_task_done(database, low_id, True) is True
        assert set_task_done(database, 999, True) is False
        assert delete_task(database, low_id) is True
        assert delete_task(database, low_id) is False

        try:
            add_task(database, course_id, "", 3)
        except sqlite3.IntegrityError:
            print("schema rejected an empty title")
        else:
            raise AssertionError("the title constraint should reject an empty value")
        assert database.in_transaction is False

        print("tasks:", list_tasks(database, minimum_priority=1, limit=10))
        print("missing update/delete paths returned False")
