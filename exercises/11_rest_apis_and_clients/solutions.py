"""Solutions: 11 REST APIs and HTTP Clients."""

import json
import math
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str


@dataclass(frozen=True)
class UpdateTaskCommand:
    title: str | None
    completed: bool | None


class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class StorageError(DomainError):
    pass


@dataclass(frozen=True)
class ErrorResponse:
    status: int
    body: dict[str, object]


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class TaskTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        timeout: float,
    ) -> TransportResponse:
        """Send one request."""


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


class MalformedResponse(Exception):
    pass


def normalized_title(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("title must be a string")
    title = value.strip()
    if not 1 <= len(title) <= 120:
        raise ValidationError("title must contain between 1 and 120 characters")
    if any(unicodedata.category(character) == "Cc" for character in title):
        raise ValidationError("title must not contain control characters")
    return title


def validate_create_request(value: object) -> CreateTaskCommand:
    if not isinstance(value, dict):
        raise ValidationError("request body must be an object")
    if set(value) != {"title"}:
        raise ValidationError("create requires exactly title")
    return CreateTaskCommand(normalized_title(value["title"]))


def validate_update_request(value: object) -> UpdateTaskCommand:
    if not isinstance(value, dict):
        raise ValidationError("request body must be an object")
    if not value or not set(value) <= {"title", "completed"}:
        raise ValidationError("update requires title, completed, or both")

    title = normalized_title(value["title"]) if "title" in value else None
    completed = value.get("completed")
    if "completed" in value and not isinstance(completed, bool):
        raise ValidationError("completed must be a Boolean")
    return UpdateTaskCommand(title, completed)


def parse_completed_filter(values: list[str]) -> bool | None:
    if not values:
        return None
    if values == ["true"]:
        return True
    if values == ["false"]:
        return False
    raise ValidationError("completed must appear once as true or false")


def map_domain_error(error: DomainError) -> ErrorResponse:
    if isinstance(error, ValidationError):
        status, code, message = 422, "validation_error", str(error)
    elif isinstance(error, NotFoundError):
        status, code, message = 404, "not_found", str(error)
    else:
        status = 500
        code = "internal_error"
        message = "the server could not complete the request"
    return ErrorResponse(
        status,
        {"error": {"code": code, "message": message}},
    )


def response_content_type(headers: Mapping[str, str]) -> str:
    value = next(
        (
            header_value
            for name, header_value in headers.items()
            if name.casefold() == "content-type"
        ),
        "",
    )
    return value.split(";", 1)[0].strip().casefold()


def decode_json(response: TransportResponse) -> object:
    if response_content_type(response.headers) != "application/json":
        raise MalformedResponse("expected application/json")
    try:
        value: object = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MalformedResponse("body was not UTF-8 JSON") from error
    return value


def decode_api_error(response: TransportResponse) -> ApiError:
    value = decode_json(response)
    if not isinstance(value, dict) or set(value) != {"error"}:
        raise MalformedResponse("error envelope was malformed")
    details = value["error"]
    if not isinstance(details, dict):
        raise MalformedResponse("error details were malformed")
    code = details.get("code")
    message = details.get("message")
    if not isinstance(code, str) or not isinstance(message, str):
        raise MalformedResponse("error code or message was malformed")
    return ApiError(response.status, code, message)


def decode_task_response(response: TransportResponse) -> Task:
    if response.status != 200:
        if 400 <= response.status <= 599:
            raise decode_api_error(response)
        raise MalformedResponse(f"unexpected HTTP status: {response.status}")

    value = decode_json(response)
    if not isinstance(value, dict) or set(value) != {
        "id",
        "title",
        "completed",
    }:
        raise MalformedResponse("Task fields were malformed")

    task_id = value["id"]
    title = value["title"]
    completed = value["completed"]
    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
        or not isinstance(title, str)
        or not 1 <= len(title) <= 120
        or any(unicodedata.category(character) == "Cc" for character in title)
        or not isinstance(completed, bool)
    ):
        raise MalformedResponse("Task values were malformed")
    return Task(task_id, title, completed)


