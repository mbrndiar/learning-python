"""
Shared teaching domain for Chapter 17's Flask and FastAPI adapters.

This support module deliberately imports no web framework. Both adapters call
the same service and repository protocol so framework differences remain at the
HTTP boundary.
"""

import unicodedata
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


class DomainError(Exception):
    code = "internal_error"
    status = 500

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(DomainError):
    code = "validation_error"
    status = 422


class NotFoundError(DomainError):
    code = "not_found"
    status = 404


class TaskRepository(Protocol):
    def create(self, title: str) -> Task:
        """Store and return one incomplete task."""

    def list(self, completed: bool | None = None) -> list[Task]:
        """Return tasks in ID order, optionally filtered."""

    def get(self, task_id: int) -> Task | None:
        """Return one task, or None."""


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def create(self, title: str) -> Task:
        task = Task(len(self._tasks) + 1, title, False)
        self._tasks.append(task)
        return task

    def list(self, completed: bool | None = None) -> list[Task]:
        return [
            task
            for task in self._tasks
            if completed is None or task.completed is completed
        ]

    def get(self, task_id: int) -> Task | None:
        return next((task for task in self._tasks if task.id == task_id), None)


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create(self, title: str) -> Task:
        normalized = title.strip()
        if not 1 <= len(normalized) <= 120:
            raise ValidationError(
                "title must contain between 1 and 120 characters",
                details={"field": "title"},
            )
        if any(unicodedata.category(character) == "Cc" for character in normalized):
            raise ValidationError(
                "title must not contain control characters",
                details={"field": "title"},
            )
        return self._repository.create(normalized)

    def list(self, completed: bool | None = None) -> list[Task]:
        return self._repository.list(completed)

    def get(self, task_id: int) -> Task:
        if task_id <= 0:
            raise ValidationError(
                "task ID must be positive",
                details={"field": "task_id"},
            )
        task = self._repository.get(task_id)
        if task is None:
            raise NotFoundError(f"task {task_id} was not found")
        return task


def error_body(error: DomainError) -> dict[str, object]:
    details: dict[str, object] = {
        "code": error.code,
        "message": error.message,
    }
    if error.details is not None:
        details["details"] = error.details
    return {"error": details}
