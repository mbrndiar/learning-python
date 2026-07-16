"""Application service boundary shared by all HTTP adapters."""

from .domain import UNSET, Task
from .errors import incomplete
from .repositories.protocol import TaskRepository


class TaskService:
    """Coordinate validation and repository operations."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(self, title: object) -> Task:
        """Create one incomplete task."""

        # TODO(milestone 1): normalize the title, then delegate to create.
        incomplete(f"milestone 1 task creation for {title!r}")

    def list_tasks(self, completed: object | None = None) -> list[Task]:
        """List tasks, optionally filtered by completion state."""

        # TODO(milestone 1): validate the optional strict Boolean filter.
        incomplete(f"milestone 1 task listing for {completed!r}")

    def get_task(self, task_id: object) -> Task:
        """Return one task by identifier."""

        # TODO(milestone 1): validate the ID before repository access.
        incomplete(f"milestone 1 task lookup for {task_id!r}")

    def update_task(
        self,
        task_id: object,
        *,
        title: object = UNSET,
        completed: object = UNSET,
    ) -> Task:
        """Apply a partial task update."""

        # TODO(milestone 1): keep omitted fields distinct from explicit False.
        incomplete(
            "milestone 1 task update "
            f"for {task_id!r}, title={title!r}, completed={completed!r}"
        )

    def delete_task(self, task_id: object) -> None:
        """Delete one task by identifier."""

        # TODO(milestone 1): validate the ID before repository access.
        incomplete(f"milestone 1 task deletion for {task_id!r}")


__all__ = ["TaskService"]
