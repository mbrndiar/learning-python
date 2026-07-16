"""Task values and boundary normalization independent of storage or frameworks."""

from dataclasses import dataclass
from enum import Enum
from unicodedata import category

from .errors import ValidationError

MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 120


class UnsetType(Enum):
    """Distinguish an omitted update field from an explicitly supplied value.

    In particular, ``False`` must remain a real completion update rather than
    being mistaken for a missing, falsey value.
    """

    UNSET = "unset"


UNSET = UnsetType.UNSET


def validate_task_id(value: object) -> int:
    """Validate and return a positive task identifier."""

    # bool is a subclass of int in Python, so the explicit exclusion keeps IDs
    # from silently accepting True as 1.
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValidationError(
            "task ID must be a positive integer",
            field="id",
        )
    return value


def validate_title(value: object) -> str:
    """Validate, trim, and return a task title."""

    if not isinstance(value, str):
        raise ValidationError("title must be a string", field="title")

    title = value.strip()
    if not MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH:
        raise ValidationError(
            "title must contain between 1 and 120 characters",
            field="title",
        )
    if len(title.splitlines()) != 1:
        raise ValidationError("title must occupy one physical line", field="title")
    if any(category(character) == "Cc" for character in title):
        raise ValidationError(
            "title must not contain control characters",
            field="title",
        )
    return title


def validate_completed(value: object) -> bool:
    """Accept only bool, rather than coercing integers or other truthy values."""

    if not isinstance(value, bool):
        raise ValidationError("completed must be a Boolean", field="completed")
    return value


def validate_completed_filter(value: object | None) -> bool | None:
    """Validate an optional completion filter."""

    if value is None:
        return None
    return validate_completed(value)


@dataclass(frozen=True, slots=True)
class Task:
    """Validated, immutable task value shared by repositories and adapters."""

    id: int
    title: str
    completed: bool

    def __post_init__(self) -> None:
        # frozen dataclasses reject normal assignment even during post-init.
        # object.__setattr__ permits this one-time normalization; later ordinary
        # attribute assignment remains blocked by the generated frozen methods.
        object.__setattr__(self, "id", validate_task_id(self.id))
        object.__setattr__(self, "title", validate_title(self.title))
        object.__setattr__(self, "completed", validate_completed(self.completed))


@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    """Normalized repository input for creating an incomplete task."""

    title: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", validate_title(self.title))


@dataclass(frozen=True, slots=True)
class UpdateTaskInput:
    """Normalized partial update with omission distinct from ``False``."""

    title: str | UnsetType = UNSET
    completed: bool | UnsetType = UNSET

    def __post_init__(self) -> None:
        title_omitted = isinstance(self.title, UnsetType)
        completed_omitted = isinstance(self.completed, UnsetType)
        if title_omitted and completed_omitted:
            raise ValidationError(
                "update must include title or completed",
                field="update",
            )
        if not title_omitted:
            object.__setattr__(self, "title", validate_title(self.title))
        if not completed_omitted:
            object.__setattr__(
                self,
                "completed",
                validate_completed(self.completed),
            )


def normalize_create_input(title: object) -> CreateTaskInput:
    """Convert an untyped boundary value into repository-ready create input."""

    return CreateTaskInput(title=validate_title(title))


def normalize_update_input(
    *,
    title: object = UNSET,
    completed: object = UNSET,
) -> UpdateTaskInput:
    """Normalize boundary values while preserving which fields were omitted."""

    normalized_title: str | UnsetType
    if isinstance(title, UnsetType):
        normalized_title = UNSET
    else:
        normalized_title = validate_title(title)

    normalized_completed: bool | UnsetType
    if isinstance(completed, UnsetType):
        normalized_completed = UNSET
    else:
        normalized_completed = validate_completed(completed)

    return UpdateTaskInput(
        title=normalized_title,
        completed=normalized_completed,
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
