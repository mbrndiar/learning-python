"""Requests transport boundary for milestone four."""

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class RequestsTransport:
    """Task transport that will own a ``requests.Session``."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        incomplete(
            "milestone 4 requests call "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """Release the future session owned by this transport."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one Requests transport without importing the optional library."""

    return RequestsTransport(base_url, timeout)


__all__ = ["RequestsTransport", "create_transport"]
