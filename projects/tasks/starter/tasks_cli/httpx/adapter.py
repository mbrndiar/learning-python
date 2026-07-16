"""HTTPX transport boundary for milestone five."""

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class HttpxTransport:
    """Task transport that will own an ``httpx.Client``."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        incomplete(
            "milestone 5 httpx call "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """Release the future client owned by this transport."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one HTTPX transport without importing the optional library."""

    return HttpxTransport(base_url, timeout)


__all__ = ["HttpxTransport", "create_transport"]
