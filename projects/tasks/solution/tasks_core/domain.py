"""Task value and milestone-one validation boundaries."""

from dataclasses import dataclass

from .errors import incomplete


@dataclass(frozen=True, slots=True)
class Task:
    """Read-only task value shared by repositories and adapters."""

    id: int
    title: str
    completed: bool


def validate_task_id(value: object) -> int:
    """Validate and return a positive task identifier."""

    incomplete(f"milestone 1 task ID validation for {value!r}")


def validate_title(value: object) -> str:
    """Validate, trim, and return a task title."""

    incomplete(f"milestone 1 title validation for {value!r}")


def validate_completed(value: object) -> bool:
    """Validate and return a strict Boolean completion value."""

    incomplete(f"milestone 1 completion validation for {value!r}")


def validate_completed_filter(value: object | None) -> bool | None:
    """Validate an optional completion filter."""

    incomplete(f"milestone 1 completion filter validation for {value!r}")


__all__ = [
    "Task",
    "validate_completed",
    "validate_completed_filter",
    "validate_task_id",
    "validate_title",
]