def get_task(
    transport: TaskTransport,
    task_id: int,
    *,
    timeout: float = 5.0,
) -> Task:
    if task_id <= 0:
        raise ValueError("task ID must be positive")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    response = transport.request(
        "GET",
        f"/tasks/{task_id}",
        timeout=timeout,
    )
    return decode_task_response(response)


class FakeTransport:
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, str, float]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        timeout: float,
    ) -> TransportResponse:
        self.calls.append((method, path, timeout))
        return self.response


def assert_checks() -> None:
    assert validate_create_request({"title": "  Learn HTTP  "}) == CreateTaskCommand(
        "Learn HTTP"
    )
    assert validate_update_request(
        {"title": "  Ship API  ", "completed": True}
    ) == UpdateTaskCommand("Ship API", True)

    invalid_requests: list[tuple[object, Callable[[object], object]]] = [
        ({}, validate_create_request),
        ({"title": "ok", "done": True}, validate_create_request),
        ({"title": 3}, validate_create_request),
        ({}, validate_update_request),
        ({"completed": 1}, validate_update_request),
        ({"title": "two\nlines"}, validate_update_request),
    ]
    for value, validator in invalid_requests:
        try:
            validator(value)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"request should be invalid: {value!r}")

    assert parse_completed_filter([]) is None
    assert parse_completed_filter(["true"]) is True
    assert parse_completed_filter(["false"]) is False
    for values in (["True"], ["1"], [""], ["true", "false"]):
        try:
            parse_completed_filter(values)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"filter should be invalid: {values!r}")

    assert map_domain_error(ValidationError("bad title")) == ErrorResponse(
        422,
        {
            "error": {
                "code": "validation_error",
                "message": "bad title",
            }
        },
    )
    assert map_domain_error(NotFoundError("task 9 was not found")).status == 404
    assert map_domain_error(StorageError("database password leaked")).body == {
        "error": {
            "code": "internal_error",
            "message": "the server could not complete the request",
        }
    }

    response = TransportResponse(
        200,
        {"Content-Type": "application/json; charset=utf-8"},
        b'{"id":1,"title":"Learn HTTP","completed":false}',
    )
    transport = FakeTransport(response)
    assert get_task(transport, 1, timeout=1.25) == Task(
        1,
        "Learn HTTP",
        False,
    )
    assert transport.calls == [("GET", "/tasks/1", 1.25)]

    for invalid_timeout in (0.0, -1.0, math.inf):
        try:
            get_task(transport, 1, timeout=invalid_timeout)
        except ValueError:
            pass
        else:
            raise AssertionError("timeout should be positive and finite")

    api_response = TransportResponse(
        404,
        {"Content-Type": "application/json"},
        b'{"error":{"code":"not_found","message":"missing"}}',
    )
    try:
        decode_task_response(api_response)
    except ApiError as error:
        assert (error.status, error.code) == (404, "not_found")
    else:
        raise AssertionError("documented non-success should raise ApiError")

    malformed_responses = [
        TransportResponse(
            200,
            {"Content-Type": "text/plain"},
            b"not JSON",
        ),
        TransportResponse(
            200,
            {"Content-Type": "application/json"},
            b"{",
        ),
        TransportResponse(
            200,
            {"Content-Type": "application/json"},
            b'{"id":true,"title":"Bad","completed":false}',
        ),
        TransportResponse(
            503,
            {"Content-Type": "text/plain"},
            b"unavailable",
        ),
    ]
    for malformed in malformed_responses:
        try:
            decode_task_response(malformed)
        except MalformedResponse:
            pass
        else:
            raise AssertionError("malformed response should be rejected")


if __name__ == "__main__":
    assert_checks()
    print("All checks passed!")
