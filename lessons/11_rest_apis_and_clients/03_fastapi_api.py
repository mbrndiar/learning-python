"""
Lesson 11.3: A FastAPI API

Pydantic models validate the HTTP boundary. A FastAPI dependency provider finds
the injected service, response models document output, and exception handlers
map framework/domain failures to one envelope. No server process is started.
"""

import unicodedata
from dataclasses import dataclass
from typing import Annotated, Literal, Protocol

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


class DomainError(Exception):
    code = "internal_error"
    status = 500

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(DomainError):
    code = "validation_error"
    status = 422


class NotFoundError(DomainError):
    code = "not_found"
    status = 404


class TaskRepository(Protocol):
    def create(self, title: str) -> Task:
        """Store and return one task."""

    def list(self, completed: bool | None = None) -> list[Task]:
        """Return tasks in ID order."""

    def get(self, task_id: int) -> Task | None:
        """Return one task, or None."""


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def create(self, title: str) -> Task:
        task = Task(len(self._tasks) + 1, title, False)
        self._tasks.append(task)
        return task

    def list(self, completed: bool | None = None) -> list[Task]:
        return [
            task
            for task in self._tasks
            if completed is None or task.completed is completed
        ]

    def get(self, task_id: int) -> Task | None:
        return next((task for task in self._tasks if task.id == task_id), None)


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create(self, title: str) -> Task:
        normalized = title.strip()
        if not 1 <= len(normalized) <= 120:
            raise ValidationError(
                "title must contain between 1 and 120 characters",
                details={"field": "title"},
            )
        if any(unicodedata.category(character) == "Cc" for character in normalized):
            raise ValidationError(
                "title must not contain control characters",
                details={"field": "title"},
            )
        return self._repository.create(normalized)

    def list(self, completed: bool | None) -> list[Task]:
        return self._repository.list(completed)

    def get(self, task_id: int) -> Task:
        if task_id <= 0:
            raise ValidationError(
                "task ID must be positive",
                details={"field": "task_id"},
            )
        task = self._repository.get(task_id)
        if task is None:
            raise NotFoundError(f"task {task_id} was not found")
        return task


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    title: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    title: str
    completed: bool


def error_content(error: DomainError) -> dict[str, object]:
    value: dict[str, object] = {
        "code": error.code,
        "message": error.message,
    }
    if error.details is not None:
        value["details"] = error.details
    return {"error": value}


def get_task_service(request: Request) -> TaskService:
    service = request.app.state.task_service
    if not isinstance(service, TaskService):
        raise RuntimeError("Task service was not configured")
    return service


ServiceDependency = Annotated[TaskService, Depends(get_task_service)]
CompletedQuery = Annotated[
    Literal["true", "false"] | None,
    Query(description="Filter by exact lowercase completion state"),
]


def create_app(repository: TaskRepository | None = None) -> FastAPI:
    app = FastAPI(title="Task lesson API", version="1.0.0")
    selected_repository = (
        repository if repository is not None else InMemoryTaskRepository()
    )
    app.state.task_service = TaskService(selected_repository)

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        error: DomainError,
    ) -> JSONResponse:
        del request
        return JSONResponse(error_content(error), status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
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
        return JSONResponse(error_content(mapped), status_code=mapped.status)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request,
        error: HTTPException,
    ) -> JSONResponse:
        del request
        if error.status_code == 404:
            mapped = NotFoundError("route was not found")
            return JSONResponse(
                error_content(mapped),
                status_code=mapped.status,
            )
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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

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


def test_fastapi_api() -> None:
    repository = InMemoryTaskRepository()
    app = create_app(repository)

    with TestClient(app) as client:
        created = client.post("/tasks", json={"title": "  Learn FastAPI  "})
        assert created.status_code == 201
        assert created.json() == {
            "id": 1,
            "title": "Learn FastAPI",
            "completed": False,
        }

        listed = client.get("/tasks", params={"completed": "false"})
        assert listed.status_code == 200
        assert listed.json() == [created.json()]

        wrong_shape = client.post(
            "/tasks",
            json={"title": "Valid", "done": True},
        )
        assert wrong_shape.status_code == 422
        assert wrong_shape.json()["error"]["code"] == "validation_error"

        wrong_filter = client.get("/tasks", params={"completed": "True"})
        assert wrong_filter.status_code == 422
        assert wrong_filter.json()["error"]["code"] == "validation_error"

        missing = client.get("/tasks/99")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "not_found"

    generated = app.openapi()
    assert {"/health", "/tasks", "/tasks/{task_id}"} <= set(generated["paths"])
    schemas = generated["components"]["schemas"]
    assert {"CreateTaskRequest", "TaskResponse"} <= set(schemas)
    assert repository.list() == [Task(1, "Learn FastAPI", False)]


if __name__ == "__main__":
    test_fastapi_api()
    print("FastAPI test-client and generated OpenAPI checks passed!")
