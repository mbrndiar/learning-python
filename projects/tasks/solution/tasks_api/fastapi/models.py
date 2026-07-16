"""Define strict Pydantic schemas for FastAPI's HTTP boundary.

These models convert between untrusted JSON-shaped data and typed route values;
the framework-neutral domain keeps its own validation and representations.
"""

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, InstanceOf, WithJsonSchema
from pydantic.json_schema import SkipJsonSchema
from tasks_core.domain import MAX_TITLE_LENGTH, MIN_TITLE_LENGTH

ErrorCode: TypeAlias = Literal[
    "invalid_json",
    "not_found",
    "method_not_allowed",
    "validation_error",
    "internal_error",
]
Title: TypeAlias = Annotated[
    str,
    Field(strict=True),
    WithJsonSchema(
        {
            "type": "string",
            "minLength": MIN_TITLE_LENGTH,
            "maxLength": MAX_TITLE_LENGTH,
        }
    ),
]
Completed: TypeAlias = Annotated[bool, Field(strict=True)]


class _Missing:
    """Represent an omitted PATCH field without adding a JSON-level sentinel."""


MISSING = _Missing()
MissingField: TypeAlias = SkipJsonSchema[InstanceOf[_Missing]]


def _missing() -> _Missing:
    return MISSING


class BoundaryModel(BaseModel):
    """Apply the closed-object policy shared by request and response models."""

    # Strict field aliases below prevent coercion, while ``extra="forbid"``
    # distinguishes misspelled client properties from valid domain input.
    # Arbitrary types are needed only for the private omission sentinel.
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class Health(BoundaryModel):
    """Readiness response."""

    status: Literal["ok"]


class Task(BoundaryModel):
    """Serialized Task value."""

    # Domain tasks are dataclasses, so response validation reads attributes
    # rather than requiring routes to first manufacture dictionaries.
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: Annotated[int, Field(ge=1)]
    title: Title
    completed: Completed


class CreateTask(BoundaryModel):
    """Request body for creating a task."""

    title: Title


class UpdateTask(BoundaryModel):
    """Request body preserving omitted fields for a partial update."""

    # The private default makes omission representable to Pydantic while
    # SkipJsonSchema keeps that implementation detail out of the HTTP schema.
    # Routes still use ``model_fields_set`` as the authoritative presence check.
    title: Title | MissingField = Field(default_factory=_missing)
    completed: Completed | MissingField = Field(default_factory=_missing)


class ErrorBody(BoundaryModel):
    """Stable error information nested in the shared envelope."""

    code: ErrorCode
    message: Annotated[str, Field(min_length=1)]
    details: dict[str, object] | SkipJsonSchema[None] = None


class Error(BoundaryModel):
    """Shared JSON error envelope."""

    error: ErrorBody


__all__ = [
    "MISSING",
    "BoundaryModel",
    "CreateTask",
    "Error",
    "ErrorBody",
    "Health",
    "Task",
    "UpdateTask",
]
