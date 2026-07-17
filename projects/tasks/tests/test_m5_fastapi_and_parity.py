"""Milestone-five tests for FastAPI, HTTPX, OpenAPI, and focused parity.

The starter exposes schema scaffolding but deliberately stops at named app and
transport TODOs.  The solution checks FastAPI's normalization around Pydantic,
HTTPX ownership and error translation, generated-schema intent, and parity
between in-process TestClient calls and real loopback HTTP exchanges.
"""

import json
import socket
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any, ClassVar, cast

import pytest
import yaml  # type: ignore[import-untyped]
from fastapi.testclient import TestClient
from implementation import IMPLEMENTATION
from support import PROJECT_ROOT, running_task_server, temporary_project_directory
from tasks_api.fastapi import CreateTask, UpdateTask, create_app
from tasks_cli.httpx import HttpxTransport
from tasks_cli.httpx.__main__ import main as client_main
from tasks_cli.transport import (
    HttpMethod,
    JsonValue,
    TransportConnectionError,
    TransportError,
    TransportRequest,
    TransportResponse,
)
from tasks_core import (
    IncompleteImplementationError,
    StorageError,
    TaskService,
)
from tasks_core import (
    Task as DomainTask,
)
from tasks_core.repositories import SQLiteTaskRepository

IS_SOLUTION = IMPLEMENTATION == "solution"
solution_only = pytest.mark.skipif(
    not IS_SOLUTION,
    reason="the starter intentionally leaves milestone five incomplete",
)


def _service(path: Path) -> TaskService:
    return TaskService(SQLiteTaskRepository(path))


@contextmanager
def _client() -> Iterator[TestClient]:
    """Own app storage and the framework-specific TestClient lifecycle."""

    with temporary_project_directory() as directory:
        app = create_app(_service(directory / "tasks.db"))
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


@contextmanager
def _live_app() -> Iterator[str]:
    """Expose the same app over a real, finite-lived loopback server."""

    with temporary_project_directory() as directory:
        with running_task_server(
            "fastapi",
            _service(directory / "live.db"),
        ) as server:
            yield server.base_url


def _json(response: TransportResponse) -> object:
    return json.loads(response.body.decode("utf-8"))


def test_starter_exposes_guided_models_and_explicit_todos() -> None:
    if IS_SOLUTION:
        pytest.skip("starter-only guidance check")

    # Models are provided early so learners can inspect the target schema even
    # though application and transport execution remain deliberately incomplete.
    assert CreateTask.model_json_schema()["additionalProperties"] is False
    update_schema = UpdateTask.model_json_schema()
    assert set(update_schema["properties"]) == {"title", "completed"}

    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 5 FastAPI application factory.*intentionally incomplete",
    ):
        create_app(_service(Path("unused.db")))

    transport = HttpxTransport("http://127.0.0.1:8000", 1.0)
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 5 httpx call.*intentionally incomplete",
    ):
        transport.send(TransportRequest("GET", "/health"))


@solution_only
def test_fastapi_normal_and_boundary_flows() -> None:
    with _client() as client:
        assert client.get("/health").json() == {"status": "ok"}

        created = client.post("/tasks", json={"title": "  Learn REST  "})
        assert created.status_code == 201
        assert created.json() == {
            "id": 1,
            "title": "Learn REST",
            "completed": False,
        }

        assert client.get("/tasks?completed=false").json() == [created.json()]
        updated = client.patch("/tasks/1", json={"completed": True})
        assert updated.status_code == 200
        assert updated.json()["completed"] is True
        assert client.get("/tasks?completed=false").json() == []
        assert client.get("/tasks?completed=true").json() == [updated.json()]

        deleted = client.delete("/tasks/1")
        assert deleted.status_code == 204
        assert deleted.content == b""
        missing = client.get("/tasks/1")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "not_found"


@solution_only
def test_fastapi_applies_title_length_after_domain_trimming() -> None:
    # Pydantic must not reject padded input before the domain trims it to the
    # valid upper boundary.
    title = "x" * 120
    with _client() as client:
        response = client.post("/tasks", json={"title": f"  {title}  "})

    assert response.status_code == 201
    assert response.json()["title"] == title


