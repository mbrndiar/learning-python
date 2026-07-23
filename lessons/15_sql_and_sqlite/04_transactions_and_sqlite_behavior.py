"""
Chapter 15, Lesson 4: Transactions and SQLite Behavior

Purpose: make several writes atomic, compare explicit commit/rollback with the
Connection transaction context manager, and separate portable transaction
ideas from SQLite-specific affinity, generated IDs, pragmas, and concurrency.

Prerequisite: Lessons 1-3.

Run from the repository root:

    python lessons/15_sql_and_sqlite/04_transactions_and_sqlite_behavior.py
"""

import sqlite3
from contextlib import closing


def create_schema(connection: sqlite3.Connection) -> None:
    # Foreign-key enforcement must be configured before any transaction. This
    # schema has no foreign key, but the fixed placement demonstrates the
    # connection-level rule used by real relational schemas.
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        BEGIN;
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE reusable_ids (
            id INTEGER PRIMARY KEY,
            label TEXT NOT NULL
        );

        CREATE TABLE never_reuse_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL
        );

        CREATE TABLE affinity_examples (
            value INTEGER
        );
        COMMIT;
        """
    )


def add_task(connection: sqlite3.Connection, title: str) -> int:
    cursor = connection.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,),
    )
    connection.commit()
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not generate a task ID")
    return cursor.lastrowid


# Step 1: explicit control is verbose but makes every transition visible.
def add_pair_with_explicit_control(
    connection: sqlite3.Connection,
    first_title: str,
    second_title: str,
) -> None:
    """Commit both inserts, or roll both back and re-raise the database error."""
    try:
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (first_title,),
        )
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (second_title,),
        )
    except sqlite3.Error:
        connection.rollback()
        raise
    else:
        connection.commit()


# Step 2: the Connection context manager expresses the same transaction end.
# It commits on normal exit and rolls back when an exception escapes. It does
# not open a transaction by itself and does not close the connection.
def add_pair_with_context(
    connection: sqlite3.Connection,
    first_title: str,
    second_title: str,
) -> None:
    """Commit both inserts, or roll both back when one statement fails."""
    with connection:
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (first_title,),
        )
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (second_title,),
        )


def task_exists(connection: sqlite3.Connection, title: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM tasks WHERE title = ?",
        (title,),
    ).fetchone()
    return row is not None


# Step 3: SQLite applies a column's affinity when possible, but the storage
# class belongs to each value. INTEGER affinity converts "42" to integer and
# can still store text that cannot be converted.
def demonstrate_type_affinity(
    connection: sqlite3.Connection,
) -> list[tuple[str, object]]:
    connection.executemany(
        "INSERT INTO affinity_examples (value) VALUES (?)",
        [("42",), ("forty-two",)],
    )
    connection.commit()
    rows = connection.execute(
        """
        SELECT typeof(value) AS storage_class, value
        FROM affinity_examples
        ORDER BY rowid
        """
    ).fetchall()
    return [(str(row["storage_class"]), row["value"]) for row in rows]


# Step 4: INTEGER PRIMARY KEY already generates rowids. AUTOINCREMENT is an
# extra rule that prevents reuse of deleted rowids and adds overhead; it does
# not mean IDs have no gaps.
def demonstrate_id_reuse(connection: sqlite3.Connection) -> tuple[int, int]:
    with connection:
        connection.execute("INSERT INTO reusable_ids (label) VALUES ('first')")
        reusable_max = connection.execute(
            "INSERT INTO reusable_ids (label) VALUES ('second')"
        )
        connection.execute(
            "DELETE FROM reusable_ids WHERE id = ?",
            (reusable_max.lastrowid,),
        )
        reused = connection.execute("INSERT INTO reusable_ids (label) VALUES ('third')")

        connection.execute("INSERT INTO never_reuse_ids (label) VALUES ('first')")
        monotonic_max = connection.execute(
            "INSERT INTO never_reuse_ids (label) VALUES ('second')"
        )
        connection.execute(
            "DELETE FROM never_reuse_ids WHERE id = ?",
            (monotonic_max.lastrowid,),
        )
        not_reused = connection.execute(
            "INSERT INTO never_reuse_ids (label) VALUES ('third')"
        )

    if reused.lastrowid is None or not_reused.lastrowid is None:
        raise RuntimeError("SQLite did not generate an ID")
    return reused.lastrowid, not_reused.lastrowid


if __name__ == "__main__":
    with closing(sqlite3.connect(":memory:", timeout=1.0)) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)
        assert add_task(database, "Existing title") == 1

        try:
            add_pair_with_explicit_control(
                database,
                "Explicit rollback",
                "Existing title",
            )
        except sqlite3.IntegrityError:
            pass
        assert not task_exists(database, "Explicit rollback")

        try:
            add_pair_with_context(
                database,
                "Context rollback",
                "Existing title",
            )
        except sqlite3.IntegrityError:
            pass
        assert not task_exists(database, "Context rollback")

        affinity = demonstrate_type_affinity(database)
        generated_ids = demonstrate_id_reuse(database)
        assert affinity == [("integer", 42), ("text", "forty-two")]
        assert generated_ids == (2, 3)

        # A normal transaction-context exit commits, but database remains open
        # and usable afterward. closing() at the outer boundary owns close().
        with database:
            database.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                ("Connection is still open",),
            )
        assert task_exists(database, "Connection is still open")

        print("explicit and context-manager rollbacks were atomic")
        print("affinity:", affinity)
        print("generated IDs (reused, AUTOINCREMENT):", generated_ids)
        print("connection remained open after 'with database:'")
        print(
            "concurrency boundary: multiple readers, one writer; "
            f"this build reports sqlite3.threadsafety={sqlite3.threadsafety}"
        )
