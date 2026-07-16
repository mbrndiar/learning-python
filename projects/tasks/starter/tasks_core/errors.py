"""Stable domain errors and intentional learning placeholders."""

from collections.abc import Mapping
from typing import Literal, NoReturn, TypeAlias

ErrorCode: TypeAlias = Literal[
    "validation_error",
    "not_found",
    "internal_error",
]


class TaskError(Exception):
    """Expected application failure safe to translate at a boundary."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Mapping[str, object] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        # Shallow-copy the top-level mapping so later key changes cannot alter an
        # error already crossing a boundary; nested mutable values remain shared.
        self.details = dict(details or {})
        super().__init__(message)


class ValidationError(TaskError):
    """A request or domain value violates the Task contract."""

    def __init__(self, message: str, *, field: str) -> None:
        self.field = field
        super().__init__(
            "validation_error",
            message,
            {"field": field},
        )


class TaskNotFoundError(TaskError):
    """A valid task identifier does not exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__("not_found", f"task {task_id} was not found")


class StorageError(TaskError):
    """Persistence could not safely complete an operation."""

    def __init__(self, message: str, *, operation: str | None = None) -> None:
        self.operation = operation
        details: dict[str, object] = {}
        if operation is not None:
            details["operation"] = operation
        super().__init__("internal_error", message, details)


class IncompleteImplementationError(NotImplementedError):
    """Mark an intentionally unfinished learner milestone."""


def incomplete(feature: str) -> NoReturn:
    """Raise the single deliberate failure used by scaffold operations."""

    # The starter remains importable and type-correct; unfinished behavior fails
    # explicitly instead of leaking a plausible-looking placeholder result.
    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the matching milestone"
    )


__all__ = [
    "ErrorCode",
    "IncompleteImplementationError",
    "StorageError",
    "TaskError",
    "TaskNotFoundError",
    "ValidationError",
    "incomplete",
]
