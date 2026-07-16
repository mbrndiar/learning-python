"""SQLite repository scaffold for milestone two."""

from pathlib import Path

from ..domain import CreateTaskInput, Task, UpdateTaskInput
from ..errors import incomplete


class SQLiteTaskRepository:
    """Task repository backed by one SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        # TODO(milestone 2): initialize the checked AUTOINCREMENT schema once.

    def create(self, task: CreateTaskInput) -> Task:
        # TODO(milestone 2): use one connection and transaction for this insert.
        incomplete(f"milestone 2 SQLite create in {self.database_path}: {task!r}")

    def list(self, completed: bool | None = None) -> list[Task]:
        # TODO(milestone 2): map explicit columns ordered by ID.
        incomplete(
            f"milestone 2 SQLite list in {self.database_path}: completed={completed!r}"
        )

    def get(self, task_id: int) -> Task:
        # TODO(milestone 2): translate a missing row to TaskNotFoundError.
        incomplete(f"milestone 2 SQLite get in {self.database_path}: {task_id}")

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        # TODO(milestone 2): preserve omitted fields in one atomic transaction.
        incomplete(
            f"milestone 2 SQLite update in {self.database_path}: "
            f"{task_id}, update={update!r}"
        )

    def delete(self, task_id: int) -> None:
        # TODO(milestone 2): do not reset or reuse SQLite's ID sequence.
        incomplete(f"milestone 2 SQLite delete in {self.database_path}: {task_id}")


__all__ = ["SQLiteTaskRepository"]
