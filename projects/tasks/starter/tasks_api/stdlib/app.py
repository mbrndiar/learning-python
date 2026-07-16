"""Low-level ``http.server`` boundary for milestone three."""

from http.server import ThreadingHTTPServer

from tasks_core.errors import incomplete
from tasks_core.service import TaskService


def create_server(
    service: TaskService,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    """Create the low-level server while keeping its socket lifecycle external.

    Milestone three needs a RequestHandler subclass that can reach the injected
    service, implements the documented routes, and owns HTTP details that later
    frameworks normally hide: paths, methods, headers, bytes, JSON and statuses.
    A handler factory or closure can bind the service without global state.
    """

    del service, host, port
    incomplete("milestone 3 standard-library server factory")


def serve(service: TaskService, host: str, port: int) -> None:
    """Run the server until interruption and always release its listening socket.

    Keep creation separate so tests can bind port 0 and control startup/shutdown
    without running this blocking process-level function.
    """

    del service, host, port
    incomplete("milestone 3 standard-library server lifecycle")


__all__ = ["create_server", "serve"]
