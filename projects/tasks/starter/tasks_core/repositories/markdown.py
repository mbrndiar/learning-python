"""Versioned Markdown repository scaffold for milestone two."""

from pathlib import Path

from ..domain import CreateTaskInput, Task, UpdateTaskInput
from ..errors import incomplete


class MarkdownTaskRepository:
    """Task repository backed by one versioned Markdown checklist."""

    def __init__(self, document_path: str | Path) -> None:
        self.document_path = Path(document_path)
        # TODO(milestone 2): share an in-process lock for this storage path.

    def create(self, task: CreateTaskInput) -> Task:
        # TODO(milestone 2): lock, strictly load, allocate next-id, and atomically save.
        incomplete(f"milestone 2 Markdown create in {self.document_path}: {task!r}")

    def list(self, completed: bool | None = None) -> list[Task]:
        # TODO(milestone 2): validate metadata and every checklist row.
        incomplete(
            "milestone 2 Markdown list in "
            f"{self.document_path}: completed={completed!r}"
        )

    def get(self, task_id: int) -> Task:
        # TODO(milestone 2): reject malformed data before searching for the ID.
        incomplete(f"milestone 2 Markdown get in {self.document_path}: {task_id}")

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        # TODO(milestone 2): perform one locked load-modify-save operation.
        incomplete(
            f"milestone 2 Markdown update in {self.document_path}: "
            f"{task_id}, update={update!r}"
        )

    def delete(self, task_id: int) -> None:
        # TODO(milestone 2): retain next-id while publishing a complete sibling file.
        incomplete(f"milestone 2 Markdown delete in {self.document_path}: {task_id}")


__all__ = ["MarkdownTaskRepository"]
