"""SQLite repository scaffold for milestone two."""

from pathlib import Path

from ..domain import CreateTaskInput, Task, UpdateTaskInput
from ..errors import incomplete


class SQLiteTaskRepository:
    """Task repository backed by one SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def create(self, task: CreateTaskInput) -> Task:
        incomplete(f"milestone 2 SQLite create in {self.database_path}: {task!r}")

    def list(self, completed: bool | None = None) -> list[Task]:
        incomplete(
            f"milestone 2 SQLite list in {self.database_path}: completed={completed!r}"
        )

    def get(self, task_id: int) -> Task:
        incomplete(f"milestone 2 SQLite get in {self.database_path}: {task_id}")

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        incomplete(
            f"milestone 2 SQLite update in {self.database_path}: "
            f"{task_id}, update={update!r}"
        )

    def delete(self, task_id: int) -> None:
        incomplete(f"milestone 2 SQLite delete in {self.database_path}: {task_id}")


__all__ = ["SQLiteTaskRepository"]
