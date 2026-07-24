"""
Exercises: Chapter 16 - HTTP Fundamentals and the Standard Library

Implement a pure request/response boundary, URL routing, and one in-memory
BaseHTTPRequestHandler adapter. No evaluator check opens a socket.

Run from the repository root:

    python exercises/16_http_fundamentals_and_stdlib/exercises.py
"""

import io
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from email.message import Message
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler


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


@dataclass(frozen=True)
class ParsedTarget:
    route: str | None
    task_id: int | None
    completed: bool | None


TASKS = [
    {"id": 1, "title": "Read HTTP", "completed": True},
    {"id": 2, "title": "Write bytes", "completed": False},
]


def header_value(headers: Mapping[str, str], name: str) -> str | None:
    """Return one case-insensitive HTTP field value, or None."""
    # TODO: compare field names case-insensitively
    raise NotImplementedError


def json_response(
    status: HTTPStatus,
    payload: object,
    *,
    allow: str | None = None,
) -> HttpResponse:
    """Serialize compact UTF-8 JSON and set representation headers."""
    # TODO: encode JSON, count bytes, and optionally add Allow
    raise NotImplementedError


def parse_target(target: str) -> ParsedTarget:
    """Parse the supported local paths and strict completed query."""
    # TODO: use urlsplit() and parse_qs(); preserve repeated query values
    raise NotImplementedError


def dispatch_request(request: HttpRequest) -> HttpResponse:
    """Route one pure request and return one complete response."""
    # TODO: implement /health, /tasks, and /tasks/<id> behavior
    raise NotImplementedError


class TaskRequestHandler(BaseHTTPRequestHandler):
    """Adapt http.server request state to dispatch_request()."""

    def do_GET(self) -> None:
        # TODO: map command/path/headers, dispatch, and send the response
        raise NotImplementedError

    def send_http_response(self, response: HttpResponse) -> None:
        # TODO: send status, headers, end_headers(), then body bytes
        raise NotImplementedError

    def log_message(self, format: str, *args: object) -> None:
        del format, args


def _decode_json_body(response: HttpResponse) -> object:
    assert header_value(response.headers, "content-type") == (
        "application/json; charset=utf-8"
    )
    assert response.headers["Content-Length"] == str(len(response.body))
    return json.loads(response.body.decode("utf-8"))


def _run_get_handler(target: str) -> bytes:
    handler = object.__new__(TaskRequestHandler)
    handler.command = "GET"
    handler.path = target
    handler.request_version = "HTTP/1.1"
    handler.requestline = f"GET {target} HTTP/1.1"
    handler.client_address = ("127.0.0.1", 12345)
    handler.headers = Message()
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()
    handler.close_connection = True
    handler.do_GET()
    return handler.wfile.getvalue()


def _parse_raw_response(raw: bytes) -> tuple[int, dict[str, str], bytes]:
    header_bytes, body = raw.split(b"\r\n\r\n", 1)
    lines = header_bytes.decode("iso-8859-1").splitlines()
    status = int(lines[0].split(" ", 2)[1])
    headers = {
        name: value for name, value in (line.split(": ", 1) for line in lines[1:])
    }
    return status, headers, body


def evaluate_response_lifecycle() -> None:
    assert header_value({"content-type": "application/json"}, "Content-Type") == (
        "application/json"
    )
    assert header_value({"X-Trace": "abc"}, "x-trace") == "abc"
    assert header_value({}, "missing") is None

    response = json_response(
        HTTPStatus.CREATED,
        {"title": "Learn café HTTP", "completed": False},
    )
    assert response.status == HTTPStatus.CREATED
    assert response.body == ('{"title":"Learn café HTTP","completed":false}'.encode())
    assert response.headers["Content-Type"] == ("application/json; charset=utf-8")
    assert response.headers["Content-Length"] == str(len(response.body))
    assert int(response.headers["Content-Length"]) > len(response.body.decode())

    method_error = json_response(
        HTTPStatus.METHOD_NOT_ALLOWED,
        {"error": {"code": "method_not_allowed"}},
        allow="GET, POST",
    )
    assert method_error.headers["Allow"] == "GET, POST"


