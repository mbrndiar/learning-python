"""Idiomatic Flask boundary for the Task HTTP API."""

import json
from collections.abc import Mapping
from typing import NoReturn

from flask import Flask, Response, jsonify, request
from tasks_core.domain import UNSET, Task
from tasks_core.errors import StorageError, TaskNotFoundError, ValidationError
from tasks_core.service import TaskService
from werkzeug.exceptions import BadRequest, MethodNotAllowed, NotFound

MAX_REQUEST_BODY = 64 * 1024
_METHODS_BY_ROUTE = {
    "health": ("GET",),
    "tasks": ("GET", "POST"),
    "task": ("GET", "PATCH", "DELETE"),
}


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


def _reject_duplicate_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise _InvalidJsonError("request body must be valid JSON")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> NoReturn:
    del value
    raise _InvalidJsonError("request body must be valid JSON")


def _json_object() -> dict[str, object]:
    if request.mimetype != "application/json":
        raise _InvalidJsonError("request Content-Type must be application/json")
    charset = request.mimetype_params.get("charset")
    if charset is not None and charset.casefold() != "utf-8":
        raise _InvalidJsonError("request JSON charset must be UTF-8")
    try:
        body = request.get_data(cache=False)
        if len(body) > MAX_REQUEST_BODY:
            raise _InvalidJsonError("request body is too large")
        value: object = json.loads(
            body.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_fields,
            parse_constant=_reject_json_constant,
        )
    except (
        BadRequest,
        UnicodeDecodeError,
        json.JSONDecodeError,
        _InvalidJsonError,
    ) as error:
        if isinstance(error, _InvalidJsonError):
            raise
        raise _InvalidJsonError("request body must be valid JSON") from error
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
            "completed filter must be true or false",
            field="completed",
        )
    return values[0] == "true"


def _route(path: str) -> str | None:
    if path == "/health":
        return "health"
    if path == "/tasks":
        return "tasks"
    if path.startswith("/tasks/"):
        task_id = path.removeprefix("/tasks/")
        if task_id and "/" not in task_id:
            return "task"
    return None


def _validate_query(allowed: frozenset[str]) -> None:
    unknown = sorted(set(request.args) - allowed)
    if unknown:
        field = unknown[0]
        raise ValidationError(
            f"unknown query parameter: {field}",
            field=field,
        )


def create_app(service: TaskService) -> Flask:
    """Create one Flask application with an injected Task service."""

    app = Flask(__name__)

    @app.before_request
    def enforce_portable_contract() -> tuple[Response, int] | None:
        route = _route(request.path)
        if route is None:
            return None
        methods = _METHODS_BY_ROUTE[route]
        if request.method not in methods:
            response, status_code = _error_response(
                "method_not_allowed",
                "method is not allowed for this path",
                405,
            )
            response.headers["Allow"] = ", ".join(methods)
            return response, status_code

        allowed_query = (
            frozenset({"completed"})
            if route == "tasks" and request.method == "GET"
            else frozenset()
        )
        _validate_query(allowed_query)
        return None

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
    def delete_task(task_id: str) -> Response:
        service.delete_task(_task_id(task_id))
        response = Response(status=204)
        response.headers.pop("Content-Type", None)
        return response

    @app.errorhandler(_InvalidJsonError)
    def handle_invalid_json(error: _InvalidJsonError) -> tuple[Response, int]:
        return _error_response(
            "invalid_json",
            str(error),
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
        route = _route(request.path)
        methods = _METHODS_BY_ROUTE.get(route or "")
        response, status = _error_response(
            "method_not_allowed",
            "method is not allowed for this path",
            405,
        )
        if methods is not None:
            response.headers["Allow"] = ", ".join(methods)
        elif error.valid_methods:
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
