"""Guided Pydantic boundary models for milestone five."""

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
    """Represent an omitted PATCH field without accepting a JSON value.

    Explicit JSON null remains invalid; omission is an internal boundary state
    that will later map to the core's UNSET sentinel.
    """


MISSING = _Missing()
MissingField: TypeAlias = SkipJsonSchema[InstanceOf[_Missing]]


def _missing() -> _Missing:
    return MISSING


class BoundaryModel(BaseModel):
    """Reject fields outside the documented HTTP contract."""

    # Framework models deliberately reject unknown input instead of silently
    # accepting fields that the portable OpenAPI contract does not define.
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class Health(BoundaryModel):
    """TODO: return this fixed response from the GET /health readiness route."""

    status: Literal["ok"]


class Task(BoundaryModel):
    """TODO: convert domain Tasks to this response-only boundary model."""

    # from_attributes lets Pydantic read the domain dataclass without teaching
    # tasks_core about Pydantic or duplicating a manual response dictionary.
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: Annotated[int, Field(ge=1)]
    title: Title
    completed: Completed


class CreateTask(BoundaryModel):
    """TODO: inject this strict request model into the create route."""

    title: Title


class UpdateTask(BoundaryModel):
    """TODO: preserve omitted PATCH fields when calling TaskService.

    Consult Pydantic's set-field tracking: a default sentinel means omitted,
    whereas a supplied value must cross the domain validation boundary.
    """

    title: Title | MissingField = Field(default_factory=_missing)
    completed: Completed | MissingField = Field(default_factory=_missing)


class ErrorBody(BoundaryModel):
    """TODO: use this payload from centralized exception handlers.

    One error model keeps FastAPI validation, domain failures, and sanitized
    unexpected failures compatible with the shared HTTP envelope.
    """

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