def evaluate_targets_and_dispatch() -> None:
    assert parse_target("/health") == ParsedTarget("health", None, None)
    assert parse_target("/tasks") == ParsedTarget("tasks", None, None)
    assert parse_target("/tasks?completed=false") == ParsedTarget(
        "tasks",
        None,
        False,
    )
    assert parse_target("/tasks/7") == ParsedTarget("task", 7, None)
    assert parse_target("/missing") == ParsedTarget(None, None, None)

    invalid_targets = [
        "/tasks?completed=",
        "/tasks?completed=True",
        "/tasks?completed=true&completed=false",
        "/tasks?unknown=value",
        "/tasks/0",
        "/tasks/not-a-number",
        "https://example.com/tasks",
        "/tasks#fragment",
    ]
    for target in invalid_targets:
        try:
            parse_target(target)
        except ValueError:
            pass
        else:
            raise AssertionError(f"target should be invalid: {target!r}")

    health = dispatch_request(HttpRequest("GET", "/health", {}))
    assert health.status == HTTPStatus.OK
    assert _decode_json_body(health) == {"status": "ok"}

    open_tasks = dispatch_request(HttpRequest("GET", "/tasks?completed=false", {}))
    assert open_tasks.status == HTTPStatus.OK
    assert _decode_json_body(open_tasks) == [TASKS[1]]

    one_task = dispatch_request(HttpRequest("GET", "/tasks/2", {}))
    assert one_task.status == HTTPStatus.OK
    assert _decode_json_body(one_task) == TASKS[1]

    missing_task = dispatch_request(HttpRequest("GET", "/tasks/99", {}))
    assert missing_task.status == HTTPStatus.NOT_FOUND

    created = dispatch_request(
        HttpRequest(
            "POST",
            "/tasks",
            {"content-type": "application/json"},
            b'{"title":"  Learn stdlib  "}',
        )
    )
    assert created.status == HTTPStatus.CREATED
    assert _decode_json_body(created) == {
        "id": 3,
        "title": "Learn stdlib",
        "completed": False,
    }

    invalid_posts = [
        HttpRequest("POST", "/tasks", {}, b'{"title":"Missing type"}'),
        HttpRequest(
            "POST",
            "/tasks",
            {"Content-Type": "text/plain"},
            b'{"title":"Wrong type"}',
        ),
        HttpRequest(
            "POST",
            "/tasks",
            {"Content-Type": "application/json"},
            b"{",
        ),
        HttpRequest(
            "POST",
            "/tasks",
            {"Content-Type": "application/json"},
            b'{"title":"","extra":true}',
        ),
    ]
    assert [dispatch_request(request).status for request in invalid_posts] == [
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.BAD_REQUEST,
    ]

    wrong_method = dispatch_request(HttpRequest("DELETE", "/tasks", {}))
    assert wrong_method.status == HTTPStatus.METHOD_NOT_ALLOWED
    assert wrong_method.headers["Allow"] == "GET, POST"

    unknown = dispatch_request(HttpRequest("GET", "/unknown", {}))
    assert unknown.status == HTTPStatus.NOT_FOUND
    nested_unknown = dispatch_request(HttpRequest("GET", "/tasks/1/extra", {}))
    assert nested_unknown.status == HTTPStatus.NOT_FOUND


def evaluate_stdlib_adapter() -> None:
    assert issubclass(TaskRequestHandler, BaseHTTPRequestHandler)

    status, headers, body = _parse_raw_response(
        _run_get_handler("/tasks?completed=true")
    )
    assert status == HTTPStatus.OK
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Content-Length"] == str(len(body))
    assert json.loads(body) == [TASKS[0]]

    missing_status, missing_headers, missing_body = _parse_raw_response(
        _run_get_handler("/unknown")
    )
    assert missing_status == HTTPStatus.NOT_FOUND
    assert missing_headers["Content-Length"] == str(len(missing_body))
    assert json.loads(missing_body)["error"]["code"] == "not_found"


def run_evaluation(label: str, evaluation: Callable[[], None]) -> None:
    try:
        evaluation()
    except NotImplementedError as error:
        raise AssertionError(f"{label}: implement the remaining TODO") from error
    print(f"{label}: OK")


if __name__ == "__main__":
    run_evaluation("response lifecycle", evaluate_response_lifecycle)
    run_evaluation("targets and dispatch", evaluate_targets_and_dispatch)
    run_evaluation("stdlib handler adapter", evaluate_stdlib_adapter)
    print("\nAll checks passed!")
