"""Typed FastAPI boundary for milestone five."""

import json
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, NoReturn

import uvicorn
from fastapi import Depends, FastAPI, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BeforeValidator
from starlette.exceptions import HTTPException
from tasks_core.domain import UNSET
from tasks_core.errors import TaskError, ValidationError
from tasks_core.service import TaskService

from .models import (
    CreateTask,
    Error,
    ErrorBody,
    ErrorCode,
    Health,
    Task,
    UpdateTask,
)

logger = logging.getLogger(__name__)

_INTERNAL_MESSAGE = "the server could not complete the request"
_UNPROCESSABLE_STATUS = 422
_JSON_METHOD_PATHS = (
    ("POST", re.compile(r"/tasks")),
    ("PATCH", re.compile(r"/tasks/[^/]+")),
)
_ERROR_DESCRIPTIONS = {
    400: "The request body could not be decoded as JSON.",
    404: "The task or route was not found.",
    405: "The path does not support the request method.",
    422: "The decoded request violates shape or domain rules.",
    500: "The server could not complete the request.",
}


def _error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    return {
        code: {
            "model": Error,
            "description": _ERROR_DESCRIPTIONS[code],
        }
        for code in codes
    }


def _error_response(
    status_code: int,
    code: ErrorCode,
    message: str,
    *,
    details: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = Error(
        error=ErrorBody(
            code=code,
            message=message,
            details=details,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json", exclude_none=True),
        headers=headers,
    )


def _expects_json(request: Request) -> bool:
    return any(
        request.method == method and pattern.fullmatch(request.url.path)
        for method, pattern in _JSON_METHOD_PATHS
    )


def _has_json_content_type(request: Request) -> bool:
    content_type = request.headers.get("content-type", "")
    media_type = content_type.split(";", 1)[0].strip().casefold()
    return media_type == "application/json" or (
        media_type.startswith("application/") and media_type.endswith("+json")
    )


def _reject_json_constant(value: str) -> NoReturn:
    raise ValueError(f"invalid JSON constant: {value}")


async def _validate_json_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if not _expects_json(request):
        return await call_next(request)
    if not _has_json_content_type(request):
        return _error_response(
            status.HTTP_400_BAD_REQUEST,
            "invalid_json",
            "request Content-Type must be application/json",
        )

    try:
        text = (await request.body()).decode("utf-8")
        json.loads(text, parse_constant=_reject_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _error_response(
            status.HTTP_400_BAD_REQUEST,
            "invalid_json",
            "request body must be valid UTF-8 JSON",
        )
    return await call_next(request)


def _parse_completed_query(value: object) -> bool | None:
    if value is None:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError("completed must be true or false")


def _parse_task_id(value: object) -> int:
    if (
        not isinstance(value, str)
        or not value
        or not value.isascii()
        or not value.isdecimal()
    ):
        raise ValueError("task ID must be a positive integer")
    task_id = int(value)
    if task_id <= 0:
        raise ValueError("task ID must be a positive integer")
    return task_id


CompletedQuery = Annotated[
    bool | None,
    BeforeValidator(_parse_completed_query),
    Query(description="Filter by completion state."),
]
TaskId = Annotated[
    int,
    BeforeValidator(_parse_task_id),
    Path(alias="taskId", ge=1, description="A positive task ID."),
]


def _validation_message(error: dict[str, Any]) -> tuple[str, dict[str, object]]:
    location = error.get("loc", ())
    field = next(
        (
            item
            for item in reversed(location)
            if item in {"title", "completed", "taskId"}
        ),
        "request",
    )
    error_type = error.get("type", "")

    if field == "taskId":
        return "task ID must be a positive integer", {"field": "id"}
    if field == "completed":
        if location and location[0] == "query":
            return "completed must be true or false", {"field": "completed"}
        return "completed must be a Boolean", {"field": "completed"}
    if field == "title":
        if error_type == "missing":
            return "title is required", {"field": "title"}
        if error_type in {"string_too_short", "string_too_long"}:
            return (
                "title must contain between 1 and 120 characters",
                {"field": "title"},
            )
        return "title must be a string", {"field": "title"}
    if error_type == "extra_forbidden" and location:
        unknown = str(location[-1])
        return f"unknown property: {unknown}", {"field": unknown}
    return "request body must be a JSON object", {"field": "request"}


def _task_error_response(error: TaskError) -> JSONResponse:
    if error.code == "validation_error":
        return _error_response(
            _UNPROCESSABLE_STATUS,
            error.code,
            error.message,
            details=error.details or None,
        )
    if error.code == "not_found":
        return _error_response(
            status.HTTP_404_NOT_FOUND,
            error.code,
            error.message,
            details=error.details or None,
        )

    logger.error(
        "Task service failed",
        exc_info=(type(error), error, error.__traceback__),
    )
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "internal_error",
        _INTERNAL_MESSAGE,
    )


def _install_openapi_schema(app: FastAPI) -> None:
    schema = app.openapi()
    components = schema.get("components", {}).get("schemas", {})
    update_schema = components.get("UpdateTask")
    if isinstance(update_schema, dict):
        update_schema["minProperties"] = 1

    list_operation = schema.get("paths", {}).get("/tasks", {}).get("get", {})
    parameters = list_operation.get("parameters", [])
    for parameter in parameters:
        if isinstance(parameter, dict) and parameter.get("name") == "completed":
            parameter["schema"] = {"type": "boolean"}
    app.openapi_schema = schema


def create_app(service: TaskService) -> FastAPI:
    """Create an application whose service dependency is process-owned."""

    app = FastAPI(
        title="Task REST API",
        version="1.0.0",
        description=(
            "A small framework-neutral task contract used by the applied REST project."
        ),
        servers=[{"url": "http://127.0.0.1:8000"}],
        redirect_slashes=False,
    )

    def provide_task_service() -> TaskService:
        return service

    Service = Annotated[TaskService, Depends(provide_task_service)]
    app.middleware("http")(_validate_json_request)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        del request
        errors = error.errors()
        first_error = next(
            (
                validation_error
                for validation_error in errors
                if validation_error.get("type") == "extra_forbidden"
            ),
            errors[0],
        )
        if first_error.get("type") == "json_invalid":
            return _error_response(
                status.HTTP_400_BAD_REQUEST,
                "invalid_json",
                "request body must be valid UTF-8 JSON",
            )
        message, details = _validation_message(first_error)
        return _error_response(
            _UNPROCESSABLE_STATUS,
            "validation_error",
            message,
            details=details,
        )

    @app.exception_handler(TaskError)
    async def handle_task_error(
        request: Request,
        error: TaskError,
    ) -> JSONResponse:
        del request
        return _task_error_response(error)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request,
        error: HTTPException,
    ) -> JSONResponse:
        del request
        if error.status_code == status.HTTP_404_NOT_FOUND:
            return _error_response(
                status.HTTP_404_NOT_FOUND,
                "not_found",
                "path was not found",
            )
        if error.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            return _error_response(
                status.HTTP_405_METHOD_NOT_ALLOWED,
                "method_not_allowed",
                "method is not allowed for this path",
                headers=dict(error.headers or {}),
            )
        logger.error(
            "Unexpected framework HTTP error",
            exc_info=(type(error), error, error.__traceback__),
        )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            _INTERNAL_MESSAGE,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        del request
        logger.error(
            "Unexpected Task API failure",
            exc_info=(type(error), error, error.__traceback__),
        )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            _INTERNAL_MESSAGE,
        )

    @app.get(
        "/health",
        operation_id="getHealth",
        response_model=Health,
        responses=_error_responses(405, 500),
        summary="Check server readiness",
    )
    def get_health() -> Health:
        return Health(status="ok")

    @app.post(
        "/tasks",
        operation_id="createTask",
        response_model=Task,
        status_code=status.HTTP_201_CREATED,
        responses=_error_responses(400, 405, 422, 500),
        summary="Create an incomplete task",
    )
    def create_task(body: CreateTask, task_service: Service) -> Task:
        return Task.model_validate(task_service.create_task(body.title))

    @app.get(
        "/tasks",
        operation_id="listTasks",
        response_model=list[Task],
        responses=_error_responses(405, 422, 500),
        summary="List tasks",
    )
    def list_tasks(
        request: Request,
        task_service: Service,
        completed: CompletedQuery = None,
    ) -> list[Task]:
        if len(request.query_params.getlist("completed")) > 1:
            raise ValidationError(
                "completed must appear at most once",
                field="completed",
            )
        return [
            Task.model_validate(task)
            for task in task_service.list_tasks(completed=completed)
        ]

    @app.get(
        "/tasks/{taskId}",
        operation_id="getTask",
        response_model=Task,
        responses=_error_responses(404, 405, 422, 500),
        summary="Get one task",
    )
    def get_task(task_id: TaskId, task_service: Service) -> Task:
        return Task.model_validate(task_service.get_task(task_id))

    @app.patch(
        "/tasks/{taskId}",
        operation_id="updateTask",
        response_model=Task,
        responses=_error_responses(400, 404, 405, 422, 500),
        summary="Update a task",
    )
    def update_task(
        body: UpdateTask,
        task_id: TaskId,
        task_service: Service,
    ) -> Task:
        title: object = UNSET
        completed_value: object = UNSET
        if "title" in body.model_fields_set:
            title = body.title
        if "completed" in body.model_fields_set:
            completed_value = body.completed
        return Task.model_validate(
            task_service.update_task(
                task_id,
                title=title,
                completed=completed_value,
            )
        )

    @app.delete(
        "/tasks/{taskId}",
        operation_id="deleteTask",
        response_class=Response,
        status_code=status.HTTP_204_NO_CONTENT,
        responses=_error_responses(404, 405, 422, 500),
        summary="Delete a task",
    )
    def delete_task(task_id: TaskId, task_service: Service) -> Response:
        task_service.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    _install_openapi_schema(app)
    return app


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """Run the local learning application with Uvicorn."""

    uvicorn.run(
        create_app(service),
        host=host,
        port=port,
        log_level="info",
    )
    raise SystemExit(0)


__all__ = ["create_app", "serve"]
