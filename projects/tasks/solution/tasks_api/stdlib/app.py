"""Low-level ``http.server`` boundary for milestone three."""

from http.server import ThreadingHTTPServer
from typing import NoReturn

from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_server(
    service: TaskService,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    """Create a configured standard-library HTTP server."""

    del service, host, port
    incomplete("milestone 3 standard-library server factory")


def serve(service: TaskService, host: str, port: int) -> NoReturn:
    """Own the standard-library server lifecycle."""

    del service, host, port
    incomplete("milestone 3 standard-library server lifecycle")


__all__ = ["create_server", "serve"]
