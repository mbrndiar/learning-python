"""Cross-adapter black-box contracts for the completed Task application.

The same HTTP cases run against stdlib, Flask, and FastAPI; client cases run
against urllib, Requests, and HTTPX; and the interoperability matrix combines
them.  Parametrization is the diagnostic boundary: a failure names the concrete
server/client/backend while the assertion remains one transport-neutral API
contract.  Starter runs keep parser/schema checks but skip unfinished behavior.
"""

import json
import socket
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler
from threading import Event
from types import ModuleType
from typing import ClassVar, cast

import pytest
import tasks_api.fastapi.__main__ as fastapi_server
import tasks_api.flask.__main__ as flask_server
import tasks_api.stdlib.__main__ as stdlib_server
import yaml  # type: ignore[import-untyped]
from contracts.client import invoke_client
from contracts.http import (
    assert_error_response,
    assert_json_response,
)
from implementation import IMPLEMENTATION
from openapi_spec_validator import validate  # type: ignore[import-untyped]
from support import (
    CLIENT_COMMANDS,
    PROJECT_ROOT,
    ClientName,
    LiveServer,
    ServerName,
    assert_client_parser,
    assert_server_parser,
    request_http,
    request_json,
    running_handler_server,
    running_task_server,
    temporary_project_directory,
    unavailable_loopback_url,
)
from tasks_api import ServerSettings, build_service
from tasks_cli.httpx.__main__ import build_parser as build_httpx_parser
from tasks_cli.httpx.__main__ import main as httpx_main
from tasks_cli.httpx.adapter import create_transport as create_httpx_transport
from tasks_cli.requests.__main__ import build_parser as build_requests_parser
from tasks_cli.requests.__main__ import main as requests_main
from tasks_cli.requests.adapter import create_transport as create_requests_transport
from tasks_cli.transport import (
    TaskTransport,
    TransportConnectionError,
    TransportError,
    TransportFactory,
    TransportRequest,
    TransportTimeoutError,
)
from tasks_cli.urllib.__main__ import build_parser as build_urllib_parser
from tasks_cli.urllib.__main__ import main as urllib_main
from tasks_cli.urllib.adapter import create_transport as create_urllib_transport
from tasks_core import (
    CreateTaskInput,
    StorageError,
    Task,
    UpdateTaskInput,
)
from tasks_core.repositories import SQLiteTaskRepository
from tasks_core.service import TaskService

IS_SOLUTION = IMPLEMENTATION == "solution"
solution_only = pytest.mark.skipif(
    not IS_SOLUTION,
    reason="the starter intentionally leaves server and client milestones incomplete",
)

SERVER_NAMES: tuple[ServerName, ...] = ("stdlib", "flask", "fastapi")
CLIENT_NAMES: tuple[ClientName, ...] = ("urllib", "requests", "httpx")
TRANSPORT_FACTORIES: dict[ClientName, TransportFactory] = {
    "urllib": create_urllib_transport,
    "requests": create_requests_transport,
    "httpx": create_httpx_transport,
}
CLIENT_MAINS: dict[ClientName, Callable[[list[str] | None], int]] = {
    "urllib": urllib_main,
    "requests": requests_main,
    "httpx": httpx_main,
}
SERVER_MODULES: dict[ServerName, ModuleType] = {
    "stdlib": stdlib_server,
    "flask": flask_server,
    "fastapi": fastapi_server,
}


class _FailureRepository:
    def _fail(self, operation: str) -> None:
        raise StorageError(
            f"private {operation} storage detail",
            operation=operation,
        )

    def create(self, task: CreateTaskInput) -> Task:
        del task
        self._fail("create")

    def list(self, completed: bool | None = None) -> list[Task]:
        del completed
        self._fail("list")

    def get(self, task_id: int) -> Task:
        del task_id
        self._fail("get")

    def update(self, task_id: int, update: UpdateTaskInput) -> Task:
        del task_id, update
        self._fail("update")

    def delete(self, task_id: int) -> None:
        del task_id
        self._fail("delete")


