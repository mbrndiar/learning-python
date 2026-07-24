"""Solutions: Chapter 17 - Web APIs with Flask and FastAPI."""

import inspect
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Literal, Protocol

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from flask import Flask, Response, jsonify
from flask import request as flask_request
from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticError
from starlette.exceptions import HTTPException as StarletteHTTPException
from werkzeug.exceptions import (
    BadRequest,
    HTTPException,
    MethodNotAllowed,
    UnsupportedMediaType,
)


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool
    internal_note: str


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


class TaskRepository(Protocol):
    def create(self, title: str) -> Task:
        """Store and return one incomplete task."""

    def list(self, completed: bool | None = None) -> list[Task]:
        """Return tasks in ID order, optionally filtered."""


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def create(self, title: str) -> Task:
        task = Task(
            id=len(self._tasks) + 1,
            title=title,
            completed=False,
            internal_note="repository-only metadata",
        )
        self._tasks.append(task)
        return task

    def list(self, completed: bool | None = None) -> list[Task]:
        return [
            task
            for task in self._tasks
            if completed is None or task.completed is completed
        ]


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

    def list(self, completed: bool | None = None) -> list[Task]:
        return self._repository.list(completed)


def error_body(error: DomainError) -> dict[str, object]:
    details: dict[str, object] = {
        "code": error.code,
        "message": error.message,
    }
    if error.details is not None:
        details["details"] = error.details
    return {"error": details}


def task_payload(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
    }


def parse_completed(values: list[str]) -> bool | None:
    if not values:
        return None
    if values == ["true"]:
        return True
    if values == ["false"]:
        return False
    raise ValidationError(
        "completed must appear once as true or false",
        details={"field": "completed"},
    )


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


def create_flask_app(repository: TaskRepository | None = None) -> Flask:
    app = Flask(__name__)
    selected = repository if repository is not None else InMemoryTaskRepository()
    service = TaskService(selected)

    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError) -> tuple[Response, int]:
        return jsonify(error_body(error)), error.status

    @app.errorhandler(BadRequest)
    @app.errorhandler(UnsupportedMediaType)
    def handle_invalid_json(error: HTTPException) -> tuple[Response, int]:
        del error
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_json",
                        "message": "request body must be valid JSON",
                    }
                }
            ),
            400,
        )

    @app.errorhandler(405)
    def handle_wrong_method(error: MethodNotAllowed) -> tuple[Response, int]:
        response = jsonify(
            {
                "error": {
                    "code": "method_not_allowed",
                    "message": "method is not allowed for this path",
                }
            }
        )
        response.headers["Allow"] = ", ".join(error.valid_methods or ())
        return response, 405

    @app.errorhandler(404)
    def handle_unknown_route(error: HTTPException) -> tuple[Response, int]:
        del error
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "route was not found",
                    }
                }
            ),
            404,
        )

    @app.post("/tasks")
    def create_task() -> tuple[Response, int]:
        payload: object = flask_request.get_json()
        if not isinstance(payload, dict) or set(payload) != {"title"}:
            raise ValidationError("request body must contain exactly title")
        title = payload["title"]
        if not isinstance(title, str):
            raise ValidationError(
                "title must be a string",
                details={"field": "title"},
            )
        return jsonify(task_payload(service.create(title))), 201

    @app.get("/tasks")
    def list_tasks() -> Response:
        completed = parse_completed(flask_request.args.getlist("completed"))
        return jsonify([task_payload(task) for task in service.list(completed)])

    return app


def get_task_service(http_request: Request) -> TaskService:
    service = http_request.app.state.task_service
    if not isinstance(service, TaskService):
        raise RuntimeError("Task service was not configured")
    return service


ServiceDependency = Annotated[TaskService, Depends(get_task_service)]
CompletedQuery = Annotated[
    Literal["true", "false"] | None,
    Query(description="Exact lowercase completion state"),
]


