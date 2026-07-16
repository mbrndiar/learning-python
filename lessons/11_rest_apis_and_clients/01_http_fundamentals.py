"""
Lesson 11.1: HTTP Fundamentals

HTTP exchanges a request for a response. The protocol carries bytes; headers
describe how to interpret those bytes, such as UTF-8 JSON. This lesson models a
small boundary without starting a server or using the public network.
"""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from types import TracebackType
from typing import Protocol, Self
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request


@dataclass(frozen=True)
class HttpRequest:
    method: str
    target: str
    headers: Mapping[str, str]
    body: bytes = b""


@dataclass(frozen=True)
class HttpResponse:
    status: HTTPStatus
    headers: Mapping[str, str]
    body: bytes


TASKS = [
    {"id": 1, "title": "Read the HTTP lesson", "completed": True},
    {"id": 2, "title": "Send UTF-8 JSON", "completed": False},
]


def json_response(status: HTTPStatus, payload: object) -> HttpResponse:
    body = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return HttpResponse(
        status=status,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body)),
        },
        body=body,
    )


def error_response(
    status: HTTPStatus,
    code: str,
    message: str,
    *,
    allow: str | None = None,
) -> HttpResponse:
    response = json_response(
        status,
        {"error": {"code": code, "message": message}},
    )
    if allow is None:
        return response
    return HttpResponse(
        response.status,
        {**response.headers, "Allow": allow},
        response.body,
    )


def header_value(headers: Mapping[str, str], name: str) -> str | None:
    """HTTP field names are case-insensitive."""

    wanted = name.casefold()
    return next(
        (value for key, value in headers.items() if key.casefold() == wanted),
        None,
    )


def decode_json_object(request: HttpRequest) -> dict[str, object]:
    content_type = header_value(request.headers, "Content-Type")
    if content_type is None or content_type.split(";", 1)[0].strip() != (
        "application/json"
    ):
        raise ValueError("Content-Type must be application/json")

    try:
        text = request.body.decode("utf-8")
        value: object = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("body must contain UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise ValueError("JSON body must be an object")
    return value


def parse_completed_query(target: str) -> bool | None:
    query = parse_qs(urlsplit(target).query, keep_blank_values=True)
    unknown = set(query) - {"completed"}
    if unknown:
        raise ValueError(f"unknown query field: {min(unknown)}")
    values = query.get("completed")
    if values is None:
        return None
    if values == ["true"]:
        return True
    if values == ["false"]:
        return False
    raise ValueError("completed must appear once as true or false")


def handle_request(request: HttpRequest) -> HttpResponse:
    """A minimal request/response boundary with visible routing decisions."""

    path = urlsplit(request.target).path
    method = request.method.upper()

    if path == "/health":
        if method != "GET":
            return error_response(
                HTTPStatus.METHOD_NOT_ALLOWED,
                "method_not_allowed",
                "method is not allowed for this path",
                allow="GET",
            )
        return json_response(HTTPStatus.OK, {"status": "ok"})

    if path == "/tasks" and method == "GET":
        try:
            completed = parse_completed_query(request.target)
        except ValueError as error:
            return error_response(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "validation_error",
                str(error),
            )
        tasks = [
            task
            for task in TASKS
            if completed is None or task["completed"] is completed
        ]
        return json_response(HTTPStatus.OK, tasks)

    if path == "/tasks" and method == "POST":
        try:
            payload = decode_json_object(request)
        except ValueError as error:
            return error_response(
                HTTPStatus.BAD_REQUEST,
                "invalid_json",
                str(error),
            )
        if set(payload) != {"title"} or not isinstance(payload["title"], str):
            return error_response(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "validation_error",
                "request must contain exactly one string title",
            )
        title = payload["title"].strip()
        if not title:
            return error_response(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "validation_error",
                "title must not be empty",
            )
        return json_response(
            HTTPStatus.CREATED,
            {"id": 3, "title": title, "completed": False},
        )

    if path == "/tasks":
        return error_response(
            HTTPStatus.METHOD_NOT_ALLOWED,
            "method_not_allowed",
            "method is not allowed for this path",
            allow="GET, POST",
        )
    return error_response(
        HTTPStatus.NOT_FOUND,
        "not_found",
        "route was not found",
    )


class ReadableResponse(Protocol):
    status: int
    headers: Mapping[str, str]

    def read(self) -> bytes:
        """Read the response body."""

    def __enter__(self) -> Self:
        """Own the response lifetime."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the response."""


class UrlOpener(Protocol):
    def open(self, request: Request, *, timeout: float) -> ReadableResponse:
        """Send one request with a finite timeout."""


def fetch_json(
    opener: UrlOpener,
    base_url: str,
    *,
    completed: bool,
    timeout: float,
) -> tuple[int, object]:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")

    query = urlencode({"completed": str(completed).lower()})
    request = Request(
        f"{base_url.rstrip('/')}/tasks?{query}",
        method="GET",
        headers={"Accept": "application/json"},
    )
    with opener.open(request, timeout=timeout) as response:
        body = response.read()
        value: object = json.loads(body.decode("utf-8"))
        return response.status, value


class FakeResponse:
    def __init__(self, status: int, body: bytes) -> None:
        self.status = status
        self.headers: Mapping[str, str] = {"Content-Type": "application/json"}
        self._body = body
        self.closed = False

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.closed = True


class FakeOpener:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.request: Request | None = None
        self.timeout: float | None = None

    def open(self, request: Request, *, timeout: float) -> ReadableResponse:
        self.request = request
        self.timeout = timeout
        return self.response


def test_http_fundamentals() -> None:
    create = handle_request(
        HttpRequest(
            "POST",
            "/tasks",
            {"content-type": "application/json"},
            json.dumps({"title": "  Learn café APIs  "}).encode("utf-8"),
        )
    )
    assert create.status == HTTPStatus.CREATED
    assert json.loads(create.body.decode("utf-8")) == {
        "id": 3,
        "title": "Learn café APIs",
        "completed": False,
    }
    assert create.headers["Content-Length"] == str(len(create.body))

    filtered = handle_request(HttpRequest("GET", "/tasks?completed=true", {}))
    assert filtered.status == HTTPStatus.OK
    assert json.loads(filtered.body) == [TASKS[0]]

    wrong_method = handle_request(HttpRequest("DELETE", "/health", {}))
    assert wrong_method.status == HTTPStatus.METHOD_NOT_ALLOWED
    assert wrong_method.headers["Allow"] == "GET"

    fake_response = FakeResponse(200, b'{"status":"ok"}')
    opener = FakeOpener(fake_response)
    status, payload = fetch_json(
        opener,
        "http://example.invalid",
        completed=False,
        timeout=1.5,
    )
    assert (status, payload) == (200, {"status": "ok"})
    assert opener.timeout == 1.5
    assert opener.request is not None
    assert opener.request.full_url.endswith("completed=false")
    assert fake_response.closed


if __name__ == "__main__":
    test_http_fundamentals()
    print("HTTP fundamentals checks passed!")
