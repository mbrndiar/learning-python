"""
Lesson 10.2: Joins, Aggregates, and Indexes

Joins combine related rows, aggregates summarize groups, and indexes can make
selected lookups cheaper. The optimizer remains responsible for choosing a
query plan.
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskProject:
    task_title: str
    project_name: str


@dataclass(frozen=True)
class ProjectTask:
    project_name: str
    task_title: str | None


@dataclass(frozen=True)
class ProjectSummary:
    project_name: str
    task_count: int
    completed_count: int


def create_schema(connection: sqlite3.Connection) -> None:
    # SQLite does not enforce foreign keys unless each connection enables them.
    # Other database engines configure referential integrity differently.
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            done INTEGER NOT NULL CHECK (done IN (0, 1)),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """
    )


def seed_data(connection: sqlite3.Connection) -> None:
    with connection:
        connection.executemany(
            "INSERT INTO projects (id, name) VALUES (?, ?)",
            [(1, "Course"), (2, "Garden"), (3, "Empty project")],
        )
        connection.executemany(
            """
            INSERT INTO tasks (id, project_id, title, done)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, 1, "Read SQL lesson", 1),
                (2, 1, "Practice joins", 0),
                (3, 2, "Plant herbs", 0),
            ],
        )


def list_tasks_with_projects(connection: sqlite3.Connection) -> list[TaskProject]:
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


def list_projects_with_optional_tasks(
    connection: sqlite3.Connection,
) -> list[ProjectTask]:
    rows = connection.execute(
        """
        SELECT projects.name AS project_name, tasks.title AS task_title
        FROM projects
        LEFT JOIN tasks ON tasks.project_id = projects.id
        ORDER BY projects.id, tasks.id
        """
    ).fetchall()
    return [
        ProjectTask(
            project_name=str(row["project_name"]),
            task_title=(None if row["task_title"] is None else str(row["task_title"])),
        )
        for row in rows
    ]


def summarize_projects(
    connection: sqlite3.Connection,
    minimum_task_count: int,
) -> list[ProjectSummary]:
    rows = connection.execute(
        """
        SELECT
            projects.name AS project_name,
            COUNT(tasks.id) AS task_count,
            SUM(CASE WHEN tasks.done = 1 THEN 1 ELSE 0 END) AS completed_count
        FROM projects
        LEFT JOIN tasks ON tasks.project_id = projects.id
        GROUP BY projects.id, projects.name
        HAVING COUNT(tasks.id) >= ?
        ORDER BY projects.id
        """,
        (minimum_task_count,),
    ).fetchall()
    return [
        ProjectSummary(
            project_name=str(row["project_name"]),
            task_count=int(row["task_count"]),
            completed_count=int(row["completed_count"]),
        )
        for row in rows
    ]


def add_lookup_index(connection: sqlite3.Connection) -> None:
    # CREATE INDEX is widely available, but index kinds, syntax, and usefulness
    # vary. Indexes speed some reads while adding storage and write costs.
    connection.execute(
        "CREATE INDEX idx_tasks_project_done ON tasks (project_id, done)"
    )


def explain_open_task_lookup(
    connection: sqlite3.Connection,
    project_id: int,
) -> list[str]:
    # EXPLAIN QUERY PLAN and its output are SQLite-specific. Treat the details
    # as orientation, not as a portable or stable application interface.
    rows = connection.execute(
        """
        EXPLAIN QUERY PLAN
        SELECT id, title
        FROM tasks
        WHERE project_id = ? AND done = 0
        """,
        (project_id,),
    ).fetchall()
    return [str(row["detail"]) for row in rows]


if __name__ == "__main__":
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)
        seed_data(database)

        print("INNER JOIN:", list_tasks_with_projects(database))
        print("LEFT JOIN:", list_projects_with_optional_tasks(database))
        print("GROUP BY:", summarize_projects(database, minimum_task_count=1))

        add_lookup_index(database)
        plan = explain_open_task_lookup(database, project_id=1)
        assert plan and all(plan)
        print("SQLite query plan available:", bool(plan))
