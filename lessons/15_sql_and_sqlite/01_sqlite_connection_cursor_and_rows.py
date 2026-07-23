"""
Chapter 15, Lesson 1: Connection, Cursor, and Rows

Purpose: learn Python's sqlite3 lifecycle before adding relational complexity.
The code that opens a Connection owns closing it. Connection shortcut methods
create and return Cursor objects; cursors expose generated IDs, affected-row
counts, and fetched rows.

Prerequisites: Chapter 7 resource ownership and Chapter 8 dataclasses.

Run from the repository root:

    python lessons/15_sql_and_sqlite/01_sqlite_connection_cursor_and_rows.py
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    """An application value mapped from one storage row."""

    id: int
    body: str


# Step 1: executescript() is for several semicolon-separated statements.
# In Python 3.11 it commits any pending transaction before running the script,
# so setup code uses it before DML and puts its own BEGIN/COMMIT in the script.
def create_schema(connection: sqlite3.Connection) -> None:
    """Create the lesson's table."""
    connection.executescript(
        """
        BEGIN;
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            body TEXT NOT NULL CHECK (body <> '')
        );
        COMMIT;
        """
    )


# Step 2: one execute() returns the Cursor that ran the statement.
# lastrowid belongs to a successful single INSERT through execute().
def add_note(connection: sqlite3.Connection, body: str) -> int:
    """Insert one note, commit it, and return its generated SQLite ID."""
    with connection:
        cursor = connection.execute(
            "INSERT INTO notes (body) VALUES (?)",
            (body,),
        )
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite did not generate a note ID")
    return cursor.lastrowid


# Step 3: executemany() repeats one parameterized DML statement. It returns a
# Cursor too, but its lastrowid is not updated; use it for batching, not for
# collecting generated IDs.
def add_notes(connection: sqlite3.Connection, bodies: list[str]) -> int:
    """Insert several notes and return the number of affected rows."""
    with connection:
        cursor = connection.executemany(
            "INSERT INTO notes (body) VALUES (?)",
            [(body,) for body in bodies],
        )
    return cursor.rowcount


def row_to_note(row: sqlite3.Row) -> Note:
    """Translate driver storage values at one application boundary."""
    return Note(id=int(row["id"]), body=str(row["body"]))


# Step 4: fetchone() returns one row or None when no row remains.
def find_note(connection: sqlite3.Connection, note_id: int) -> Note | None:
    """Return one note by ID, or None when it does not exist."""
    row = connection.execute(
        "SELECT id, body FROM notes WHERE id = ?",
        (note_id,),
    ).fetchone()
    return None if row is None else row_to_note(row)


# Step 5: fetchall() returns every remaining row as a list. ORDER BY makes the
# caller-visible order an explicit part of the query.
def list_notes(connection: sqlite3.Connection) -> list[Note]:
    """Return every note in stable ID order."""
    rows = connection.execute("SELECT id, body FROM notes ORDER BY id").fetchall()
    return [row_to_note(row) for row in rows]


if __name__ == "__main__":
    # :memory: creates a database private to this connection. closing() calls
    # close() at block exit; the Connection transaction context manager shown
    # later in this chapter does not close resources.
    with closing(sqlite3.connect(":memory:")) as database:
        # Set row_factory before creating cursors so all result rows support
        # readable name access as well as positional access.
        database.row_factory = sqlite3.Row
        create_schema(database)

        first_id = add_note(database, "Own the connection")
        inserted = add_notes(database, ["Observe the cursor", "Map each row"])

        try:
            add_notes(database, ["Must roll back", ""])
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("the empty body should violate the schema")
        assert database.in_transaction is False

        first = find_note(database, first_id)
        missing = find_note(database, 999)
        all_notes = list_notes(database)

        assert first == Note(1, "Own the connection")
        assert missing is None
        assert inserted == 2
        assert all_notes == [
            Note(1, "Own the connection"),
            Note(2, "Observe the cursor"),
            Note(3, "Map each row"),
        ]

        print("fetchone:", first)
        print("fetchall:", all_notes)
        print("executemany rowcount:", inserted)
