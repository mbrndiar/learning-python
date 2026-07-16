"""Requests transport boundary for milestone four."""

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class RequestsTransport:
    """TODO: own one ``requests.Session`` for this CLI invocation."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        """TODO: use Requests' ``params=`` and ``json=`` arguments."""

        incomplete(
            "milestone 4 requests call "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """TODO: close the session owned by this transport."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one Requests transport for the shared client application."""

    return RequestsTransport(base_url, timeout)


__all__ = ["RequestsTransport", "create_transport"]
