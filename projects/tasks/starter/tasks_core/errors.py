"""Stable domain errors and intentional learning placeholders."""

from collections.abc import Mapping
from typing import NoReturn


class TaskError(Exception):
    """Expected application failure safe to translate at a boundary."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Mapping[str, object] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = dict(details or {})
        super().__init__(message)


class ValidationError(TaskError):
    """A request or domain value violates the Task contract."""


class TaskNotFoundError(TaskError):
    """A valid task identifier does not exist."""


class StorageError(TaskError):
    """Persistence could not safely complete an operation."""


class IncompleteImplementationError(NotImplementedError):
    """Mark an intentionally unfinished learner milestone."""


def incomplete(feature: str) -> NoReturn:
    """Raise the single deliberate failure used by scaffold operations."""

    raise IncompleteImplementationError(
        f"{feature} is intentionally incomplete; implement the matching milestone"
    )


__all__ = [
    "IncompleteImplementationError",
    "StorageError",
    "TaskError",
    "TaskNotFoundError",
    "ValidationError",
    "incomplete",
]
