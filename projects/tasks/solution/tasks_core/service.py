"""Application service boundary shared by all HTTP adapters."""

from .domain import (
    UNSET,
    Task,
    normalize_create_input,
    normalize_update_input,
    validate_completed_filter,
    validate_task_id,
)
from .repositories.protocol import TaskRepository


class TaskService:
    """Validate boundary values and delegate domain operations."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(self, title: object) -> Task:
        """Create one incomplete task."""

        return self._repository.create(normalize_create_input(title))

    def list_tasks(self, completed: object | None = None) -> list[Task]:
        """List tasks, optionally filtered by completion state."""

        return self._repository.list(validate_completed_filter(completed))

    def get_task(self, task_id: object) -> Task:
        """Return one task by identifier."""

        return self._repository.get(validate_task_id(task_id))

    def update_task(
        self,
        task_id: object,
        *,
        title: object = UNSET,
        completed: object = UNSET,
    ) -> Task:
        """Apply a partial task update."""

        normalized_id = validate_task_id(task_id)
        update = normalize_update_input(title=title, completed=completed)
        return self._repository.update(normalized_id, update)

    def delete_task(self, task_id: object) -> None:
        """Delete one task by identifier."""

        self._repository.delete(validate_task_id(task_id))


__all__ = ["TaskService"]