@pytest.fixture(params=SERVER_NAMES)
def live_sqlite_server(request: pytest.FixtureRequest) -> Iterator[LiveServer]:
    """Run each server against identical fresh SQLite state."""

    if not IS_SOLUTION:
        pytest.skip("solution-only black-box HTTP contract")
    server_name = cast(ServerName, request.param)
    with temporary_project_directory() as directory:
        service = TaskService(SQLiteTaskRepository(directory / "tasks.db"))
        with running_task_server(server_name, service) as server:
            yield server


@pytest.fixture(params=CLIENT_NAMES)
def transport_factory(request: pytest.FixtureRequest) -> TransportFactory:
    """Select each transport without changing the client contract body."""

    return TRANSPORT_FACTORIES[cast(ClientName, request.param)]


@solution_only
def test_http_contract_normal_crud_filter_and_204(
    live_sqlite_server: LiveServer,
) -> None:
    # This black-box sequence deliberately avoids framework test clients, so
    # status, headers, envelopes, persistence, and ID behavior share one oracle.
    base_url = live_sqlite_server.base_url
    assert_json_response(
        request_http(base_url, "GET", "/health"),
        200,
        {"status": "ok"},
    )
    assert_json_response(request_http(base_url, "GET", "/tasks"), 200, [])

    created = request_json(
        base_url,
        "POST",
        "/tasks",
        {"title": "  Learn REST 🐍  "},
    )
    expected_created = {
        "id": 1,
        "title": "Learn REST 🐍",
        "completed": False,
    }
    assert_json_response(created, 201, expected_created)
    assert_json_response(
        request_http(base_url, "GET", "/tasks?completed=false"),
        200,
        [expected_created],
    )
    assert_json_response(
        request_http(base_url, "GET", "/tasks/1"),
        200,
        expected_created,
    )

    updated = {
        "id": 1,
        "title": "Read OpenAPI",
        "completed": True,
    }
    assert_json_response(
        request_json(
            base_url,
            "PATCH",
            "/tasks/1",
            {"title": "Read OpenAPI", "completed": True},
        ),
        200,
        updated,
    )
    assert_json_response(
        request_http(base_url, "GET", "/tasks?completed=true"),
        200,
        [updated],
    )
    assert_json_response(
        request_http(base_url, "GET", "/tasks?completed=false"),
        200,
        [],
    )

    deleted = request_http(base_url, "DELETE", "/tasks/1")
    assert deleted.status == 204
    assert deleted.body == b""
    assert deleted.header("Content-Type") is None
    assert_error_response(
        request_http(base_url, "GET", "/tasks/1"),
        404,
        "not_found",
        "task 1 was not found",
    )
    assert_json_response(
        request_json(base_url, "POST", "/tasks", {"title": "Never reuse IDs"}),
        201,
        {"id": 2, "title": "Never reuse IDs", "completed": False},
    )


