"""Idiomatic Flask boundary for the Task HTTP API."""

from collections.abc import Mapping
from typing import NoReturn

from flask import Flask, Response, jsonify, request
from tasks_core.domain import UNSET, Task
from tasks_core.errors import StorageError, TaskNotFoundError, ValidationError
from tasks_core.service import TaskService
from werkzeug.exceptions import BadRequest, MethodNotAllowed, NotFound


class _InvalidJsonError(Exception):
    """The request body could not be decoded under the JSON contract."""


def _task_payload(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
    }


def _error_response(
    code: str,
    message: str,
    status: int,
    details: Mapping[str, object] | None = None,
) -> tuple[Response, int]:
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error["details"] = dict(details)
    return jsonify({"error": error}), status


def _json_object() -> dict[str, object]:
    if request.mimetype != "application/json":
        raise _InvalidJsonError
    try:
        request.get_data(cache=True).decode("utf-8")
        value: object = request.get_json(cache=False)
    except (BadRequest, UnicodeDecodeError) as error:
        raise _InvalidJsonError from error
    if not isinstance(value, dict):
        raise ValidationError("request body must be a JSON object", field="body")
    return value


def _validate_properties(
    value: Mapping[str, object],
    *,
    allowed: frozenset[str],
    required: frozenset[str] = frozenset(),
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        field = unknown[0]
        raise ValidationError(f"unknown property: {field}", field=field)
    missing = sorted(required - set(value))
    if missing:
        field = missing[0]
        raise ValidationError(f"missing property: {field}", field=field)


def _task_id(value: str) -> int:
    if not value.isascii() or not value.isdecimal():
        raise ValidationError("task ID must be a positive integer", field="id")
    task_id = int(value)
    if task_id <= 0:
        raise ValidationError("task ID must be a positive integer", field="id")
    return task_id


def _completed_filter() -> bool | None:
    if "completed" not in request.args:
        return None
    values = request.args.getlist("completed")
    if len(values) != 1 or values[0] not in {"true", "false"}:
        raise ValidationError(
            "completed must be true or false",
            field="completed",
        )
    return values[0] == "true"


def create_app(service: TaskService) -> Flask:
    """Create one Flask application with an injected Task service."""

    app = Flask(__name__)

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.post("/tasks")
    def create_task() -> tuple[Response, int]:
        body = _json_object()
        _validate_properties(
            body,
            allowed=frozenset({"title"}),
            required=frozenset({"title"}),
        )
        task = service.create_task(body["title"])
        return jsonify(_task_payload(task)), 201

    @app.get("/tasks")
    def list_tasks() -> Response:
        tasks = service.list_tasks(_completed_filter())
        return jsonify([_task_payload(task) for task in tasks])

    @app.get("/tasks/<task_id>")
    def get_task(task_id: str) -> Response:
        return jsonify(_task_payload(service.get_task(_task_id(task_id))))

    @app.patch("/tasks/<task_id>")
    def update_task(task_id: str) -> Response:
        body = _json_object()
        _validate_properties(
            body,
            allowed=frozenset({"title", "completed"}),
        )
        task = service.update_task(
            _task_id(task_id),
            title=body["title"] if "title" in body else UNSET,
            completed=body["completed"] if "completed" in body else UNSET,
        )
        return jsonify(_task_payload(task))

    @app.delete("/tasks/<task_id>")
    def delete_task(task_id: str) -> tuple[str, int]:
        service.delete_task(_task_id(task_id))
        return "", 204

    @app.errorhandler(_InvalidJsonError)
    def handle_invalid_json(_: _InvalidJsonError) -> tuple[Response, int]:
        return _error_response(
            "invalid_json",
            "request body must be valid JSON",
            400,
        )

    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError) -> tuple[Response, int]:
        return _error_response(
            error.code,
            error.message,
            422,
            error.details,
        )

    @app.errorhandler(TaskNotFoundError)
    def handle_not_found(error: TaskNotFoundError) -> tuple[Response, int]:
        return _error_response(error.code, error.message, 404)

    @app.errorhandler(StorageError)
    def handle_storage(error: StorageError) -> tuple[Response, int]:
        app.logger.error("Task storage failure", exc_info=error)
        return _error_response(
            "internal_error",
            "the server could not complete the request",
            500,
        )

    @app.errorhandler(NotFound)
    def handle_unknown_route(_: NotFound) -> tuple[Response, int]:
        return _error_response("not_found", "route was not found", 404)

    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(
        error: MethodNotAllowed,
    ) -> tuple[Response, int]:
        response, status = _error_response(
            "method_not_allowed",
            "method is not allowed for this path",
            405,
        )
        if error.valid_methods:
            response.headers["Allow"] = ", ".join(error.valid_methods)
        return response, status

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception) -> tuple[Response, int]:
        app.logger.error("Unexpected Task API failure", exc_info=error)
        return _error_response(
            "internal_error",
            "the server could not complete the request",
            500,
        )

    return app


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """Run Flask's development server with explicit local-development settings."""

    create_app(service).run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
    raise SystemExit(0)


__all__ = ["create_app", "serve"]
