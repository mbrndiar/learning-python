"""Task values and guided milestone-one validation boundaries."""

from dataclasses import dataclass
from enum import Enum

from .errors import incomplete

MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 120


class UnsetType(Enum):
    """Singleton type used when a partial-update field was omitted."""

    UNSET = "unset"


UNSET = UnsetType.UNSET


@dataclass(frozen=True, slots=True)
class Task:
    """Read-only task value shared by repositories and adapters."""

    id: int
    title: str
    completed: bool

    # TODO(milestone 1): validate and normalize every field in __post_init__.


@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    """Normalized repository input for creating an incomplete task."""

    title: str

    # TODO(milestone 1): preserve the validated, trimmed title invariant.


@dataclass(frozen=True, slots=True)
class UpdateTaskInput:
    """Normalized partial update with omission distinct from ``False``."""

    title: str | UnsetType = UNSET
    completed: bool | UnsetType = UNSET

    # TODO(milestone 1): reject an empty update and validate present fields.


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


def normalize_create_input(title: object) -> CreateTaskInput:
    """Return validated repository input for a create operation."""

    incomplete(f"milestone 1 create input normalization for {title!r}")


def normalize_update_input(
    *,
    title: object = UNSET,
    completed: object = UNSET,
) -> UpdateTaskInput:
    """Return a validated partial update, preserving omitted fields."""

    incomplete(
        "milestone 1 update input normalization "
        f"for title={title!r}, completed={completed!r}"
    )


__all__ = [
    "MAX_TITLE_LENGTH",
    "MIN_TITLE_LENGTH",
    "UNSET",
    "CreateTaskInput",
    "Task",
    "UnsetType",
    "UpdateTaskInput",
    "normalize_create_input",
    "normalize_update_input",
    "validate_completed",
    "validate_completed_filter",
    "validate_task_id",
    "validate_title",
]