INVALID_BODY_CASES = (
    # Raw bytes preserve malformed inputs that higher-level JSON helpers would
    # normalize before any server implementation could inspect them.
    pytest.param(
        "POST",
        "/tasks",
        b"{}",
        {},
        400,
        "invalid_json",
        "request Content-Type must be application/json",
        None,
        id="missing-content-type",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b"{}",
        {"Content-Type": "text/plain"},
        400,
        "invalid_json",
        "request Content-Type must be application/json",
        None,
        id="unsupported-content-type",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b"{}",
        {"Content-Type": "application/json; charset=iso-8859-1"},
        400,
        "invalid_json",
        "request JSON charset must be UTF-8",
        None,
        id="unsupported-charset",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b"\xff",
        {"Content-Type": "application/json"},
        400,
        "invalid_json",
        "request body must be valid JSON",
        None,
        id="invalid-utf8",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b"{",
        {"Content-Type": "application/json"},
        400,
        "invalid_json",
        "request body must be valid JSON",
        None,
        id="malformed-json",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":"first","title":"second"}',
        {"Content-Type": "application/json"},
        400,
        "invalid_json",
        "request body must be valid JSON",
        None,
        id="duplicate-property",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":NaN}',
        {"Content-Type": "application/json"},
        400,
        "invalid_json",
        "request body must be valid JSON",
        None,
        id="non-json-constant",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b"[]",
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "request body must be a JSON object",
        {"field": "body"},
        id="wrong-body-shape",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b"{}",
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "missing property: title",
        {"field": "title"},
        id="missing-title",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":"valid","done":false}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "unknown property: done",
        {"field": "done"},
        id="unknown-property",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":null}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "title must be a string",
        {"field": "title"},
        id="null-title",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":7}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "title must be a string",
        {"field": "title"},
        id="non-string-title",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":" "}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "title must contain between 1 and 120 characters",
        {"field": "title"},
        id="empty-title",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":"first\\nsecond"}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "title must occupy one physical line",
        {"field": "title"},
        id="multiline-title",
    ),
    pytest.param(
        "POST",
        "/tasks",
        b'{"title":"control\\u0000"}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "title must not contain control characters",
        {"field": "title"},
        id="control-title",
    ),
    pytest.param(
        "POST",
        "/tasks",
        json.dumps({"title": "x" * 121}).encode(),
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "title must contain between 1 and 120 characters",
        {"field": "title"},
        id="long-title",
    ),
    pytest.param(
        "PATCH",
        "/tasks/1",
        b"{}",
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "update must include title or completed",
        {"field": "update"},
        id="empty-update",
    ),
    pytest.param(
        "PATCH",
        "/tasks/1",
        b'{"completed":0}',
        {"Content-Type": "application/json"},
        422,
        "validation_error",
        "completed must be a Boolean",
        {"field": "completed"},
        id="non-boolean-completed",
    ),
)


@solution_only
@pytest.mark.parametrize(
    (
        "method",
        "path",
        "body",
        "headers",
        "status",
        "code",
        "message",
        "details",
    ),
    INVALID_BODY_CASES,
)
def test_http_contract_rejects_invalid_json_shapes_and_values(
    live_sqlite_server: LiveServer,
    method: str,
    path: str,
    body: bytes,
    headers: dict[str, str],
    status: int,
    code: str,
    message: str,
    details: dict[str, object] | None,
) -> None:
    assert_error_response(
        request_http(
            live_sqlite_server.base_url,
            method,
            path,
            body=body,
            headers=headers,
        ),
        status,
        code,
        message,
        details=details,
    )


REQUEST_ERROR_CASES = (
    pytest.param(
        "/tasks?completed=True",
        "completed filter must be true or false",
        "completed",
        id="invalid-filter",
    ),
    pytest.param(
        "/tasks?completed=true&completed=false",
        "completed filter must be true or false",
        "completed",
        id="duplicate-filter",
    ),
    pytest.param(
        "/tasks?other=true",
        "unknown query parameter: other",
        "other",
        id="unknown-list-query",
    ),
    pytest.param(
        "/health?verbose=true",
        "unknown query parameter: verbose",
        "verbose",
        id="unexpected-health-query",
    ),
    pytest.param(
        "/tasks/0",
        "task ID must be a positive integer",
        "id",
        id="zero-id",
    ),
    pytest.param(
        "/tasks/+1",
        "task ID must be a positive integer",
        "id",
        id="signed-id",
    ),
    pytest.param(
        "/tasks/%D9%A1",
        "task ID must be a positive integer",
        "id",
        id="non-ascii-id",
    ),
)


@solution_only
@pytest.mark.parametrize(("path", "message", "field"), REQUEST_ERROR_CASES)
def test_http_contract_rejects_invalid_queries_and_ids(
    live_sqlite_server: LiveServer,
    path: str,
    message: str,
    field: str,
) -> None:
    assert_error_response(
        request_http(live_sqlite_server.base_url, "GET", path),
        422,
        "validation_error",
        message,
        details={"field": field},
    )


@solution_only
@pytest.mark.parametrize(
    ("method", "path", "allow"),
    [
        ("POST", "/health", "GET"),
        ("PUT", "/tasks", "GET, POST"),
        ("POST", "/tasks/1", "GET, PATCH, DELETE"),
    ],
)
def test_http_contract_normalizes_405_and_allow(
    live_sqlite_server: LiveServer,
    method: str,
    path: str,
    allow: str,
) -> None:
    response = request_http(live_sqlite_server.base_url, method, path)
    assert response.header("Allow") == allow
    assert_error_response(
        response,
        405,
        "method_not_allowed",
        "method is not allowed for this path",
    )


