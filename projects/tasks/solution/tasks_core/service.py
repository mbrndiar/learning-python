"""Application service boundary shared by all HTTP adapters."""

from .domain import Task
from .errors import incomplete
from .repositories.protocol import TaskRepository


class TaskService:
    """Coordinate validation and repository operations."""

    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create_task(self, title: object) -> Task:
        """Create one incomplete task."""

        incomplete(f"milestone 1 task creation for {title!r}")

    def list_tasks(self, completed: object | None = None) -> list[Task]:
        """List tasks, optionally filtered by completion state."""

        incomplete(f"milestone 1 task listing for {completed!r}")

    def get_task(self, task_id: object) -> Task:
        """Return one task by identifier."""

        incomplete(f"milestone 1 task lookup for {task_id!r}")

    def update_task(
        self,
        task_id: object,
        *,
        title: object | None = None,
        completed: object | None = None,
    ) -> Task:
        """Apply a partial task update."""

        incomplete(
            "milestone 1 task update "
            f"for {task_id!r}, title={title!r}, completed={completed!r}"
        )

    def delete_task(self, task_id: object) -> None:
        """Delete one task by identifier."""

        incomplete(f"milestone 1 task deletion for {task_id!r}")


__all__ = ["TaskService"]
