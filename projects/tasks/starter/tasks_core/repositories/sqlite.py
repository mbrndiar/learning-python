"""SQLite repository scaffold for milestone two."""

from pathlib import Path

from ..domain import CreateTaskInput, Task, UpdateTaskInput
from ..errors import incomplete


class SQLiteTaskRepository:
    """Task repository backed by one SQLite database.

    Use short-lived connections so each operation clearly owns its transaction
    and cleanup rather than relying on process-global connection state.
    """

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        # TODO(milestone 2): initialize the checked AUTOINCREMENT schema once.
        # CREATE TABLE IF NOT EXISTS makes startup repeatable; CHECK keeps stored
        # completion values within SQLite's integer representation of bool.

    def create(self, task: CreateTaskInput) -> Task:
        # TODO(milestone 2): use one connection and transaction for this insert.
        # Keep parameter values separate from SQL text, verify lastrowid, and
        # return the row as mapped storage data rather than reconstructing it.
        incomplete(f"milestone 2 SQLite create in {self.database_path}: {task!r}")

    def list(self, completed: bool | None = None) -> list[Task]:
        # TODO(milestone 2): select explicit columns ordered by ID.
        # Apply the completed predicate only when requested, and validate every
        # row while converting SQLite integers back to domain values.
        incomplete(
            f"milestone 2 SQLite list in {self.database_path}: completed={completed!r}"
        )

    def get(self, task_id: int) -> Task:
        # TODO(milestone 2): translate a missing row to TaskNotFoundError.
        # The protocol uses one exception path for both persistence adapters;
        # returning None here would leak a storage-specific API into the service.
        incomplete(f"milestone 2 SQLite get in {self.database_path}: {task_id}")

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        # TODO(milestone 2): preserve omitted fields in one atomic transaction.
        # Under sqlite3's default transaction control, a SELECT alone does not
        # start the write transaction. Serializing the complete read-modify-write
        # cycle therefore requires an explicit transaction before that read.
        incomplete(
            f"milestone 2 SQLite update in {self.database_path}: "
            f"{task_id}, update={update!r}"
        )

    def delete(self, task_id: int) -> None:
        # TODO(milestone 2): do not reset or reuse SQLite's ID sequence.
        # Check the affected-row count for not-found, but leave sqlite_sequence
        # alone so deleting a task never makes its public ID available again.
        incomplete(f"milestone 2 SQLite delete in {self.database_path}: {task_id}")


__all__ = ["SQLiteTaskRepository"]
