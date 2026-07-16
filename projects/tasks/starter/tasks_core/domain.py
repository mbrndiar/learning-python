"""Task values and guided milestone-one validation boundaries."""

from dataclasses import dataclass
from enum import Enum

from .errors import incomplete

MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 120


class UnsetType(Enum):
    """Singleton type used when a partial-update field was omitted."""

    # `None` is not used for omission: it is invalid input, while `False` is a
    # valid PATCH value that must survive boundary conversion unchanged.
    UNSET = "unset"


UNSET = UnsetType.UNSET


@dataclass(frozen=True, slots=True)
class Task:
    """Read-only task value shared by repositories and adapters."""

    id: int
    title: str
    completed: bool

    # TODO(milestone 1): validate and normalize every field in __post_init__.
    # Establish the invariant during construction without making later ordinary
    # attribute assignment possible on this frozen value.


@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    """Normalized repository input for creating an incomplete task."""

    title: str

    # TODO(milestone 1): preserve the validated, trimmed title invariant.
    # Repository inputs are trusted only after this boundary has normalized them.


@dataclass(frozen=True, slots=True)
class UpdateTaskInput:
    """Normalized partial update with omission distinct from ``False``."""

    title: str | UnsetType = UNSET
    completed: bool | UnsetType = UNSET

    # TODO(milestone 1): reject an empty update and validate present fields.
    # Validate only values that are not UNSET; explicit False means "mark
    # incomplete", not "the caller omitted completed".


def validate_task_id(value: object) -> int:
    """Validate and return a positive task identifier."""

    # `bool` subclasses `int`, so a strict ID check must reject True and False.
    incomplete(f"milestone 1 task ID validation for {value!r}")


def validate_title(value: object) -> str:
    """Validate, trim, and return a task title."""

    # Treat boundary text as untrusted: normalize surrounding whitespace, then
    # enforce the length, one-line, and control-character rules from the spec.
    incomplete(f"milestone 1 title validation for {value!r}")


def validate_completed(value: object) -> bool:
    """Validate and return a strict Boolean completion value."""

    # Truthy integers and strings are not accepted; the domain requires an
    # actual bool so every adapter observes the same contract.
    incomplete(f"milestone 1 completion validation for {value!r}")


def validate_completed_filter(value: object | None) -> bool | None:
    """Validate an optional completion filter."""

    incomplete(f"milestone 1 completion filter validation for {value!r}")


def normalize_create_input(title: object) -> CreateTaskInput:
    """Return validated repository input for a create operation."""

    # Keep raw boundary values out of repositories. The service converts them
    # into this narrow, already-validated persistence input.
    incomplete(f"milestone 1 create input normalization for {title!r}")


def normalize_update_input(
    *,
    title: object = UNSET,
    completed: object = UNSET,
) -> UpdateTaskInput:
    """Return a validated partial update, preserving omitted fields."""

    # Preserve UNSET while normalizing each supplied value independently; using
    # truthiness here would accidentally discard completed=False.
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
