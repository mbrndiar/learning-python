"""Milestone-four tests for Flask integration and the Requests transport.

The starter retains explicit lifecycle/client TODOs while the solution tests
cover dependency-injected app factories, Flask error normalization, persistence
composition, Requests-native argument mapping, and deterministic resource
cleanup.  Framework-specific tests complement—not replace—the shared REST
contract that later compares all adapters as black boxes.
"""

import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Thread
from typing import NoReturn

import pytest
import requests as requests_library
from flask import Flask
from implementation import IMPLEMENTATION
from support import (
    SERVER_ARGUMENTS,
    assert_client_parser,
    assert_server_parser,
    temporary_project_directory,
)
from tasks_api.bootstrap import Backend, ServerSettings, build_service
from tasks_api.flask.__main__ import build_parser as build_server_parser
from tasks_api.flask.__main__ import main as server_main
from tasks_api.flask.app import create_app
from tasks_cli.requests.__main__ import build_parser as build_client_parser
from tasks_cli.requests.__main__ import main as client_main
from tasks_cli.requests.adapter import RequestsTransport
from tasks_cli.transport import (
    TransportConnectionError,
    TransportError,
    TransportRequest,
    TransportTimeoutError,
)
from tasks_core import (
    CreateTaskInput,
    IncompleteImplementationError,
    StorageError,
    Task,
    TaskService,
    UpdateTaskInput,
)
from werkzeug.serving import make_server
from werkzeug.test import TestResponse

STARTER = IMPLEMENTATION == "starter"
# Keep guidance checks runnable without treating deliberately absent milestone
# behavior as a regression in the starter tree.
solution_only = pytest.mark.skipif(STARTER, reason="solution milestone-four behavior")
starter_only = pytest.mark.skipif(not STARTER, reason="starter guidance behavior")


