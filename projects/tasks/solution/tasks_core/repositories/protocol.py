"""Narrow repository capability used by the application service."""

from typing import Protocol, runtime_checkable

from ..domain import CreateTaskInput, Task, UpdateTaskInput


@runtime_checkable
class TaskRepository(Protocol):
    """Persistence contract consumed by the framework-neutral service.

    Missing single-task operations raise ``TaskNotFoundError`` rather than
    returning ``None``, so every successful result is a complete ``Task``.
    Repository-assigned IDs increase monotonically and are not recycled after
    deletion; gaps are allowed.
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
        """Apply all supplied fields atomically or leave the task unchanged."""

        ...

    def delete(self, task_id: int) -> None:
        """Atomically remove one task."""

        ...


__all__ = ["TaskRepository"]