def create_fastapi_app(repository: TaskRepository | None = None) -> FastAPI:
    app = FastAPI(title="Task exercise API", version="1.0.0")
    selected = repository if repository is not None else InMemoryTaskRepository()
    app.state.task_service = TaskService(selected)

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
    def handle_http_error(
        request: Request,
        error: StarletteHTTPException,
    ) -> JSONResponse:
        del request
        if error.status_code == 404:
            code = "not_found"
            message = "route was not found"
        else:
            code = "method_not_allowed"
            message = "method is not allowed for this path"
        return JSONResponse(
            {"error": {"code": code, "message": message}},
            status_code=error.status_code,
            headers=error.headers,
        )

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

    return app


class _FalseLikeRepository(InMemoryTaskRepository):
    def __bool__(self) -> bool:
        return False


def evaluate_pydantic_models() -> None:
    model = CreateTaskRequest.model_validate({"title": "  Learn boundaries  "})
    assert model.title == "Learn boundaries"
    assert model.model_dump() == {"title": "Learn boundaries"}

    invalid_values = [
        {"title": 3},
        {"title": b"bytes are coercible only in lax mode"},
        {"title": "valid", "extra": True},
        {"title": "   "},
        {"title": "x" * 121},
    ]
    for value in invalid_values:
        try:
            CreateTaskRequest.model_validate(value)
        except PydanticError:
            pass
        else:
            raise AssertionError(f"request model should reject {value!r}")

    stored = Task(1, "Public title", False, "must stay private")
    response = TaskResponse.model_validate(stored)
    assert response.model_dump() == {
        "id": 1,
        "title": "Public title",
        "completed": False,
    }
    assert "internal_note" not in response.model_dump()

    schema = CreateTaskRequest.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["title"]["minLength"] == 1
    assert schema["properties"]["title"]["maxLength"] == 120


def evaluate_flask_factory() -> None:
    repository = _FalseLikeRepository()
    app = create_flask_app(repository)
    app.config.update(TESTING=True)

    with app.test_client() as client:
        created = client.post("/tasks", json={"title": "  Learn Flask  "})
        listed = client.get("/tasks", query_string={"completed": "false"})
        invalid_filter = client.get(
            "/tasks",
            query_string={"completed": "False"},
        )
        invalid_type = client.post("/tasks", json={"title": 3})
        extra_field = client.post(
            "/tasks",
            json={"title": "valid", "extra": True},
        )
        malformed = client.post(
            "/tasks",
            data="{",
            content_type="application/json",
        )
        wrong_method = client.delete("/tasks")
        unknown = client.get("/unknown")

    expected = {"id": 1, "title": "Learn Flask", "completed": False}
    assert created.status_code == 201
    assert created.get_json() == expected
    assert "internal_note" not in created.get_json()
    assert listed.status_code == 200
    assert listed.get_json() == [expected]
    assert invalid_filter.status_code == 422
    assert invalid_filter.get_json()["error"]["code"] == "validation_error"
    assert invalid_type.status_code == 422
    assert invalid_type.get_json()["error"]["code"] == "validation_error"
    assert extra_field.status_code == 422
    assert malformed.status_code == 400
    assert malformed.get_json()["error"]["code"] == "invalid_json"
    assert wrong_method.status_code == 405
    assert wrong_method.get_json()["error"]["code"] == "method_not_allowed"
    assert {"GET", "POST"} <= set(wrong_method.headers["Allow"].split(", "))
    assert unknown.status_code == 404
    assert unknown.get_json()["error"]["code"] == "not_found"
    assert repository.list() == [
        Task(1, "Learn Flask", False, "repository-only metadata")
    ]

    with create_flask_app().test_client() as fresh_client:
        assert fresh_client.get("/tasks").get_json() == []