class _FailureRepository:
    """Make every repository operation fail at the service boundary."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    def _fail(self) -> NoReturn:
        raise self._error

    def create(self, task: CreateTaskInput) -> Task:
        del task
        self._fail()

    def list(self, completed: bool | None = None) -> list[Task]:
        del completed
        self._fail()

    def get(self, task_id: int) -> Task:
        del task_id
        self._fail()

    def update(self, task_id: int, update: UpdateTaskInput) -> Task:
        del task_id, update
        self._fail()

    def delete(self, task_id: int) -> None:
        del task_id
        self._fail()


@contextmanager
def _loopback_server(app: Flask) -> Iterator[str]:
    """Own a threaded Werkzeug server bound to an ephemeral loopback port."""

    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        # Werkzeug separates graceful shutdown from listener cleanup; both are
        # required before asserting the worker thread has terminated.
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        assert not thread.is_alive()


def _assert_error(
    response: TestResponse,
    status: int,
    code: str,
    *,
    details: dict[str, object] | None = None,
) -> None:
    assert response.status_code == status
    assert response.mimetype == "application/json"
    error: dict[str, object] = {
        "code": code,
        "message": response.get_json()["error"]["message"],
    }
    if details is not None:
        error["details"] = details
    assert response.get_json() == {"error": error}


def test_flask_and_requests_launchers_parse_the_documented_commands() -> None:
    assert_server_parser(build_server_parser())
    assert_client_parser(build_client_parser())


@starter_only
def test_starter_keeps_milestone_four_guidance_deliberately_incomplete() -> None:
    # Named incomplete errors keep the exercise discoverable and distinguish a
    # pending milestone from an accidental framework/import failure.
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 4 Flask server lifecycle.*intentionally incomplete",
    ):
        server_main(SERVER_ARGUMENTS)

    with pytest.raises(
        IncompleteImplementationError,
        match=r"client command execution.*intentionally incomplete",
    ):
        client_main(["show", "1"])


@solution_only
def test_flask_factory_uses_injected_services_without_global_state() -> None:
    with temporary_project_directory() as directory:
        # Two independent apps expose accidental module-level service state:
        # mutating one must never alter the other's repository.
        first = create_app(
            build_service(
                ServerSettings(
                    "127.0.0.1",
                    0,
                    "sqlite",
                    directory / "first.db",
                )
            )
        )
        second = create_app(
            build_service(
                ServerSettings(
                    "127.0.0.1",
                    0,
                    "sqlite",
                    directory / "second.db",
                )
            )
        )

        assert isinstance(first, Flask)
        response = first.test_client().post(
            "/tasks",
            json={"title": "Only first"},
        )
        assert response.status_code == 201
        assert second.test_client().get("/tasks").get_json() == []


@solution_only
def test_flask_test_client_covers_normal_and_boundary_task_flows() -> None:
    with temporary_project_directory() as directory:
        app = create_app(
            build_service(
                ServerSettings(
                    "127.0.0.1",
                    0,
                    "sqlite",
                    directory / "tasks.db",
                )
            )
        )
        client = app.test_client()

        health = client.get("/health")
        assert health.status_code == 200
        assert health.get_json() == {"status": "ok"}

        created = client.post("/tasks", json={"title": "  Learn Flask  "})
        assert created.status_code == 201
        assert created.get_json() == {
            "id": 1,
            "title": "Learn Flask",
            "completed": False,
        }

        # The exact upper boundary guards against framework validation becoming
        # stricter than the domain's normalized 120-character contract.
        boundary_title = "x" * 120
        boundary = client.post("/tasks", json={"title": boundary_title})
        assert boundary.status_code == 201
        assert boundary.get_json()["title"] == boundary_title

        updated = client.patch("/tasks/1", json={"completed": True})
        assert updated.status_code == 200
        assert updated.get_json() == {
            "id": 1,
            "title": "Learn Flask",
            "completed": True,
        }
        assert client.get("/tasks?completed=true").get_json() == [updated.get_json()]
        assert client.get("/tasks?completed=false").get_json() == [boundary.get_json()]
        assert client.get("/tasks/1").get_json() == updated.get_json()

        deleted = client.delete("/tasks/1")
        assert deleted.status_code == 204
        assert deleted.data == b""
        _assert_error(client.get("/tasks/1"), 404, "not_found")


@solution_only
def test_flask_normalizes_json_validation_routing_and_method_errors() -> None:
    with temporary_project_directory() as directory:
        client = create_app(
            build_service(
                ServerSettings(
                    "127.0.0.1",
                    0,
                    "sqlite",
                    directory / "tasks.db",
                )
            )
        ).test_client()

        _assert_error(
            client.post("/tasks", data=b'{"title":"x"}'),
            400,
            "invalid_json",
        )
        _assert_error(
            client.post("/tasks", data=b"{", content_type="application/json"),
            400,
            "invalid_json",
        )
        _assert_error(
            client.post(
                "/tasks", data=b'{"title":"\xff"}', content_type="application/json"
            ),
            400,
            "invalid_json",
        )
        _assert_error(
            client.post("/tasks", json=[]),
            422,
            "validation_error",
            details={"field": "body"},
        )
        _assert_error(
            client.post("/tasks", json={"title": "x", "done": False}),
            422,
            "validation_error",
            details={"field": "done"},
        )
        _assert_error(
            client.patch("/tasks/1", json={}),
            422,
            "validation_error",
            details={"field": "update"},
        )
        _assert_error(
            client.get("/tasks/0"),
            422,
            "validation_error",
            details={"field": "id"},
        )
        _assert_error(
            client.get("/tasks/not-a-number"),
            422,
            "validation_error",
            details={"field": "id"},
        )
        _assert_error(
            client.get("/tasks?completed=True"),
            422,
            "validation_error",
            details={"field": "completed"},
        )
        _assert_error(
            client.get("/tasks?completed=true&completed=false"),
            422,
            "validation_error",
            details={"field": "completed"},
        )

        method = client.put("/tasks")
        _assert_error(method, 405, "method_not_allowed")
        assert {"GET", "POST"} <= set(method.headers["Allow"].split(", "))
        _assert_error(client.get("/missing"), 404, "not_found")


@solution_only
@pytest.mark.parametrize(
    ("error", "secret"),
    [
        (StorageError("database password leaked", operation="list"), "password leaked"),
        (RuntimeError("unexpected implementation detail"), "implementation detail"),
    ],
)
def test_flask_logs_failures_and_sanitizes_internal_errors(
    error: Exception,
    secret: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Storage and unexpected failures take the same public path so neither can
    # leak the injected secret through Flask's default exception handling.
    app = create_app(TaskService(_FailureRepository(error)))
    with caplog.at_level(logging.ERROR):
        response = app.test_client().get("/tasks")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": {
            "code": "internal_error",
            "message": "the server could not complete the request",
        }
    }
    assert secret.encode() not in response.data
    assert secret in caplog.text


@solution_only
@pytest.mark.parametrize(
    ("backend", "filename"),
    [("sqlite", "tasks.db"), ("markdown", "tasks.md")],
)
def test_flask_composes_each_persistence_backend(
    backend: Backend,
    filename: str,
) -> None:
    with temporary_project_directory() as directory:
        data = directory / filename
        service = build_service(ServerSettings("127.0.0.1", 0, backend, data))
        client = create_app(service).test_client()

        assert client.post("/tasks", json={"title": backend}).status_code == 201
        assert client.get("/tasks").get_json() == [
            {"id": 1, "title": backend, "completed": False}
        ]
        assert data.exists()


@solution_only
def test_requests_transport_uses_native_arguments_and_owns_resources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RecordingResponse:
        status_code = 201
        headers = {"Content-Type": "application/json", "X-Test": "captured"}
        content = b'{"id":1,"title":"Native","completed":false}'

        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    class RecordingSession:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []
            self.response = RecordingResponse()
            self.closed = False

        def request(self, **arguments: object) -> RecordingResponse:
            self.calls.append(arguments)
            return self.response

        def close(self) -> None:
            self.closed = True

    # A recording Session verifies Requests receives params/json natively rather
    # than a pre-encoded approximation, and that response and session both close.
    session = RecordingSession()
    monkeypatch.setattr(requests_library, "Session", lambda: session)
    transport = RequestsTransport("http://127.0.0.1:8000/", 1.25)

    response = transport.send(
        TransportRequest(
            "POST",
            "/tasks",
            query={"source": "requests"},
            json_body={"title": "Native"},
        )
    )
    assert response.status == 201
    assert response.headers["X-Test"] == "captured"
    assert response.body == RecordingResponse.content
    assert session.calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/tasks",
            "params": {"source": "requests"},
            "json": {"title": "Native"},
            "timeout": 1.25,
        }
    ]
    assert session.response.closed

    transport.close()
    transport.close()
    assert session.closed
    with pytest.raises(TransportError, match="transport is closed"):
        transport.send(TransportRequest("GET", "/tasks"))


@solution_only
@pytest.mark.parametrize(
    ("library_error", "transport_error"),
    [
        (requests_library.Timeout("slow"), TransportTimeoutError),
        (requests_library.ConnectionError("offline"), TransportConnectionError),
        (requests_library.RequestException("bad exchange"), TransportError),
    ],
)
def test_requests_translates_library_failures(
    library_error: requests_library.RequestException,
    transport_error: type[TransportError],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingSession:
        def request(self, **arguments: object) -> NoReturn:
            del arguments
            raise library_error

        def close(self) -> None:
            pass

    # Inject at Session.request so each Requests exception is normalized at the
    # adapter boundary without making a real network call.
    monkeypatch.setattr(requests_library, "Session", FailingSession)
    transport = RequestsTransport("http://127.0.0.1:8000", 1.0)
    try:
        with pytest.raises(transport_error) as raised:
            transport.send(TransportRequest("GET", "/tasks"))
        assert library_error.args[0] not in str(raised.value)
    finally:
        transport.close()


@solution_only
def test_requests_cli_runs_over_a_controlled_flask_loopback_server(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with temporary_project_directory() as directory:
        app = create_app(
            build_service(
                ServerSettings(
                    "127.0.0.1",
                    0,
                    "sqlite",
                    directory / "tasks.db",
                )
            )
        )

        with _loopback_server(app) as base_url:
            exit_code = client_main(
                [
                    "--base-url",
                    base_url,
                    "--timeout",
                    "2",
                    "add",
                    "From Requests",
                ]
            )
            captured = capsys.readouterr()
            assert exit_code == 0
            assert json.loads(captured.out) == {
                "id": 1,
                "title": "From Requests",
                "completed": False,
            }
            assert captured.err == ""

            exit_code = client_main(
                [
                    "--base-url",
                    base_url,
                    "--timeout",
                    "2",
                    "list",
                    "--completed",
                    "false",
                ]
            )
            captured = capsys.readouterr()
            assert exit_code == 0
            assert json.loads(captured.out) == [
                {"id": 1, "title": "From Requests", "completed": False}
            ]

            exit_code = client_main(
                ["--base-url", base_url, "--timeout", "2", "show", "99"]
            )
            captured = capsys.readouterr()
            assert exit_code == 3
            assert captured.out == ""
            assert captured.err == "api: 404 not_found: task 99 was not found\n"