@solution_only
@pytest.mark.parametrize(
    "path",
    ["/missing", "/tasks/", "/tasks/1/extra", "/docs", "/openapi.json"],
)
def test_http_contract_normalizes_unknown_routes(
    live_sqlite_server: LiveServer,
    path: str,
) -> None:
    assert_error_response(
        request_http(live_sqlite_server.base_url, "GET", path),
        404,
        "not_found",
        "route was not found",
    )


@solution_only
@pytest.mark.parametrize("server_name", SERVER_NAMES)
def test_http_contract_sanitizes_internal_failures(server_name: ServerName) -> None:
    # One injected repository failure proves each framework maps private storage
    # diagnostics to the same public 500 envelope.
    service = TaskService(_FailureRepository())
    with running_task_server(server_name, service) as server:
        response = request_http(server.base_url, "GET", "/tasks")

    assert_error_response(
        response,
        500,
        "internal_error",
        "the server could not complete the request",
    )
    assert b"private" not in response.body


@solution_only
@pytest.mark.parametrize("server_name", SERVER_NAMES)
def test_loopback_cleanup_runs_during_assertion_failure(
    server_name: ServerName,
) -> None:
    # The deliberate test-body failure exercises context-manager unwinding, not
    # the normal success path; a second close confirms cleanup is idempotent.
    with temporary_project_directory() as directory:
        service = TaskService(SQLiteTaskRepository(directory / "tasks.db"))
        server: LiveServer | None = None
        try:
            with running_task_server(server_name, service) as active_server:
                server = active_server
                assert active_server.thread.is_alive()
                raise AssertionError("forced test-body failure")
        except AssertionError as error:
            assert str(error) == "forced test-body failure"

        assert server is not None
        assert server.closed
        assert not server.thread.is_alive()
        parsed_port = int(server.base_url.rsplit(":", 1)[1])
        with pytest.raises(OSError):
            socket.create_connection(("127.0.0.1", parsed_port), timeout=0.1)
        server.close()


class _RecordingHandler(BaseHTTPRequestHandler):
    requests: ClassVar[list[tuple[str, bytes, str | None]]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        type(self).requests.append(
            (
                self.path,
                self.rfile.read(length),
                self.headers.get("Content-Type"),
            )
        )
        body = b'{"error":{"code":"validation_error","message":"captured"}}'
        self.send_response(422)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


@solution_only
def test_client_transport_contract_sends_json_and_captures_errors(
    transport_factory: TransportFactory,
) -> None:
    # A single controlled peer makes encoding/status behavior comparable across
    # all libraries and localizes failures to the transport fixture parameter.
    _RecordingHandler.requests.clear()
    with running_handler_server(_RecordingHandler) as server:
        transport = transport_factory(f"{server.base_url}/api", 1.0)
        try:
            response = transport.send(
                TransportRequest(
                    "POST",
                    "/tasks",
                    query={"completed": "false"},
                    json_body={"title": "Learn clients 🐍"},
                )
            )
        finally:
            transport.close()

    assert response.status == 422
    assert response.headers
    assert json.loads(response.body) == {
        "error": {"code": "validation_error", "message": "captured"}
    }
    path, body, content_type = _RecordingHandler.requests.pop()
    assert path == "/api/tasks?completed=false"
    assert json.loads(body) == {"title": "Learn clients 🐍"}
    assert content_type is not None
    assert content_type.split(";", 1)[0] == "application/json"
    with pytest.raises(TransportError):
        transport.send(TransportRequest("GET", "/health"))
    transport.close()


class _MalformedHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"not-json"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


class _CapturingFactory:
    def __init__(self, factory: TransportFactory) -> None:
        self.factory = factory
        self.transport: TaskTransport | None = None

    def __call__(self, base_url: str, timeout: float) -> TaskTransport:
        self.transport = self.factory(base_url, timeout)
        return self.transport


@solution_only
def test_client_transport_contract_closes_after_malformed_response(
    transport_factory: TransportFactory,
) -> None:
    capturing_factory = _CapturingFactory(transport_factory)
    with running_handler_server(_MalformedHandler) as server:
        result = invoke_client(capturing_factory, server.base_url, ["list"])

    assert result[0] == 4
    assert result[1] == ""
    assert result[2].startswith("malformed-response: ")
    assert capturing_factory.transport is not None
    with pytest.raises(TransportError):
        capturing_factory.transport.send(TransportRequest("GET", "/health"))


@solution_only
def test_client_transport_contract_translates_connection_failures(
    transport_factory: TransportFactory,
) -> None:
    with unavailable_loopback_url() as base_url:
        transport = transport_factory(base_url, 0.2)
        try:
            with pytest.raises(TransportConnectionError):
                transport.send(TransportRequest("GET", "/health"))
        finally:
            transport.close()


class _SlowHandler(BaseHTTPRequestHandler):
    started: ClassVar[Event] = Event()
    release: ClassVar[Event] = Event()
    completed: ClassVar[Event] = Event()

    def do_GET(self) -> None:
        type(self).started.set()
        type(self).release.wait(timeout=2)
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"[]")
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            type(self).completed.set()

    def log_message(self, format: str, *args: object) -> None:
        del format, args


