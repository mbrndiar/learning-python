"""Narrow repository capability used by the application service."""

from typing import Protocol, runtime_checkable

from ..domain import Task


@runtime_checkable
class TaskRepository(Protocol):
    """Create, query, mutate, and delete Task values."""

    def create(self, title: str) -> Task:
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
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        """Atomically apply a partial update."""

        ...

    def delete(self, task_id: int) -> None:
        """Atomically remove one task."""

        ...


__all__ = ["TaskRepository"]
