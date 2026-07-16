"""
Exercises: 11 REST APIs and HTTP Clients

Implement request mapping, query parsing, error mapping, one injected transport
call, and status-first response validation. All checks are offline.
"""

import math
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


def validate_create_request(value: object) -> CreateTaskCommand:
    """Validate exactly one title field and return its normalized command."""

    # TODO: implement this function
    raise NotImplementedError


def validate_update_request(value: object) -> UpdateTaskCommand:
    """Validate a non-empty partial title/completed update."""

    # TODO: implement this function
    raise NotImplementedError


def parse_completed_filter(values: list[str]) -> bool | None:
    """Accept no value, ['true'], or ['false']; reject every other shape."""

    # TODO: implement this function
    raise NotImplementedError


def map_domain_error(error: DomainError) -> ErrorResponse:
    """Map domain errors to a status and the shared JSON error envelope."""

    # TODO: implement this function
    raise NotImplementedError


def decode_task_response(response: TransportResponse) -> Task:
    """Check status first, then validate content type, JSON, fields, and values."""

    # TODO: implement this function
    raise NotImplementedError


def get_task(
    transport: TaskTransport,
    task_id: int,
    *,
    timeout: float = 5.0,
) -> Task:
    """Make one injected transport call and validate its response."""

    # TODO: implement this function
    raise NotImplementedError


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
        TransportResponse(200, {"Content-Type": "text/plain"}, b"not JSON"),
        TransportResponse(200, {"Content-Type": "application/json"}, b"{"),
        TransportResponse(
            200,
            {"Content-Type": "application/json"},
            b'{"id":true,"title":"Bad","completed":false}',
        ),
        TransportResponse(503, {"Content-Type": "text/plain"}, b"unavailable"),
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