@solution_only
def test_client_transport_contract_uses_finite_timeouts(
    transport_factory: TransportFactory,
) -> None:
    # Per-test Events prevent state leakage between transport parameters.  The
    # handler is released in finally so timeout verification cannot strand it.
    _SlowHandler.started = Event()
    _SlowHandler.release = Event()
    _SlowHandler.completed = Event()
    with running_handler_server(_SlowHandler) as server:
        transport = transport_factory(server.base_url, 0.05)
        try:
            with pytest.raises(TransportTimeoutError):
                transport.send(TransportRequest("GET", "/tasks"))
            assert _SlowHandler.started.wait(timeout=1)
        finally:
            _SlowHandler.release.set()
            assert _SlowHandler.completed.wait(timeout=2)
            transport.close()


def test_all_server_and_client_entrypoints_parse_documented_options() -> None:
    for module in SERVER_MODULES.values():
        assert_server_parser(module.build_parser())
    for parser_factory in (
        build_urllib_parser,
        build_requests_parser,
        build_httpx_parser,
    ):
        assert_client_parser(parser_factory())
    assert CLIENT_COMMANDS


@solution_only
@pytest.mark.parametrize("server_name", SERVER_NAMES)
@pytest.mark.parametrize(
    ("backend", "filename"),
    [("sqlite", "tasks.db"), ("markdown", "tasks.md")],
)
def test_server_entrypoints_select_each_backend(
    server_name: ServerName,
    backend: str,
    filename: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Replacing only ``serve`` tests CLI composition without starting a second
    # lifecycle; the persisted file proves the requested backend reached service.
    module = SERVER_MODULES[server_name]
    with temporary_project_directory() as directory:
        data = directory / filename

        def fake_serve(service: TaskService, host: str, port: int) -> None:
            assert host == "127.0.0.1"
            assert port == 8765
            assert service.create_task(f"{server_name}-{backend}").id == 1

        monkeypatch.setattr(module, "serve", fake_serve)
        assert (
            module.main(
                [
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8765",
                    "--backend",
                    backend,
                    "--data",
                    str(data),
                ]
            )
            == 0
        )
        assert data.exists()


@solution_only
@pytest.mark.parametrize("server_name", SERVER_NAMES)
@pytest.mark.parametrize("client_name", CLIENT_NAMES)
def test_sqlite_client_server_interoperability_matrix(
    server_name: ServerName,
    client_name: ClientName,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Every client/server pair receives the same commands and assertions.  A
    # failing node therefore identifies an interoperability seam, not test drift.
    client_main = CLIENT_MAINS[client_name]
    with temporary_project_directory() as directory:
        service = build_service(
            ServerSettings(
                "127.0.0.1",
                0,
                "sqlite",
                directory / "tasks.db",
            )
        )
        with running_task_server(server_name, service) as server:
            assert (
                client_main(
                    [
                        "--base-url",
                        server.base_url,
                        "--timeout",
                        "2",
                        "add",
                        f"{client_name} to {server_name}",
                    ]
                )
                == 0
            )
            created = json.loads(capsys.readouterr().out)
            assert created == {
                "id": 1,
                "title": f"{client_name} to {server_name}",
                "completed": False,
            }

            assert (
                client_main(
                    [
                        "--base-url",
                        server.base_url,
                        "--timeout",
                        "2",
                        "complete",
                        "1",
                    ]
                )
                == 0
            )
            completed = json.loads(capsys.readouterr().out)
            assert completed["completed"] is True


@solution_only
@pytest.mark.parametrize(
    ("server_name", "client_name"),
    [
        ("stdlib", "urllib"),
        ("flask", "requests"),
        ("fastapi", "httpx"),
    ],
)
def test_matching_client_server_markdown_smoke(
    server_name: ServerName,
    client_name: ClientName,
) -> None:
    # The full 3x3 matrix uses SQLite; these representative pairs add coverage
    # that wire compatibility also survives the alternate persistence format.
    with temporary_project_directory() as directory:
        data = directory / "tasks.md"
        service = build_service(ServerSettings("127.0.0.1", 0, "markdown", data))
        with running_task_server(server_name, service) as server:
            created = invoke_client(
                TRANSPORT_FACTORIES[client_name],
                server.base_url,
                ["add", "Markdown interoperability"],
            )
            listed = invoke_client(
                TRANSPORT_FACTORIES[client_name],
                server.base_url,
                ["list"],
            )
        markdown_text = data.read_text(encoding="utf-8")

    assert created == (
        0,
        '{"id": 1, "title": "Markdown interoperability", "completed": false}\n',
        "",
    )
    assert json.loads(listed[1]) == [
        {
            "id": 1,
            "title": "Markdown interoperability",
            "completed": False,
        }
    ]
    assert listed[0] == 0
    assert listed[2] == ""
    assert markdown_text.startswith("<!-- rest-task-api:v1 next-id=2 -->")


def test_checked_in_openapi_yaml_is_valid() -> None:
    document = yaml.safe_load(
        (PROJECT_ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8")
    )
    validate(document)


@solution_only
def test_generated_fastapi_openapi_is_focused_compatible() -> None:
    from tasks_api.fastapi import create_app

    with temporary_project_directory() as directory:
        generated = create_app(
            TaskService(SQLiteTaskRepository(directory / "openapi.db"))
        ).openapi()
    intended = yaml.safe_load(
        (PROJECT_ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8")
    )
    validate(generated)

    # Generated metadata may vary by framework version, so compare only routes,
    # operations, responses, and schemas that define client compatibility.
    assert generated["openapi"] == intended["openapi"]
    assert set(generated["paths"]) == set(intended["paths"])
    for path, intended_path in intended["paths"].items():
        generated_path = generated["paths"][path]
        intended_methods = {
            method
            for method in intended_path
            if method in {"get", "post", "patch", "delete"}
        }
        assert {
            method
            for method in generated_path
            if method in {"get", "post", "patch", "delete"}
        } == intended_methods
        for method in intended_methods:
            assert (
                generated_path[method]["operationId"]
                == intended_path[method]["operationId"]
            )
            assert set(generated_path[method]["responses"]) == set(
                intended_path[method]["responses"]
            )

    schemas = generated["components"]["schemas"]
    intended_schemas = intended["components"]["schemas"]
    for name in ("Health", "Task", "CreateTask", "UpdateTask", "Error"):
        assert schemas[name]["type"] == intended_schemas[name]["type"]
        assert schemas[name]["additionalProperties"] is False
    assert schemas["UpdateTask"]["minProperties"] == 1
    assert schemas["Task"]["required"] == ["id", "title", "completed"]
    assert generated["paths"]["/tasks"]["get"]["parameters"][0]["schema"] == {
        "type": "boolean"
    }
