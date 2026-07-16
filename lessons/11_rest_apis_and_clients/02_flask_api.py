"""
Lesson 11.2: A Flask API

An application factory constructs dependencies once. Routes translate HTTP
input and output while a service owns validation and repository coordination.
The demonstration uses Flask's in-process test client and never starts a server.
"""

import unicodedata
from dataclasses import asdict, dataclass
from typing import Protocol

from flask import Flask, Response, jsonify, request
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


class InvalidJsonError(DomainError):
    code = "invalid_json"
    status = 400


class MethodNotAllowedError(DomainError):
    code = "method_not_allowed"
    status = 405


class TaskRepository(Protocol):
    def create(self, title: str) -> Task:
        """Store and return one incomplete task."""

    def list(self, completed: bool | None = None) -> list[Task]:
        """Return tasks in ID order, optionally filtered."""

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


def parse_create_request(value: object) -> str:
    if not isinstance(value, dict):
        raise ValidationError("request body must be an object")
    if set(value) != {"title"}:
        unknown = sorted(set(value) - {"title"})
        message = f"unknown property: {unknown[0]}" if unknown else "title is required"
        raise ValidationError(message)
    title = value["title"]
    if not isinstance(title, str):
        raise ValidationError(
            "title must be a string",
            details={"field": "title"},
        )
    return title


def parse_completed_filter(values: list[str]) -> bool | None:
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


def error_body(error: DomainError) -> dict[str, object]:
    details: dict[str, object] = {
        "code": error.code,
        "message": error.message,
    }
    if error.details is not None:
        details["details"] = error.details
    return {"error": details}


def create_app(repository: TaskRepository | None = None) -> Flask:
    """Construct a complete app with an injected repository."""

    app = Flask(__name__)
    selected_repository = (
        repository if repository is not None else InMemoryTaskRepository()
    )
    service = TaskService(selected_repository)

    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError) -> tuple[Response, int]:
        return jsonify(error_body(error)), error.status

    @app.errorhandler(BadRequest)
    @app.errorhandler(UnsupportedMediaType)
    def handle_invalid_json(error: HTTPException) -> tuple[Response, int]:
        del error
        mapped = InvalidJsonError("request body must be valid JSON")
        return jsonify(error_body(mapped)), mapped.status

    @app.errorhandler(405)
    def handle_wrong_method(error: MethodNotAllowed) -> tuple[Response, int]:
        mapped = MethodNotAllowedError("method is not allowed for this path")
        response = jsonify(error_body(mapped))
        response.headers["Allow"] = ", ".join(error.valid_methods or ())
        return response, mapped.status

    @app.errorhandler(404)
    def handle_unknown_route(error: HTTPException) -> tuple[Response, int]:
        del error
        missing = NotFoundError("route was not found")
        return jsonify(error_body(missing)), missing.status

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.post("/tasks")
    def create_task() -> tuple[Response, int]:
        title = parse_create_request(request.get_json())
        return jsonify(asdict(service.create(title))), 201

    @app.get("/tasks")
    def list_tasks() -> Response:
        completed = parse_completed_filter(request.args.getlist("completed"))
        return jsonify([asdict(task) for task in service.list(completed)])

    @app.get("/tasks/<task_id>")
    def get_task(task_id: str) -> Response:
        if not task_id.isdecimal():
            raise ValidationError(
                "task ID must be a positive integer",
                details={"field": "task_id"},
            )
        return jsonify(asdict(service.get(int(task_id))))

    return app


def test_flask_api() -> None:
    repository = InMemoryTaskRepository()
    app = create_app(repository)
    app.config.update(TESTING=True)

    with app.test_client() as client:
        created = client.post("/tasks", json={"title": "  Learn Flask  "})
        assert created.status_code == 201
        assert created.get_json() == {
            "id": 1,
            "title": "Learn Flask",
            "completed": False,
        }

        listed = client.get("/tasks?completed=false")
        assert listed.status_code == 200
        assert listed.get_json() == [created.get_json()]

        invalid = client.post("/tasks", json={"title": "", "done": True})
        assert invalid.status_code == 422
        assert invalid.get_json()["error"]["code"] == "validation_error"

        invalid_json = client.post(
            "/tasks",
            data=b"{",
            content_type="application/json",
        )
        assert invalid_json.status_code == 400
        assert invalid_json.get_json()["error"]["code"] == "invalid_json"

        wrong_method = client.delete("/health")
        assert wrong_method.status_code == 405
        assert wrong_method.get_json()["error"]["code"] == "method_not_allowed"
        assert "GET" in wrong_method.headers["Allow"]

        missing = client.get("/tasks/99")
        assert missing.status_code == 404
        assert missing.get_json() == {
            "error": {
                "code": "not_found",
                "message": "task 99 was not found",
            }
        }

    assert repository.list() == [Task(1, "Learn Flask", False)]


if __name__ == "__main__":
    test_flask_api()
    print("Flask test-client checks passed!")
