"""
Chapter 17, Lesson 3: Pydantic Boundary Models

Purpose: define strict input and output structures, control extra fields and
whitespace normalization, and inspect Python and JSON Schema serialization.

Prerequisite: Chapter 11 Annotated/Literal and Chapter 17 Lessons 1-2.

Run from the repository root:

    python lessons/17_web_apis_with_flask_and_fastapi/03_pydantic_boundary_models.py
"""

from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

Title = Annotated[str, Field(min_length=1, max_length=120)]
CompletedFilter = Literal["true", "false"]


# Step 1: strict=True rejects type coercion; extra="forbid" rejects undeclared
# input; str_strip_whitespace runs before the length constraint is evaluated.
class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    title: Title


# Step 2: an output model has a separate role. from_attributes=True lets it read
# the dataclass fields while Field(ge=1) checks the public ID contract.
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    id: int = Field(ge=1)
    title: str
    completed: bool


@dataclass(frozen=True)
class StoredTask:
    id: int
    title: str
    completed: bool
    internal_note: str


if __name__ == "__main__":
    # Step 3: model_validate() accepts an untrusted Python value and returns a
    # typed model only after all configured rules pass.
    request = CreateTaskRequest.model_validate({"title": "  Learn Pydantic  "})
    assert request.title == "Learn Pydantic"
    assert request.model_dump() == {"title": "Learn Pydantic"}

    invalid_values = [
        {"title": 3},
        {"title": "valid", "extra": True},
        {"title": "   "},
    ]
    for value in invalid_values:
        try:
            CreateTaskRequest.model_validate(value)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"value should be invalid: {value!r}")

    # Step 4: only fields declared by TaskResponse are serialized.
    stored = StoredTask(1, request.title, False, "not part of the API")
    response = TaskResponse.model_validate(stored)
    assert response.model_dump() == {
        "id": 1,
        "title": "Learn Pydantic",
        "completed": False,
    }

    schema = CreateTaskRequest.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["title"]["minLength"] == 1
    assert schema["properties"]["title"]["maxLength"] == 120

    print("validated input:", request.model_dump())
    print("filtered output:", response.model_dump())
    print("title schema:", schema["properties"]["title"])
