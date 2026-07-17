"""Milestone-three tests for the stdlib HTTP server and urllib client.

Starter-only checks keep lifecycle and command execution as explicit guided
gaps.  Solution-only checks exercise raw HTTP framing, normalized API errors,
composition, transport resource ownership, and a matching client/server flow;
later cross-framework contracts reuse these expectations at a broader level.
"""

from __future__ import annotations

import http.client
import json
import socket
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request

import pytest
import tasks_api.stdlib.__main__ as server_entrypoint
import tasks_cli.urllib.adapter as urllib_adapter
from implementation import IMPLEMENTATION
from support import (
    assert_client_parser,
    assert_server_parser,
    temporary_project_directory,
)
from tasks_api.stdlib.__main__ import build_parser as build_server_parser
from tasks_api.stdlib.__main__ import main as server_main
from tasks_api.stdlib.app import create_server
from tasks_cli.transport import (
    TransportConnectionError,
    TransportError,
    TransportRequest,
    TransportTimeoutError,
)
from tasks_cli.urllib.__main__ import build_parser as build_client_parser
from tasks_cli.urllib.__main__ import main as client_main
from tasks_cli.urllib.adapter import UrllibTransport
from tasks_core import IncompleteImplementationError, StorageError, TaskService
from tasks_core.domain import CreateTaskInput, Task, UpdateTaskInput
from tasks_core.repositories import MarkdownTaskRepository, SQLiteTaskRepository

SOLUTION_ONLY = pytest.mark.skipif(
    IMPLEMENTATION != "solution",
    reason="solution behavior is implemented after the guided starter",
)
STARTER_ONLY = pytest.mark.skipif(
    IMPLEMENTATION != "starter",
    reason="starter-specific intentional TODO behavior",
)


class _FailingRepository:
    """Inject private storage diagnostics to test logging versus wire output."""

    def create(self, task: CreateTaskInput) -> Task:
        del task
        raise StorageError("top-secret storage diagnostic", operation="create")

    def list(self, completed: bool | None = None) -> list[Task]:
        del completed
        raise StorageError("top-secret storage diagnostic", operation="list")

    def get(self, task_id: int) -> Task:
        raise StorageError(
            f"top-secret storage diagnostic for {task_id}",
            operation="get",
        )

    def update(self, task_id: int, update: UpdateTaskInput) -> Task:
        del update
        raise StorageError(
            f"top-secret storage diagnostic for {task_id}",
            operation="update",
        )

    def delete(self, task_id: int) -> None:
        raise StorageError(
            f"top-secret storage diagnostic for {task_id}",
            operation="delete",
        )


@contextmanager
def _running_server(
    storage: Path,
    *,
    repository: str = "sqlite",
    service: TaskService | None = None,
) -> Iterator[tuple[str, ThreadingHTTPServer, threading.Thread]]:
    """Own a stdlib server on an ephemeral port for the full test lifetime."""

    if service is None:
        task_repository = (
            SQLiteTaskRepository(storage)
            if repository == "sqlite"
            else MarkdownTaskRepository(storage)
        )
        service = TaskService(task_repository)
    # Port zero lets the OS allocate a free loopback listener, avoiding fixed-
    # port collisions when parametrized or parallel test runs overlap.
    server = create_server(service, "127.0.0.1", 0)
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    host, port = cast(tuple[str, int], server.server_address)
    try:
        yield f"http://{host}:{port}", server, thread
    finally:
        # Shutdown stops serve_forever, server_close releases the listener, and
        # the bounded join proves the serve-loop thread terminates. Daemon
        # request threads have no completion guarantee.
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        assert not thread.is_alive()


@contextmanager
def _running_handler(
    handler: type[BaseHTTPRequestHandler],
) -> Iterator[str]:
    """Run a controlled peer used to inject transport-level responses."""

    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    host, port = cast(tuple[str, int], server.server_address)
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        assert not thread.is_alive()


