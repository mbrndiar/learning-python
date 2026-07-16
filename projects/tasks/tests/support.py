"""Deterministic paths and parser helpers for Task milestone tests."""

import argparse
import http.client
import json
import socket
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from typing import Literal, cast
from urllib.parse import urlsplit

TEST_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_ROOT.parent
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
FIXTURES = TEST_ROOT / "fixtures"
FIXED_BASE_URL = "http://127.0.0.1:8765"
LOOPBACK_HOST = "127.0.0.1"
REQUEST_TIMEOUT = 2.0
STARTUP_TIMEOUT = 5.0
SHUTDOWN_TIMEOUT = 5.0

ServerName = Literal["stdlib", "flask", "fastapi"]
ClientName = Literal["urllib", "requests", "httpx"]

SERVER_ARGUMENTS = (
    "--host",
    "127.0.0.1",
    "--port",
    "8765",
    "--backend",
    "markdown",
    "--data",
    "tasks.md",
)

CLIENT_COMMANDS = (
    ("add", "Learn REST"),
    ("list", "--completed", "false"),
    ("show", "1"),
    ("update", "1", "--title", "Read the spec", "--completed", "true"),
    ("complete", "1"),
    ("remove", "1"),
)


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """Captured loopback response with case-insensitive header lookup."""

    status: int
    headers: dict[str, str]
    body: bytes

    def header(self, name: str) -> str | None:
        folded = name.casefold()
        return next(
            (value for key, value in self.headers.items() if key.casefold() == folded),
            None,
        )