@solution_only
@pytest.mark.parametrize(
    ("method", "path", "kwargs", "status_code", "code", "field"),
    [
        (
            "post",
            "/tasks",
            {"content": b"{", "headers": {"content-type": "application/json"}},
            400,
            "invalid_json",
            None,
        ),
        (
            "post",
            "/tasks",
            {"content": b"{}"},
            400,
            "invalid_json",
            None,
        ),
        (
            "post",
            "/tasks",
            {"json": {"done": True}},
            422,
            "validation_error",
            "done",
        ),
        (
            "post",
            "/tasks",
            {"json": {"title": None}},
            422,
            "validation_error",
            "title",
        ),
        (
            "patch",
            "/tasks/1",
            {"json": {}},
            422,
            "validation_error",
            "update",
        ),
        (
            "get",
            "/tasks?completed=True",
            {},
            422,
            "validation_error",
            "completed",
        ),
        (
            "get",
            "/tasks?completed=true&completed=false",
            {},
            422,
            "validation_error",
            "completed",
        ),
        (
            "get",
            "/tasks/+1",
            {},
            422,
            "validation_error",
            "id",
        ),
    ],
)
def test_fastapi_normalizes_request_failures(
    method: str,
    path: str,
    kwargs: dict[str, Any],
    status_code: int,
    code: str,
    field: str | None,
) -> None:
    # The table mixes Starlette parsing, Pydantic validation, and domain rules;
    # identical envelopes prevent framework provenance from leaking to clients.
    with _client() as client:
        response = client.request(method, path, **kwargs)
        assert response.status_code == status_code
        error = response.json()["error"]
        assert error["code"] == code
        if field is not None:
            assert error["details"]["field"] == field


@solution_only
def test_fastapi_normalizes_routing_errors_and_allow_header() -> None:
    with _client() as client:
        unknown = client.get("/unknown")
        assert unknown.status_code == 404
        assert unknown.json()["error"]["code"] == "not_found"

        trailing_slash = client.get("/tasks/")
        assert trailing_slash.status_code == 404
        assert trailing_slash.json()["error"]["code"] == "not_found"

        unsupported = client.post("/health")
        assert unsupported.status_code == 405
        assert unsupported.headers["allow"] == "GET"
        assert unsupported.json()["error"]["code"] == "method_not_allowed"


class _FailingService(TaskService):
    def __init__(self, error: Exception) -> None:
        self._error = error

    def list_tasks(self, completed: object | None = None) -> list[DomainTask]:
        del completed
        raise self._error


@solution_only
@pytest.mark.parametrize(
    "error",
    [
        StorageError("database password=secret", operation="list"),
        RuntimeError("private traceback detail"),
    ],
)
def test_fastapi_sanitizes_internal_failures(error: Exception) -> None:
    app = create_app(cast(TaskService, _FailingService(error)))
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/tasks")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "the server could not complete the request",
        }
    }
    assert str(error) not in response.text