def _request(
    base_url: str,
    method: str,
    path: str,
    *,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    """Perform one finite-time request and close the owned connection."""

    parsed = urlsplit(base_url)
    assert parsed.hostname is not None
    assert parsed.port is not None
    connection = http.client.HTTPConnection(
        parsed.hostname,
        parsed.port,
        timeout=2,
    )
    try:
        connection.request(method, path, body=body, headers=dict(headers or {}))
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def _json_request(
    base_url: str,
    method: str,
    path: str,
    value: object,
) -> tuple[int, dict[str, str], bytes]:
    return _request(
        base_url,
        method,
        path,
        body=json.dumps(value, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


def _json_body(body: bytes) -> object:
    return json.loads(body.decode("utf-8"))


def _raw_request(base_url: str, request: bytes) -> tuple[int, bytes]:
    """Bypass http.client validation to probe malformed HTTP framing."""

    parsed = urlsplit(base_url)
    assert parsed.hostname is not None
    assert parsed.port is not None
    with socket.create_connection(
        (parsed.hostname, parsed.port),
        timeout=2,
    ) as connection:
        connection.sendall(request)
        response = bytearray()
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            response.extend(chunk)
    head, body = bytes(response).split(b"\r\n\r\n", 1)
    status = int(head.split(b" ", 2)[1])
    return status, body


def test_stdlib_launchers_parse_the_documented_commands() -> None:
    assert_server_parser(build_server_parser())
    assert_client_parser(build_client_parser())


@STARTER_ONLY
def test_starter_remains_guided_and_explicitly_incomplete() -> None:
    # These failures are part of the teaching contract: starter execution must
    # stop at named TODOs rather than crash later with incidental exceptions.
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 3 standard-library server lifecycle.*intentionally incomplete",
    ):
        server_main(
            (
                "--backend",
                "sqlite",
                "--data",
                "tasks.db",
                "--port",
                "0",
            )
        )

    with pytest.raises(
        IncompleteImplementationError,
        match=r"client command execution.*intentionally incomplete",
    ):
        client_main(["list"])


@SOLUTION_ONLY
def test_server_normal_crud_filter_and_not_found_flow() -> None:
    with temporary_project_directory() as directory:
        with _running_server(directory / "tasks.db") as (base_url, _, _):
            status, headers, body = _request(base_url, "GET", "/health")
            assert status == 200
            assert headers["Content-Type"] == "application/json"
            assert _json_body(body) == {"status": "ok"}

            status, _, body = _json_request(
                base_url,
                "POST",
                "/tasks",
                {"title": "  Learn REST 🐍  "},
            )
            assert status == 201
            assert _json_body(body) == {
                "id": 1,
                "title": "Learn REST 🐍",
                "completed": False,
            }

            status, _, body = _request(
                base_url,
                "GET",
                "/tasks?completed=false",
            )
            assert status == 200
            assert _json_body(body) == [
                {"id": 1, "title": "Learn REST 🐍", "completed": False}
            ]

            status, _, body = _request(base_url, "GET", "/tasks/1")
            assert status == 200
            assert _json_body(body) == {
                "id": 1,
                "title": "Learn REST 🐍",
                "completed": False,
            }

            status, _, body = _json_request(
                base_url,
                "PATCH",
                "/tasks/1",
                {"title": "Read OpenAPI", "completed": True},
            )
            assert status == 200
            assert _json_body(body) == {
                "id": 1,
                "title": "Read OpenAPI",
                "completed": True,
            }

            status, _, body = _request(
                base_url,
                "GET",
                "/tasks?completed=false",
            )
            assert status == 200
            assert _json_body(body) == []

            status, headers, body = _request(base_url, "DELETE", "/tasks/1")
            assert status == 204
            assert headers["Content-Length"] == "0"
            assert body == b""

            status, _, body = _request(base_url, "GET", "/tasks/1")
            assert status == 404
            assert _json_body(body) == {
                "error": {
                    "code": "not_found",
                    "message": "task 1 was not found",
                }
            }


@SOLUTION_ONLY
def test_server_rejects_malformed_oversized_and_semantic_bodies() -> None:
    # The byte-level cases separate JSON transport failures (400) from valid
    # JSON that violates domain/request shape (422).
    cases = (
        (b"{}", {}, "request Content-Type must be application/json"),
        (
            b"{}",
            {"Content-Type": "text/plain"},
            "request Content-Type must be application/json",
        ),
        (
            b"{}",
            {"Content-Type": "application/json; charset=iso-8859-1"},
            "request JSON charset must be UTF-8",
        ),
        (
            b"\xff",
            {"Content-Type": "application/json"},
            "request body must be valid JSON",
        ),
        (
            b"{",
            {"Content-Type": "application/json"},
            "request body must be valid JSON",
        ),
        (
            b'{"title":"first","title":"second"}',
            {"Content-Type": "application/json"},
            "request body must be valid JSON",
        ),
    )

    with temporary_project_directory() as directory:
        with _running_server(directory / "tasks.db") as (base_url, _, _):
            for body, headers, message in cases:
                status, _, response_body = _request(
                    base_url,
                    "POST",
                    "/tasks",
                    body=body,
                    headers=headers,
                )
                assert status == 400
                assert _json_body(response_body) == {
                    "error": {"code": "invalid_json", "message": message}
                }

            status, _, body = _request(
                base_url,
                "POST",
                "/tasks",
                body=b"x" * (64 * 1024 + 1),
                headers={"Content-Type": "application/json"},
            )
            assert status == 400
            assert _json_body(body) == {
                "error": {
                    "code": "invalid_json",
                    "message": "request body is too large",
                }
            }

            status, _, body = _json_request(base_url, "POST", "/tasks", [])
            assert status == 422
            assert _json_body(body) == {
                "error": {
                    "code": "validation_error",
                    "message": "request body must be a JSON object",
                    "details": {"field": "body"},
                }
            }

            status, _, body = _json_request(
                base_url,
                "POST",
                "/tasks",
                {"title": "valid", "done": False},
            )
            assert status == 422
            assert _json_body(body) == {
                "error": {
                    "code": "validation_error",
                    "message": "unknown property: done",
                    "details": {"field": "done"},
                }
            }


@SOLUTION_ONLY
def test_server_requires_one_valid_content_length() -> None:
    # A raw socket is required because normal HTTP clients repair or reject the
    # malformed Content-Length headers before the server can observe them.
    with temporary_project_directory() as directory:
        with _running_server(directory / "tasks.db") as (base_url, _, _):
            status, body = _raw_request(
                base_url,
                (
                    b"POST /tasks HTTP/1.0\r\n"
                    b"Host: 127.0.0.1\r\n"
                    b"Content-Type: application/json\r\n"
                    b"\r\n"
                    b'{"title":"missing length"}'
                ),
            )
            assert status == 400
            assert _json_body(body) == {
                "error": {
                    "code": "invalid_json",
                    "message": "request body must include one Content-Length",
                }
            }

            status, body = _raw_request(
                base_url,
                (
                    b"POST /tasks HTTP/1.0\r\n"
                    b"Host: 127.0.0.1\r\n"
                    b"Content-Type: application/json\r\n"
                    b"Content-Length: invalid\r\n"
                    b"\r\n"
                ),
            )
            assert status == 400
            assert _json_body(body) == {
                "error": {
                    "code": "invalid_json",
                    "message": "request Content-Length was invalid",
                }
            }


@SOLUTION_ONLY
def test_server_enforces_methods_routes_ids_and_query_filter() -> None:
    with temporary_project_directory() as directory:
        with _running_server(directory / "tasks.db") as (base_url, _, _):
            status, headers, body = _request(base_url, "PUT", "/tasks")
            assert status == 405
            assert headers["Allow"] == "GET, POST"
            assert _json_body(body) == {
                "error": {
                    "code": "method_not_allowed",
                    "message": "method is not allowed for this path",
                }
            }

            status, headers, _ = _request(base_url, "POST", "/tasks/1")
            assert status == 405
            assert headers["Allow"] == "GET, PATCH, DELETE"

            for path in ("/missing", "/tasks/", "/tasks/1/extra"):
                status, _, body = _request(base_url, "GET", path)
                assert status == 404
                assert _json_body(body)["error"]["code"] == "not_found"

            for path, field in (
                ("/tasks/nope", "id"),
                ("/tasks/+1", "id"),
                ("/tasks/%D9%A1", "id"),
                ("/tasks?completed=yes", "completed"),
                ("/tasks?completed=true&completed=false", "completed"),
                ("/tasks?other=true", "other"),
                ("/health?verbose=true", "verbose"),
            ):
                status, _, body = _request(base_url, "GET", path)
                assert status == 422
                assert _json_body(body)["error"]["details"] == {"field": field}


@SOLUTION_ONLY
def test_server_logs_storage_details_but_sanitizes_internal_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Operators need the injected diagnostic in logs, while clients receive a
    # stable envelope that cannot disclose backend or credential details.
    caplog.set_level("ERROR", logger="tasks_api.stdlib.app")
    service = TaskService(_FailingRepository())
    with temporary_project_directory() as directory:
        with _running_server(
            directory / "unused.db",
            service=service,
        ) as (base_url, _, _):
            status, _, body = _request(base_url, "GET", "/tasks")

    assert status == 500
    assert _json_body(body) == {
        "error": {
            "code": "internal_error",
            "message": "the server could not complete the request",
        }
    }
    assert b"top-secret" not in body
    assert "top-secret storage diagnostic" in caplog.text


@SOLUTION_ONLY
@pytest.mark.parametrize("repository", ["sqlite", "markdown"])
def test_server_composition_root_selects_storage(
    repository: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with temporary_project_directory() as directory:
        suffix = ".db" if repository == "sqlite" else ".md"
        storage = directory / f"tasks{suffix}"

        def fake_serve(service: TaskService, host: str, port: int) -> None:
            assert host == "127.0.0.1"
            assert port == 0
            service.create_task(f"{repository} task")

        monkeypatch.setattr(server_entrypoint, "serve", fake_serve)
        assert (
            server_main(
                (
                    "--backend",
                    repository,
                    "--data",
                    str(storage),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "0",
                )
            )
            == 0
        )

        task_repository = (
            SQLiteTaskRepository(storage)
            if repository == "sqlite"
            else MarkdownTaskRepository(storage)
        )
        assert task_repository.list() == [
            Task(id=1, title=f"{repository} task", completed=False)
        ]


@SOLUTION_ONLY
def test_matching_urllib_cli_runs_normal_and_api_failure_flows(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with temporary_project_directory() as directory:
        with _running_server(directory / "tasks.db") as (base_url, _, _):
            commands = (
                (
                    ("add", "Learn urllib"),
                    {"id": 1, "title": "Learn urllib", "completed": False},
                ),
                (
                    ("list", "--completed", "false"),
                    [{"id": 1, "title": "Learn urllib", "completed": False}],
                ),
                (
                    ("show", "1"),
                    {"id": 1, "title": "Learn urllib", "completed": False},
                ),
                (
                    (
                        "update",
                        "1",
                        "--title",
                        "Close responses",
                        "--completed",
                        "false",
                    ),
                    {"id": 1, "title": "Close responses", "completed": False},
                ),
                (
                    ("complete", "1"),
                    {"id": 1, "title": "Close responses", "completed": True},
                ),
                (("remove", "1"), {"deleted": 1}),
            )
            for command, expected in commands:
                assert client_main(["--base-url", base_url, *command]) == 0
                captured = capsys.readouterr()
                assert json.loads(captured.out) == expected
                assert captured.err == ""

            assert client_main(["--base-url", base_url, "show", "1"]) == 3
            captured = capsys.readouterr()
            assert captured.out == ""
            assert captured.err == "api: 404 not_found: task 1 was not found\n"


@SOLUTION_ONLY
def test_urllib_opener_explicitly_disables_ambient_proxies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = object()
    handlers: tuple[object, ...] = ()

    class RecordingOpener:
        def open(self, request: object, *, timeout: float) -> object:
            assert isinstance(request, Request)
            assert timeout == 1.0
            return marker

    def record_build_opener(*configured: object) -> RecordingOpener:
        nonlocal handlers
        handlers = configured
        return RecordingOpener()

    monkeypatch.setattr(urllib_adapter, "build_opener", record_build_opener)

    response = urllib_adapter._open(Request("http://127.0.0.1/tasks"), 1.0)

    proxy_handlers = [
        handler for handler in handlers if isinstance(handler, ProxyHandler)
    ]
    assert response is marker
    assert len(proxy_handlers) == 1
    assert proxy_handlers[0].proxies == {}


@SOLUTION_ONLY
def test_urllib_transport_encodes_url_body_and_captures_http_error() -> None:
    recorded: dict[str, object] = {}

    class RecordingHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers["Content-Length"])
            recorded.update(
                {
                    "path": self.path,
                    "content_type": self.headers["Content-Type"],
                    "accept": self.headers["Accept"],
                    "body": self.rfile.read(length),
                }
            )
            body = b'{"error":{"code":"validation_error","message":"recorded"}}'
            self.send_response(422)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            del format, args

    with _running_handler(RecordingHandler) as base_url:
        transport = UrllibTransport(base_url, 1.0)
        response = transport.send(
            TransportRequest(
                "POST",
                "/echo path",
                query={"filter name": "a/b & c"},
                json_body={"title": "Unicode 🐍"},
            )
        )
        transport.close()

    assert recorded == {
        "path": "/echo%20path?filter%20name=a%2Fb%20%26%20c",
        "content_type": "application/json",
        "accept": "application/json",
        "body": '{"title":"Unicode 🐍"}'.encode(),
    }
    assert response.status == 422
    assert _json_body(response.body)["error"]["code"] == "validation_error"


@SOLUTION_ONLY
def test_urllib_transport_closes_responses_and_translates_library_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResponse:
        status = 200

        def __init__(self) -> None:
            self.headers = Message()
            self.headers["Content-Type"] = "application/json"
            self.closed = False

        def read(self) -> bytes:
            return b"[]"

        def close(self) -> None:
            self.closed = True

    # Monkeypatch the narrow open seam so response ownership and exception
    # translation are tested without depending on urllib's network stack.
    response = FakeResponse()
    monkeypatch.setattr(
        urllib_adapter,
        "_open",
        lambda request, timeout: response,
    )
    transport = UrllibTransport("http://127.0.0.1:8000", 1.0)
    assert transport.send(TransportRequest("GET", "/tasks")).body == b"[]"
    assert response.closed
    transport.close()
    with pytest.raises(TransportError, match="transport is closed"):
        transport.send(TransportRequest("GET", "/tasks"))

    def timeout_error(request: object, timeout: float) -> None:
        del request, timeout
        raise URLError(TimeoutError())

    monkeypatch.setattr(urllib_adapter, "_open", timeout_error)
    with pytest.raises(TransportTimeoutError, match="request timed out"):
        UrllibTransport("http://127.0.0.1:8000", 1.0).send(
            TransportRequest("GET", "/tasks")
        )

    def connection_error(request: object, timeout: float) -> None:
        del request, timeout
        raise URLError(OSError("connection refused"))

    monkeypatch.setattr(urllib_adapter, "_open", connection_error)
    with pytest.raises(TransportConnectionError, match="connection refused"):
        UrllibTransport("http://127.0.0.1:8000", 1.0).send(
            TransportRequest("GET", "/tasks")
        )


@SOLUTION_ONLY
def test_urllib_cli_reports_malformed_response_and_connection_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    class MalformedHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = b"not-json"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            del format, args

    with _running_handler(MalformedHandler) as base_url:
        assert client_main(["--base-url", base_url, "list"]) == 4
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "malformed-response:" in captured.err
        assert "Content-Type" in captured.err

    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    _, unused_port = cast(tuple[str, int], probe.getsockname())
    probe.close()
    assert (
        client_main(
            [
                "--base-url",
                f"http://127.0.0.1:{unused_port}",
                "--timeout",
                "0.2",
                "list",
            ]
        )
        == 5
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("connection:")


@SOLUTION_ONLY
def test_loopback_shutdown_closes_socket_and_joins_thread() -> None:
    # Leaving the context is the observable lifecycle boundary: both the file
    # descriptor and worker thread must be gone before the next test starts.
    with temporary_project_directory() as directory:
        with _running_server(directory / "tasks.db") as (
            base_url,
            server,
            thread,
        ):
            assert thread.is_alive()
            assert _request(base_url, "GET", "/health")[0] == 200
        assert server.fileno() == -1
        assert not thread.is_alive()