@dataclass(slots=True)
class LiveServer:
    """Own one loopback server, its thread, listener, and shutdown callbacks."""

    base_url: str
    thread: Thread
    _shutdown: Callable[[], None] = field(repr=False)
    _close_resources: Callable[[], None] = field(repr=False)
    _force_shutdown: Callable[[], None] | None = field(default=None, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        shutdown_error: BaseException | None = None
        try:
            self._shutdown()
        except BaseException as error:
            shutdown_error = error

        self.thread.join(timeout=SHUTDOWN_TIMEOUT)
        if self.thread.is_alive() and self._force_shutdown is not None:
            self._force_shutdown()
            self.thread.join(timeout=SHUTDOWN_TIMEOUT)

        try:
            self._close_resources()
        except BaseException as error:
            if shutdown_error is None:
                shutdown_error = error

        if self.thread.is_alive():
            raise RuntimeError("loopback server thread did not terminate")
        if shutdown_error is not None:
            raise RuntimeError("loopback server cleanup failed") from shutdown_error


@contextmanager
def temporary_project_directory() -> Iterator[Path]:
    """Create cleaned test storage below this project, never in system temp."""

    with TemporaryDirectory(prefix=".tasks-test-", dir=TEST_ROOT) as directory:
        yield Path(directory)


def request_http(
    base_url: str,
    method: str,
    path: str,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = REQUEST_TIMEOUT,
) -> HttpResponse:
    """Send one finite-timeout HTTP request and close its connection."""

    parsed = urlsplit(base_url)
    if parsed.hostname is None or parsed.port is None:
        raise ValueError("loopback base URL must include a host and port")
    connection = http.client.HTTPConnection(
        parsed.hostname,
        parsed.port,
        timeout=timeout,
    )
    try:
        connection.request(
            method,
            path,
            body=body,
            headers=dict(headers or {}),
        )
        response = connection.getresponse()
        return HttpResponse(
            response.status,
            dict(response.getheaders()),
            response.read(),
        )
    finally:
        connection.close()


def request_json(
    base_url: str,
    method: str,
    path: str,
    value: object,
) -> HttpResponse:
    """Send one UTF-8 JSON request over loopback."""

    return request_http(
        base_url,
        method,
        path,
        body=json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


def _wait_until_ready(server: LiveServer) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if not server.thread.is_alive():
            server.close()
            raise RuntimeError("loopback server thread exited during startup")
        try:
            if (
                request_http(server.base_url, "GET", "/health", timeout=0.2).status
                == 200
            ):
                return
        except (ConnectionError, OSError):
            time.sleep(0.01)
    server.close()
    raise RuntimeError("loopback server did not become ready")


def start_task_server(server_name: ServerName, service: object) -> LiveServer:
    """Start one Task server on an ephemeral loopback port."""

    if server_name == "stdlib":
        from tasks_api.stdlib.app import create_server

        server = create_server(service, LOOPBACK_HOST, 0)
        server.daemon_threads = True
        thread = Thread(
            target=server.serve_forever,
            kwargs={"poll_interval": 0.01},
            name="tasks-stdlib-loopback",
            daemon=True,
        )
        thread.start()
        host, port = cast(tuple[str, int], server.server_address)
        handle = LiveServer(
            f"http://{host}:{port}",
            thread,
            server.shutdown,
            server.server_close,
        )
    elif server_name == "flask":
        from tasks_api.flask.app import create_app
        from werkzeug.serving import make_server

        server = make_server(
            LOOPBACK_HOST,
            0,
            create_app(service),
            threaded=True,
        )
        thread = Thread(
            target=server.serve_forever,
            name="tasks-flask-loopback",
            daemon=True,
        )
        thread.start()
        handle = LiveServer(
            f"http://{LOOPBACK_HOST}:{server.server_port}",
            thread,
            server.shutdown,
            server.server_close,
        )
    else:
        import uvicorn
        from tasks_api.fastapi.app import create_app

        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((LOOPBACK_HOST, 0))
        listener.listen()
        host, port = cast(tuple[str, int], listener.getsockname())
        server = uvicorn.Server(
            uvicorn.Config(
                create_app(service),
                log_level="error",
                lifespan="off",
                timeout_keep_alive=1,
            )
        )
        thread = Thread(
            target=server.run,
            kwargs={"sockets": [listener]},
            name="tasks-fastapi-loopback",
            daemon=True,
        )
        thread.start()

        def stop_uvicorn() -> None:
            server.should_exit = True

        def force_stop_uvicorn() -> None:
            server.force_exit = True
            listener.close()

        handle = LiveServer(
            f"http://{host}:{port}",
            thread,
            stop_uvicorn,
            listener.close,
            force_stop_uvicorn,
        )

    try:
        _wait_until_ready(handle)
    except BaseException:
        handle.close()
        raise
    return handle


def start_handler_server(
    handler: type[BaseHTTPRequestHandler],
) -> LiveServer:
    """Start a controlled standard-library HTTP handler on loopback."""

    server = ThreadingHTTPServer((LOOPBACK_HOST, 0), handler)
    server.daemon_threads = True
    thread = Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        name="tasks-controlled-loopback",
        daemon=True,
    )
    thread.start()
    host, port = cast(tuple[str, int], server.server_address)
    return LiveServer(
        f"http://{host}:{port}",
        thread,
        server.shutdown,
        server.server_close,
    )


@contextmanager
def running_task_server(
    server_name: ServerName,
    service: object,
) -> Iterator[LiveServer]:
    """Yield a ready loopback Task server and always release its resources."""

    server = start_task_server(server_name, service)
    try:
        yield server
    finally:
        server.close()


@contextmanager
def running_handler_server(
    handler: type[BaseHTTPRequestHandler],
) -> Iterator[LiveServer]:
    """Yield a controlled loopback handler and always stop its server."""

    server = start_handler_server(handler)
    try:
        yield server
    finally:
        server.close()


@contextmanager
def unavailable_loopback_url() -> Iterator[str]:
    """Reserve a non-listening loopback endpoint for connection-failure tests."""

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((LOOPBACK_HOST, 0))
    host, port = cast(tuple[str, int], listener.getsockname())
    try:
        yield f"http://{host}:{port}"
    finally:
        listener.close()


def load_json_fixture(*parts: str) -> object:
    """Load one deterministic UTF-8 JSON fixture."""

    return json.loads(FIXTURES.joinpath(*parts).read_text(encoding="utf-8"))


def assert_server_parser(parser: argparse.ArgumentParser) -> None:
    """Assert the common documented server options parse coherently."""

    arguments = parser.parse_args(SERVER_ARGUMENTS)
    assert cast(str, arguments.host) == "127.0.0.1"
    assert cast(int, arguments.port) == 8765
    assert cast(str, arguments.backend) == "markdown"
    assert cast(Path, arguments.data) == Path("tasks.md")


def assert_client_parser(parser: argparse.ArgumentParser) -> None:
    """Assert every documented client command parses without execution."""

    parsed_commands = [
        cast(str, parser.parse_args(command).command) for command in CLIENT_COMMANDS
    ]
    assert parsed_commands == [
        "add",
        "list",
        "show",
        "update",
        "complete",
        "remove",
    ]
