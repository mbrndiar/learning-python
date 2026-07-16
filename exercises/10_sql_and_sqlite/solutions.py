"""Solutions: 10 SQL and SQLite."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: int
    project_id: int
    title: str
    priority: int
    done: bool


@dataclass(frozen=True)
class TaskProject:
    task_title: str
    project_name: str


@dataclass(frozen=True)
class ProjectSummary:
    project_name: str
    task_count: int


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE CHECK (name <> '')
        );

        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL CHECK (title <> ''),
            priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 5),
            done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
            UNIQUE (project_id, title),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """
    )


def add_project(connection: sqlite3.Connection, name: str) -> int:
    with connection:
        cursor = connection.execute(
            "INSERT INTO projects (name) VALUES (?)",
            (name,),
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
    with connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (project_id, title, priority, done)
            VALUES (?, ?, ?, 0)
            """,
            (project_id, title, priority),
        )
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not generate a task ID")
    return cursor.lastrowid


def set_task_done(
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
    return Task(
        id=int(row["id"]),
        project_id=int(row["project_id"]),
        title=str(row["title"]),
        priority=int(row["priority"]),
        done=bool(row["done"]),
    )


def list_tasks(
    connection: sqlite3.Connection,
    *,
    done: bool | None,
    minimum_priority: int,
    limit: int,
) -> list[Task]:
    done_filter = None if done is None else int(done)
    rows = connection.execute(
        """
        SELECT id, project_id, title, priority, done
        FROM tasks
        WHERE (? IS NULL OR done = ?) AND priority >= ?
        ORDER BY priority DESC, id ASC
        LIMIT ?
        """,
        (done_filter, done_filter, minimum_priority, limit),
    ).fetchall()
    return [row_to_task(row) for row in rows]


def list_tasks_with_projects(
    connection: sqlite3.Connection,
) -> list[TaskProject]:
    rows = connection.execute(
        """
        SELECT tasks.title AS task_title, projects.name AS project_name
        FROM tasks
        INNER JOIN projects ON projects.id = tasks.project_id
        ORDER BY tasks.id
        """
    ).fetchall()
    return [
        TaskProject(str(row["task_title"]), str(row["project_name"])) for row in rows
    ]


def summarize_projects(
    connection: sqlite3.Connection,
    minimum_task_count: int,
) -> list[ProjectSummary]:
    rows = connection.execute(
        """
        SELECT projects.name AS project_name, COUNT(tasks.id) AS task_count
        FROM projects
        LEFT JOIN tasks ON tasks.project_id = projects.id
        GROUP BY projects.id, projects.name
        HAVING COUNT(tasks.id) >= ?
        ORDER BY projects.id
        """,
        (minimum_task_count,),
    ).fetchall()
    return [
        ProjectSummary(str(row["project_name"]), int(row["task_count"])) for row in rows
    ]


def add_pair_atomically(
    connection: sqlite3.Connection,
    project_id: int,
    first_title: str,
    second_title: str,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO tasks (project_id, title, priority, done)
            VALUES (?, ?, 1, 0)
            """,
            (project_id, first_title),
        )
        connection.execute(
            """
            INSERT INTO tasks (project_id, title, priority, done)
            VALUES (?, ?, 1, 0)
            """,
            (project_id, second_title),
        )


class TaskRepository(Protocol):
    def add(self, project_id: int, title: str, priority: int) -> Task:
        """Store and return a new task."""

    def list(
        self,
        *,
        done: bool | None,
        minimum_priority: int,
        limit: int,
    ) -> list[Task]:
        """Return tasks matching the requested view."""

    def set_done(self, task_id: int, done: bool) -> bool:
        """Update one task."""


class SQLiteTaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, project_id: int, title: str, priority: int) -> Task:
        task_id = add_task(self._connection, project_id, title, priority)
        return Task(task_id, project_id, title, priority, False)

    def list(
        self,
        *,
        done: bool | None,
        minimum_priority: int,
        limit: int,
    ) -> list[Task]:
        return list_tasks(
            self._connection,
            done=done,
            minimum_priority=minimum_priority,
            limit=limit,
        )

    def set_done(self, task_id: int, done: bool) -> bool:
        return set_task_done(self._connection, task_id, done)


def finish_next_task(repository: TaskRepository) -> Task | None:
    open_tasks = repository.list(
        done=False,
        minimum_priority=1,
        limit=1,
    )
    if not open_tasks:
        return None

    task = open_tasks[0]
    if not repository.set_done(task.id, True):
        return None
    return Task(task.id, task.project_id, task.title, task.priority, True)


def assert_repository_contract(
    repository: TaskRepository,
    project_id: int,
) -> None:
    low = repository.add(project_id, "Low priority", 1)
    high = repository.add(project_id, "High priority", 5)
    assert repository.list(done=False, minimum_priority=1, limit=10) == [high, low]
    assert repository.set_done(high.id, True)
    assert repository.list(done=True, minimum_priority=1, limit=10) == [
        Task(high.id, project_id, "High priority", 5, True)
    ]


if __name__ == "__main__":
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)

        course_id = add_project(database, "Course")
        empty_id = add_project(database, "Empty")
        quoted_id = add_task(database, course_id, "Read O'Brien's notes", 5)
        docs_id = add_task(database, course_id, "Write docs", 3)

        assert list_tasks(
            database,
            done=False,
            minimum_priority=3,
            limit=2,
        ) == [
            Task(quoted_id, course_id, "Read O'Brien's notes", 5, False),
            Task(docs_id, course_id, "Write docs", 3, False),
        ]
        assert set_task_done(database, docs_id, True)
        assert list_tasks_with_projects(database) == [
            TaskProject("Read O'Brien's notes", "Course"),
            TaskProject("Write docs", "Course"),
        ]
        assert summarize_projects(database, minimum_task_count=0) == [
            ProjectSummary("Course", 2),
            ProjectSummary("Empty", 0),
        ]

        try:
            add_pair_atomically(
                database,
                course_id,
                "Must roll back",
                "Read O'Brien's notes",
            )
        except sqlite3.IntegrityError:
            pass
        assert all(
            task.title != "Must roll back"
            for task in list_tasks(
                database,
                done=None,
                minimum_priority=1,
                limit=20,
            )
        )

        temporary_id = add_task(database, empty_id, "Delete me", 1)
        assert delete_task(database, temporary_id)

        invalid_tasks = [
            (course_id, "", 1),
            (course_id, "Invalid priority", 6),
            (999, "Missing project", 1),
        ]
        for invalid_project, invalid_title, invalid_priority in invalid_tasks:
            try:
                add_task(
                    database,
                    invalid_project,
                    invalid_title,
                    invalid_priority,
                )
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError("A schema constraint should reject this task")

    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)
        project_id = add_project(database, "Repository contract")
        repository = SQLiteTaskRepository(database)
        assert_repository_contract(repository, project_id)
        completed = finish_next_task(repository)
        assert completed == Task(1, project_id, "Low priority", 1, True)

    print("All checks passed!")
