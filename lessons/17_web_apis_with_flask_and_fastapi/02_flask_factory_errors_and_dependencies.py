"""
Chapter 17, Lesson 2: Flask Factory, Errors, and Dependencies

Purpose: construct a fresh app with an injected repository, keep routes thin,
and map domain plus Werkzeug failures through centralized JSON handlers.

Prerequisite: Lesson 1 and the shared `_task_domain.py` support module.

Run from the repository root:

    python lessons/17_web_apis_with_flask_and_fastapi/02_flask_factory_errors_and_dependencies.py
"""

from dataclasses import asdict

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
from flask import Flask, Response, jsonify, request
from werkzeug.exceptions import (
    BadRequest,
    HTTPException,
    MethodNotAllowed,
    UnsupportedMediaType,
)


def parse_title(value: object) -> str:
    if not isinstance(value, dict) or set(value) != {"title"}:
        raise ValidationError("request body must contain exactly title")
    title = value["title"]
    if not isinstance(title, str):
        raise ValidationError(
            "title must be a string",
            details={"field": "title"},
        )
    return title


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


# Step 1: the factory creates dependencies once and returns a configured app.
def create_app(repository: TaskRepository | None = None) -> Flask:
    app = Flask(__name__)
    selected_repository = (
        repository if repository is not None else InMemoryTaskRepository()
    )
    service = TaskService(selected_repository)

    # Step 2: error handlers centralize public envelopes instead of duplicating
    # try/except blocks in every route.
    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError) -> tuple[Response, int]:
        return jsonify(error_body(error)), error.status

    @app.errorhandler(BadRequest)
    @app.errorhandler(UnsupportedMediaType)
    def handle_invalid_json(error: HTTPException) -> tuple[Response, int]:
        del error
        mapped = DomainError("request body must be valid JSON")
        mapped.code = "invalid_json"
        mapped.status = 400
        return jsonify(error_body(mapped)), mapped.status

    @app.errorhandler(405)
    def handle_wrong_method(error: MethodNotAllowed) -> tuple[Response, int]:
        mapped = DomainError("method is not allowed for this path")
        mapped.code = "method_not_allowed"
        mapped.status = 405
        response = jsonify(error_body(mapped))
        response.headers["Allow"] = ", ".join(error.valid_methods or ())
        return response, mapped.status

    @app.errorhandler(404)
    def handle_unknown_route(error: HTTPException) -> tuple[Response, int]:
        del error
        missing = NotFoundError("route was not found")
        return jsonify(error_body(missing)), missing.status

    # Step 3: routes translate framework input/output and delegate task rules.
    @app.post("/tasks")
    def create_task() -> tuple[Response, int]:
        title = parse_title(request.get_json())
        return jsonify(asdict(service.create(title))), 201

    @app.get("/tasks")
    def list_tasks() -> Response:
        completed = parse_completed(request.args.getlist("completed"))
        return jsonify([asdict(task) for task in service.list(completed)])

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id: int) -> Response:
        return jsonify(asdict(service.get(task_id)))

    return app


if __name__ == "__main__":
    repository = InMemoryTaskRepository()
    flask_app = create_app(repository)
    flask_app.config.update(TESTING=True)

    with flask_app.test_client() as client:
        created = client.post("/tasks", json={"title": "  Learn factories  "})
        listed = client.get("/tasks", query_string={"completed": "false"})
        invalid = client.post("/tasks", json={"title": "", "extra": True})
        missing = client.get("/tasks/99")
        wrong_method = client.delete("/tasks")

    assert created.status_code == 201
    assert created.get_json() == {
        "id": 1,
        "title": "Learn factories",
        "completed": False,
    }
    assert listed.get_json() == [created.get_json()]
    assert invalid.status_code == 422
    assert invalid.get_json()["error"]["code"] == "validation_error"
    assert missing.status_code == 404
    assert wrong_method.status_code == 405
    assert "GET" in wrong_method.headers["Allow"]
    assert repository.list() == [Task(1, "Learn factories", False)]

    print("created:", created.status_code, created.get_json())
    print("validation:", invalid.status_code, invalid.get_json())
    print("not found:", missing.status_code, missing.get_json())
