"""Low-level ``urllib`` transport boundary for milestone three."""

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class UrllibTransport:
    """Task transport implemented with the Python standard library."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        incomplete(
            "milestone 3 urllib request "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """Release transport resources once milestone three owns some."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one standard-library transport."""

    return UrllibTransport(base_url, timeout)


__all__ = ["UrllibTransport", "create_transport"]
