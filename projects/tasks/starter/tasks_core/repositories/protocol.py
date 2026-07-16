"""Narrow repository capability used by the application service."""

from typing import Protocol, runtime_checkable

from ..domain import CreateTaskInput, Task, UpdateTaskInput


@runtime_checkable
class TaskRepository(Protocol):
    """Storage capability consumed by the service without a concrete base class.

    Structural typing lets SQLite and Markdown remain independent adapters while
    the service depends only on their shared observable behavior.
    """

    def create(self, task: CreateTaskInput) -> Task:
        """Persist a new incomplete task."""

        ...

    def list(self, completed: bool | None = None) -> list[Task]:
        """Return tasks ordered by identifier."""

        ...

    def get(self, task_id: int) -> Task:
        """Return one task or raise the domain not-found error."""

        ...

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        """Atomically apply a partial update.

        The caller must observe either the complete new Task or an exception,
        never a partially persisted combination of fields.
        """

        ...

    def delete(self, task_id: int) -> None:
        """Atomically remove one task without making its identifier reusable."""

        ...


__all__ = ["TaskRepository"]