def evaluate_fastapi_factory() -> None:
    repository = _FalseLikeRepository()
    app = create_fastapi_app(repository)

    with TestClient(app) as client:
        created = client.post("/tasks", json={"title": "  Learn FastAPI  "})
        listed = client.get("/tasks", params={"completed": "false"})
        invalid_type = client.post("/tasks", json={"title": 3})
        extra_field = client.post(
            "/tasks",
            json={"title": "valid", "extra": True},
        )
        invalid_query = client.get("/tasks", params={"completed": "False"})
        domain_error = client.post("/tasks", json={"title": "two\nlines"})
        wrong_method = client.delete("/tasks")
        unknown = client.get("/unknown")

    expected = {"id": 1, "title": "Learn FastAPI", "completed": False}
    assert created.status_code == 201
    assert created.json() == expected
    assert "internal_note" not in created.json()
    assert listed.status_code == 200
    assert listed.json() == [expected]
    for response in (invalid_type, extra_field, invalid_query, domain_error):
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"
    assert wrong_method.status_code == 405
    assert wrong_method.json()["error"]["code"] == "method_not_allowed"
    assert wrong_method.headers["allow"] in {"GET", "POST", "GET, POST", "POST, GET"}
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "not_found"
    assert repository.list() == [
        Task(1, "Learn FastAPI", False, "repository-only metadata")
    ]

    service = app.state.task_service
    assert isinstance(service, TaskService)
    task_routes = [
        route
        for route in app.routes
        if isinstance(route, APIRoute) and route.path.startswith("/tasks")
    ]
    assert {route.path for route in task_routes} == {"/tasks"}
    assert all(not inspect.iscoroutinefunction(route.endpoint) for route in task_routes)
    assert all(route.response_model is not None for route in task_routes)

    schema = app.openapi()
    assert "/tasks" in schema["paths"]
    assert {"get", "post"} <= set(schema["paths"]["/tasks"])
    schemas = schema["components"]["schemas"]
    assert {"CreateTaskRequest", "TaskResponse"} <= set(schemas)

    with TestClient(create_fastapi_app()) as fresh_client:
        assert fresh_client.get("/tasks").json() == []


def evaluate_shared_contract() -> None:
    flask_app = create_flask_app()
    fastapi_app = create_fastapi_app()
    flask_app.config.update(TESTING=True)

    with (
        flask_app.test_client() as flask_client,
        TestClient(fastapi_app) as fastapi_client,
    ):
        flask_created = flask_client.post("/tasks", json={"title": "  Same API  "})
        fastapi_created = fastapi_client.post(
            "/tasks",
            json={"title": "  Same API  "},
        )
        assert (flask_created.status_code, flask_created.get_json()) == (
            fastapi_created.status_code,
            fastapi_created.json(),
        )

        flask_invalid = flask_client.post(
            "/tasks",
            json={"title": "valid", "extra": True},
        )
        fastapi_invalid = fastapi_client.post(
            "/tasks",
            json={"title": "valid", "extra": True},
        )
        assert flask_invalid.status_code == fastapi_invalid.status_code == 422
        assert (
            flask_invalid.get_json()["error"]["code"]
            == (fastapi_invalid.json()["error"]["code"])
        )

        flask_list = flask_client.get("/tasks", query_string={"completed": "false"})
        fastapi_list = fastapi_client.get(
            "/tasks",
            params={"completed": "false"},
        )
        assert flask_list.get_json() == fastapi_list.json()


def run_evaluation(label: str, evaluation: Callable[[], None]) -> None:
    try:
        evaluation()
    except NotImplementedError as error:
        raise AssertionError(f"{label}: implement the remaining TODO") from error
    print(f"{label}: OK")


if __name__ == "__main__":
    run_evaluation("Pydantic models", evaluate_pydantic_models)
    run_evaluation("Flask factory", evaluate_flask_factory)
    run_evaluation("FastAPI factory", evaluate_fastapi_factory)
    run_evaluation("shared API contract", evaluate_shared_contract)
    print("\nAll checks passed!")
