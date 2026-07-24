"""
Chapter 17, Lesson 4: FastAPI Dependencies, Responses, and OpenAPI

Purpose: compose strict Pydantic models, app-owned state, Depends providers,
synchronous handlers, response models, exception mapping, TestClient, and
generated OpenAPI over the shared task domain.

Prerequisite: Lessons 1-3 and Chapter 11 dependency injection.

Run from the repository root:

    python lessons/17_web_apis_with_flask_and_fastapi/04_fastapi_dependencies_responses_and_openapi.py
"""

from typing import Annotated, Literal

from _task_domain import (
    DomainError,
    InMemoryTaskRepository,
    NotFoundError,
    Task,
    TaskRepository,
    TaskService,
    ValidationError,
    error_body,
)
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

Title = Annotated[str, Field(min_length=1, max_length=120)]


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    title: Title


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, strict=True)

    id: int = Field(ge=1)
    title: str
    completed: bool


# Step 1: the dependency provider reads the service owned by this application.
def get_task_service(request: Request) -> TaskService:
    service = request.app.state.task_service
    if not isinstance(service, TaskService):
        raise RuntimeError("Task service was not configured")
    return service


ServiceDependency = Annotated[TaskService, Depends(get_task_service)]
CompletedQuery = Annotated[
    Literal["true", "false"] | None,
    Query(description="Exact lowercase completion state"),
]


def create_app(repository: TaskRepository | None = None) -> FastAPI:
    app = FastAPI(title="Task lesson API", version="1.0.0")
    selected_repository = (
        repository if repository is not None else InMemoryTaskRepository()
    )
    app.state.task_service = TaskService(selected_repository)

    # Step 2: all handlers are synchronous normal functions. The shared domain
    # controls stable error meaning; this adapter controls HTTP representation.
    @app.exception_handler(DomainError)
    def handle_domain_error(
        request: Request,
        error: DomainError,
    ) -> JSONResponse:
        del request
        return JSONResponse(error_body(error), status_code=error.status)

    @app.exception_handler(RequestValidationError)
    def handle_request_validation(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        del request
        first = error.errors()[0]
        location = first.get("loc", ())
        field = str(location[-1]) if location else "request"
        mapped = ValidationError(
            "request did not match the expected shape",
            details={"field": field},
        )
        return JSONResponse(error_body(mapped), status_code=mapped.status)

    @app.exception_handler(StarletteHTTPException)
    def handle_http_exception(
        request: Request,
        error: StarletteHTTPException,
    ) -> JSONResponse:
        del request
        if error.status_code == 404:
            mapped = NotFoundError("route was not found")
            return JSONResponse(error_body(mapped), status_code=mapped.status)
        return JSONResponse(
            {
                "error": {
                    "code": "method_not_allowed",
                    "message": "method is not allowed for this path",
                }
            },
            status_code=error.status_code,
            headers=error.headers,
        )

    # Step 3: FastAPI validates input and dependencies before calling these
    # functions, then validates/filters their results through response_model.
    @app.post("/tasks", response_model=TaskResponse, status_code=201)
    def create_task(
        payload: CreateTaskRequest,
        service: ServiceDependency,
    ) -> Task:
        return service.create(payload.title)

    @app.get("/tasks", response_model=list[TaskResponse])
    def list_tasks(
        service: ServiceDependency,
        completed: CompletedQuery = None,
    ) -> list[Task]:
        parsed = None if completed is None else completed == "true"
        return service.list(parsed)

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    def get_task(task_id: int, service: ServiceDependency) -> Task:
        return service.get(task_id)

    return app


if __name__ == "__main__":
    repository = InMemoryTaskRepository()
    fastapi_app = create_app(repository)

    # Step 4: TestClient runs synchronous calls in process.
    with TestClient(fastapi_app) as client:
        created = client.post("/tasks", json={"title": "  Learn FastAPI  "})
        listed = client.get("/tasks", params={"completed": "false"})
        invalid = client.post("/tasks", json={"title": 3, "extra": True})
        missing = client.get("/tasks/99")

    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        "title": "Learn FastAPI",
        "completed": False,
    }
    assert listed.json() == [created.json()]
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"
    assert missing.status_code == 404

    # Step 5: generated OpenAPI reflects registered operations and models.
    generated = fastapi_app.openapi()
    assert {"/tasks", "/tasks/{task_id}"} <= set(generated["paths"])
    schemas = generated["components"]["schemas"]
    assert {"CreateTaskRequest", "TaskResponse"} <= set(schemas)
    assert repository.list() == [Task(1, "Learn FastAPI", False)]

    print("created:", created.status_code, created.json())
    print("validation:", invalid.status_code, invalid.json())
    print("OpenAPI paths:", sorted(generated["paths"]))
