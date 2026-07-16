"""SQLite implementation of the shared Task repository contract."""

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import TypeAlias

from ..domain import CreateTaskInput, Task, UnsetType, UpdateTaskInput
from ..errors import StorageError, TaskNotFoundError, ValidationError

_Row: TypeAlias = tuple[object, object, object]

# AUTOINCREMENT prevents reuse of previously committed generated IDs after
# deletion. Generated IDs remain increasing, but gaps are still possible.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
)
"""

_SELECT_COLUMNS = "SELECT id, title, completed FROM tasks"


class SQLiteTaskRepository:
    """Task repository using one short-lived SQLite connection per operation.

    ``closing`` deterministically closes each connection. For writes, the
    connection's own context manager additionally commits on normal exit or
    rolls back when the block raises; it does not itself close the connection.
    """

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize_schema(self) -> None:
        try:
            with closing(self._connect()) as connection, connection:
                connection.execute(_SCHEMA)
        except (sqlite3.Error, OSError, UnicodeError) as error:
            raise self._storage_error("initialize", error) from error

    @staticmethod
    def _storage_error(operation: str, error: BaseException) -> StorageError:
        return StorageError(
            f"SQLite {operation} failed: {error}",
            operation=operation,
        )

    @staticmethod
    def _map_row(row: _Row, *, operation: str) -> Task:
        task_id, title, completed = row
        # Treat persisted data as an untrusted boundary: first verify SQLite's
        # exact representation, then let Task enforce the domain invariants.
        if (
            type(task_id) is not int
            or not isinstance(title, str)
            or type(completed) is not int
            or completed not in (0, 1)
        ):
            raise StorageError(
                f"SQLite {operation} returned an invalid task row",
                operation=operation,
            )
        try:
            return Task(task_id, title, bool(completed))
        except ValidationError as error:
            raise StorageError(
                f"SQLite {operation} returned an invalid task row: {error}",
                operation=operation,
            ) from error

    def _get_with_connection(
        self,
        connection: sqlite3.Connection,
        task_id: int,
        *,
        operation: str,
    ) -> Task:
        # SQL structure is fixed by this module, while caller-derived values
        # are bound separately so they cannot be interpreted as SQL syntax.
        row = connection.execute(
            f"{_SELECT_COLUMNS} WHERE id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return self._map_row(row, operation=operation)

    def create(self, task: CreateTaskInput) -> Task:
        operation = "create"
        try:
            with closing(self._connect()) as connection, connection:
                cursor = connection.execute(
                    "INSERT INTO tasks (title, completed) VALUES (?, ?)",
                    (task.title, 0),
                )
                # lastrowid belongs to this insert cursor and identifies the
                # row allocated by SQLite without a second "maximum ID" query.
                task_id = cursor.lastrowid
                if task_id is None:
                    raise StorageError(
                        "SQLite create did not allocate a task ID",
                        operation=operation,
                    )
                return self._get_with_connection(
                    connection,
                    task_id,
                    operation=operation,
                )
        except StorageError:
            raise
        except (sqlite3.Error, OSError, UnicodeError) as error:
            raise self._storage_error(operation, error) from error

    def list(self, completed: bool | None = None) -> list[Task]:
        operation = "list"
        try:
            with closing(self._connect()) as connection:
                if completed is None:
                    rows = connection.execute(
                        f"{_SELECT_COLUMNS} ORDER BY id"
                    ).fetchall()
                else:
                    rows = connection.execute(
                        f"{_SELECT_COLUMNS} WHERE completed = ? ORDER BY id",
                        (int(completed),),
                    ).fetchall()
                return [self._map_row(row, operation=operation) for row in rows]
        except StorageError:
            raise
        except (sqlite3.Error, OSError, UnicodeError) as error:
            raise self._storage_error(operation, error) from error

    def get(self, task_id: int) -> Task:
        operation = "get"
        try:
            with closing(self._connect()) as connection:
                return self._get_with_connection(
                    connection,
                    task_id,
                    operation=operation,
                )
        except (StorageError, TaskNotFoundError):
            raise
        except (sqlite3.Error, OSError, UnicodeError) as error:
            raise self._storage_error(operation, error) from error

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        operation = "update"
        try:
            with closing(self._connect()) as connection, connection:
                # The initial SELECT precedes sqlite3's implicit write
                # transaction. UPDATE and the verification read commit or roll
                # back together; serializing the entire read-modify-write cycle
                # would require beginning a transaction before this SELECT.
                current = self._get_with_connection(
                    connection,
                    task_id,
                    operation=operation,
                )
                title = (
                    current.title
                    if isinstance(update.title, UnsetType)
                    else update.title
                )
                completed = (
                    current.completed
                    if isinstance(update.completed, UnsetType)
                    else update.completed
                )
                connection.execute(
                    """
                    UPDATE tasks
                    SET title = ?, completed = ?
                    WHERE id = ?
                    """,
                    (title, int(completed), task_id),
                )
                return self._get_with_connection(
                    connection,
                    task_id,
                    operation=operation,
                )
        except (StorageError, TaskNotFoundError):
            raise
        except (sqlite3.Error, OSError, UnicodeError) as error:
            raise self._storage_error(operation, error) from error

    def delete(self, task_id: int) -> None:
        operation = "delete"
        try:
            with closing(self._connect()) as connection, connection:
                cursor = connection.execute(
                    "DELETE FROM tasks WHERE id = ?",
                    (task_id,),
                )
                if cursor.rowcount == 0:
                    raise TaskNotFoundError(task_id)
        except TaskNotFoundError:
            raise
        except (sqlite3.Error, OSError, UnicodeError) as error:
            raise self._storage_error(operation, error) from error


__all__ = ["SQLiteTaskRepository"]
