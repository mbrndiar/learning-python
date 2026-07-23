"""
Chapter 15, Lesson 3: Joins, Aggregates, Indexes, and Plans

Purpose: combine related rows, summarize groups, add an index for a concrete
lookup, and inspect SQLite's query plan without treating optimizer output as a
stable application API.

Prerequisite: Lesson 2's constrained projects/tasks schema and CRUD operations.

Run from the repository root:

    python lessons/15_sql_and_sqlite/03_joins_aggregates_indexes_and_plans.py
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
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        BEGIN;
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
        COMMIT;
        """
    )


def seed_data(connection: sqlite3.Connection) -> None:
    """Insert deterministic related data with two batched statements."""
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
    connection.commit()


# Step 1: INNER JOIN keeps only rows whose project_id matches a project.
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


# Step 2: LEFT JOIN preserves every project. The empty project receives one
# joined result row whose right-side task_title is NULL, mapped to Python None.
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
            task_title=None if row["task_title"] is None else str(row["task_title"]),
        )
        for row in rows
    ]


# Step 3: WHERE would filter rows before grouping. HAVING filters the completed
# groups, and its threshold is still passed as a value parameter.
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


# Step 4: this index matches the equality lookup's project_id/done prefix.
# It can speed selected reads, but every write must maintain it.
def add_open_task_lookup_index(connection: sqlite3.Connection) -> None:
    connection.execute(
        "CREATE INDEX idx_tasks_project_done ON tasks (project_id, done)"
    )
    connection.commit()


def list_index_names(connection: sqlite3.Connection) -> list[str]:
    """Inspect schema state instead of inferring it from a chosen query plan."""
    rows = connection.execute("PRAGMA index_list('tasks')").fetchall()
    return [str(row["name"]) for row in rows]


# Step 5: EXPLAIN QUERY PLAN is a SQLite debugging aid. Its rows and wording can
# change across SQLite versions, so return details for inspection but do not
# make application behavior depend on exact text.
def explain_open_task_lookup(
    connection: sqlite3.Connection,
    project_id: int,
) -> list[str]:
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

        inner_rows = list_tasks_with_projects(database)
        left_rows = list_projects_with_optional_tasks(database)
        summaries = summarize_projects(database, minimum_task_count=1)

        assert inner_rows == [
            TaskProject("Read SQL lesson", "Course"),
            TaskProject("Practice joins", "Course"),
            TaskProject("Plant herbs", "Garden"),
        ]
        assert left_rows[-1] == ProjectTask("Empty project", None)
        assert summaries == [
            ProjectSummary("Course", 2, 1),
            ProjectSummary("Garden", 1, 0),
        ]

        add_open_task_lookup_index(database)
        assert "idx_tasks_project_done" in list_index_names(database)
        plan = explain_open_task_lookup(database, project_id=1)
        assert plan and all(plan)

        print("INNER JOIN:", inner_rows)
        print("LEFT JOIN:", left_rows)
        print("GROUP BY/HAVING:", summaries)
        print("query-plan details (version-dependent):", plan)