@solution_only
def test_generated_openapi_matches_checked_in_route_and_schema_intent() -> None:
    with temporary_project_directory() as directory:
        app = create_app(_service(directory / "openapi.db"))
        generated = app.openapi()
    intended = yaml.safe_load(
        (PROJECT_ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8")
    )

    # Compare the compatibility-bearing subset rather than formatting or
    # framework-generated descriptions that are not part of the teaching API.
    assert generated["openapi"] == intended["openapi"]
    assert set(generated["paths"]) == set(intended["paths"])
    for path, intended_path in intended["paths"].items():
        generated_path = generated["paths"][path]
        intended_methods = {
            method
            for method in intended_path
            if method in {"get", "post", "patch", "delete"}
        }
        generated_methods = {
            method for method in generated_path if method in intended_methods
        }
        assert generated_methods == intended_methods
        for method in intended_methods:
            assert (
                generated_path[method]["operationId"]
                == intended_path[method]["operationId"]
            )
            assert set(generated_path[method]["responses"]) == set(
                intended_path[method]["responses"]
            )

    schemas = generated["components"]["schemas"]
    for name in ("Health", "Task", "CreateTask", "UpdateTask", "Error"):
        assert schemas[name]["type"] == intended["components"]["schemas"][name]["type"]
        assert schemas[name]["additionalProperties"] is False
    assert schemas["UpdateTask"]["minProperties"] == 1
    assert schemas["Task"]["required"] == ["id", "title", "completed"]
    completed_parameter = generated["paths"]["/tasks"]["get"]["parameters"][0]
    assert completed_parameter["schema"] == {"type": "boolean"}


class _ControlledHandler(BaseHTTPRequestHandler):
    requests: ClassVar[list[tuple[str, bytes, str | None]]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        type(self).requests.append((self.path, body, self.headers.get("content-type")))
        response = b'{"error":"captured"}'
        self.send_response(418)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


@solution_only
def test_httpx_transport_uses_params_json_and_captures_http_status_and_body() -> None:
    _ControlledHandler.requests.clear()
    # A controlled peer observes HTTPX's actual wire request and returns a
    # non-2xx response, which the transport must capture rather than raise.
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ControlledHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with HttpxTransport(
            f"http://127.0.0.1:{server.server_port}/api",
            1.0,
        ) as transport:
            response = transport.send(
                TransportRequest(
                    "POST",
                    "/tasks",
                    query={"completed": "false"},
                    json_body={"title": "Learn HTTPX"},
                )
            )
        assert response.status == 418
        assert response.body == b'{"error":"captured"}'
        assert response.headers["content-type"] == "application/json"
        path, body, content_type = _ControlledHandler.requests.pop()
        assert path == "/api/tasks?completed=false"
        assert json.loads(body) == {"title": "Learn HTTPX"}
        assert content_type == "application/json"
        with pytest.raises(TransportError, match="closed"):
            transport.send(TransportRequest("GET", "/health"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


@solution_only
def test_httpx_transport_translates_connection_errors_without_retrying() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    port = cast(tuple[str, int], listener.getsockname())[1]
    listener.close()

    with HttpxTransport(f"http://127.0.0.1:{port}", 0.2) as transport:
        with pytest.raises(TransportConnectionError):
            transport.send(TransportRequest("GET", "/health"))


def _exercise(
    send: Callable[
        [HttpMethod, str, dict[str, str], dict[str, JsonValue] | None],
        tuple[int, object | None],
    ],
) -> list[tuple[int, object | None]]:
    return [
        send("POST", "/tasks", {}, {"title": "Parity"}),
        send("GET", "/tasks", {"completed": "false"}, None),
        send("PATCH", "/tasks/1", {}, {"completed": True}),
        send("GET", "/tasks/1", {}, None),
        send("DELETE", "/tasks/1", {}, None),
        send("GET", "/tasks/1", {}, None),
    ]


@solution_only
def test_testclient_and_loopback_httpx_observe_the_same_contract() -> None:
    # Replaying one operation sequence through both paths catches middleware or
    # serialization differences hidden by FastAPI's in-process TestClient.
    with _client() as client:

        def testclient_send(
            method: HttpMethod,
            path: str,
            query: dict[str, str],
            body: dict[str, JsonValue] | None,
        ) -> tuple[int, object | None]:
            response = client.request(method, path, params=query, json=body)
            return (
                response.status_code,
                None if not response.content else response.json(),
            )

        in_process = _exercise(testclient_send)

    with _live_app() as base_url, HttpxTransport(base_url, 2.0) as transport:

        def httpx_send(
            method: HttpMethod,
            path: str,
            query: dict[str, str],
            body: dict[str, JsonValue] | None,
        ) -> tuple[int, object | None]:
            response = transport.send(
                TransportRequest(
                    method,
                    path,
                    query=query,
                    json_body=body,
                )
            )
            return (
                response.status,
                None if not response.body else _json(response),
            )

        loopback = _exercise(httpx_send)

    assert loopback == in_process


@solution_only
def test_httpx_module_composes_the_shared_cli_against_loopback(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with _live_app() as base_url:
        assert client_main(["--base-url", base_url, "add", "CLI task"]) == 0
        created = json.loads(capsys.readouterr().out)
        assert created["title"] == "CLI task"

        assert client_main(["--base-url", base_url, "complete", "1"]) == 0
        completed = json.loads(capsys.readouterr().out)
        assert completed["completed"] is True
