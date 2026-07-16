"""
Exercises: 10 SQL and SQLite

Implement the schema, queries, transaction, mapping, and repository adapter
below. The checks use only in-memory SQLite databases.
"""

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
    """Create constrained projects and tasks tables and enable foreign keys."""

    # TODO: implement this function
    raise NotImplementedError


def add_project(connection: sqlite3.Connection, name: str) -> int:
    """Insert a project with a parameter and return its SQLite-generated ID."""

    # TODO: implement this function
    raise NotImplementedError


def add_task(
    connection: sqlite3.Connection,
    project_id: int,
    title: str,
    priority: int,
) -> int:
    """Insert an unfinished task with parameters and return its ID."""

    # TODO: implement this function
    raise NotImplementedError


def set_task_done(
    connection: sqlite3.Connection,
    task_id: int,
    done: bool,
) -> bool:
    """Update one task and report whether it existed."""

    # TODO: implement this function
    raise NotImplementedError


def delete_task(connection: sqlite3.Connection, task_id: int) -> bool:
    """Delete one task and report whether it existed."""

    # TODO: implement this function
    raise NotImplementedError


def row_to_task(row: sqlite3.Row) -> Task:
    """Map a storage row to a Task with a real bool."""

    # TODO: implement this function
    raise NotImplementedError


def list_tasks(
    connection: sqlite3.Connection,
    *,
    done: bool | None,
    minimum_priority: int,
    limit: int,
) -> list[Task]:
    """Filter tasks and order by priority descending, then ID ascending."""

    # TODO: implement this function
    raise NotImplementedError


def list_tasks_with_projects(
    connection: sqlite3.Connection,
) -> list[TaskProject]:
    """Use one inner join and return rows in task-ID order."""

    # TODO: implement this function
    raise NotImplementedError


def summarize_projects(
    connection: sqlite3.Connection,
    minimum_task_count: int,
) -> list[ProjectSummary]:
    """Use a left join, COUNT, GROUP BY, and HAVING in project-ID order."""

    # TODO: implement this function
    raise NotImplementedError


def add_pair_atomically(
    connection: sqlite3.Connection,
    project_id: int,
    first_title: str,
    second_title: str,
) -> None:
    """Insert both tasks in one transaction, rolling both back on failure."""

    # TODO: implement this function
    raise NotImplementedError


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
    """Implement TaskRepository while the caller owns the connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        # TODO: implement this method
        raise NotImplementedError

    def add(self, project_id: int, title: str, priority: int) -> Task:
        # TODO: implement this method
        raise NotImplementedError

    def list(
        self,
        *,
        done: bool | None,
        minimum_priority: int,
        limit: int,
    ) -> list[Task]:
        # TODO: implement this method
        raise NotImplementedError

    def set_done(self, task_id: int, done: bool) -> bool:
        # TODO: implement this method
        raise NotImplementedError


def finish_next_task(repository: TaskRepository) -> Task | None:
    """Complete the highest-priority open task through an injected repository."""

    # TODO: implement this function
    raise NotImplementedError


def assert_repository_contract(
    repository: TaskRepository,
    project_id: int,
) -> None:
    """Checks reusable for every fresh TaskRepository implementation."""

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
