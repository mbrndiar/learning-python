"""
Lesson 10.3: Transactions and SQLite

Transactions make a group of statements succeed or fail together. This lesson
also separates portable transaction ideas from SQLite's generated IDs, dynamic
typing, pragmas, and AUTOINCREMENT behavior.
"""

import sqlite3
from contextlib import closing


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
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
        """
    )


def add_task(connection: sqlite3.Connection, title: str) -> int:
    # Generated-key syntax and retrieval differ across engines. In SQLite,
    # INTEGER PRIMARY KEY is an alias for the rowid and lastrowid reports it.
    with connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not generate an ID")
        return cursor.lastrowid


def add_pair_atomically(
    connection: sqlite3.Connection,
    first_title: str,
    second_title: str,
) -> None:
    # Exiting normally commits. If either statement raises, __exit__ rolls the
    # transaction back. The connection stays open because it is a resource too.
    with connection:
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (first_title,),
        )
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (second_title,),
        )


def demonstrate_id_reuse(connection: sqlite3.Connection) -> tuple[int, int]:
    with connection:
        connection.execute("INSERT INTO reusable_ids (label) VALUES ('first')")
        reusable = connection.execute(
            "INSERT INTO reusable_ids (label) VALUES ('second')"
        )
        connection.execute(
            "DELETE FROM reusable_ids WHERE id = ?",
            (reusable.lastrowid,),
        )
        reused = connection.execute("INSERT INTO reusable_ids (label) VALUES ('third')")

        connection.execute("INSERT INTO never_reuse_ids (label) VALUES ('first')")
        monotonic = connection.execute(
            "INSERT INTO never_reuse_ids (label) VALUES ('second')"
        )
        connection.execute(
            "DELETE FROM never_reuse_ids WHERE id = ?",
            (monotonic.lastrowid,),
        )
        not_reused = connection.execute(
            "INSERT INTO never_reuse_ids (label) VALUES ('third')"
        )

    if reused.lastrowid is None or not_reused.lastrowid is None:
        raise RuntimeError("SQLite did not generate an ID")
    return reused.lastrowid, not_reused.lastrowid


def demonstrate_type_affinity(
    connection: sqlite3.Connection,
) -> list[tuple[str, object]]:
    # SQLite columns have type affinity rather than the rigid column typing used
    # by many server databases. Constraints remain important at the boundary.
    with connection:
        connection.executemany(
            "INSERT INTO affinity_examples (value) VALUES (?)",
            [("42",), ("forty-two",)],
        )
    rows = connection.execute(
        """
        SELECT typeof(value) AS storage_class, value
        FROM affinity_examples
        ORDER BY rowid
        """
    ).fetchall()
    return [(str(row["storage_class"]), row["value"]) for row in rows]


def read_pragmas(connection: sqlite3.Connection) -> tuple[int, int, str]:
    # PRAGMA is SQLite-specific and cannot generally be parameterized. Use fixed
    # statements, not text assembled from untrusted input.
    connection.execute("PRAGMA user_version = 1")
    foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    journal_mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0])
    return foreign_keys, user_version, journal_mode


if __name__ == "__main__":
    # closing() owns the connection lifetime. Nested "with database" blocks own
    # transactions only; they do not close the connection.
    with closing(sqlite3.connect(":memory:")) as database:
        database.row_factory = sqlite3.Row
        create_schema(database)

        assert add_task(database, "Existing title") == 1
        try:
            add_pair_atomically(database, "Should roll back", "Existing title")
        except sqlite3.IntegrityError:
            pass

        rolled_back_count = database.execute(
            "SELECT COUNT(*) FROM tasks WHERE title = ?",
            ("Should roll back",),
        ).fetchone()[0]
        assert rolled_back_count == 0
        print("Atomic rollback preserved the original state")

        assert demonstrate_id_reuse(database) == (2, 3)
        print("AUTOINCREMENT prevented reuse of a deleted maximum ID")

        assert demonstrate_type_affinity(database) == [
            ("integer", 42),
            ("text", "forty-two"),
        ]
        print("SQLite affinity can store more than one storage class")

        foreign_keys, user_version, journal_mode = read_pragmas(database)
        assert (foreign_keys, user_version) == (1, 1)
        assert journal_mode
        print("SQLite pragmas inspected with fixed statements")
