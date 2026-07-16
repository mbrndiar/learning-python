"""Requests transport boundary for milestone four."""

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class RequestsTransport:
    """TODO: own one ``requests.Session`` for this CLI invocation.

    A Session makes connection ownership explicit and must be closed by this
    adapter; avoid module-level requests functions that hide that lifecycle.
    """

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        """TODO: use Requests' ``params=`` and ``json=`` arguments.

        Let Requests encode query and JSON values, but return only status,
        copied headers and raw bytes. Translate timeout/connection/library
        failures to the shared transport errors and do not add a retry loop.
        Requests follows redirects by default, so one Session.request call may
        still produce more than one wire request.
        """

        incomplete(
            "milestone 4 requests call "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """TODO: idempotently close the session owned by this transport."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one Requests transport for the shared client application."""

    return RequestsTransport(base_url, timeout)


__all__ = ["RequestsTransport", "create_transport"]
