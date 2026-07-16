"""Requests transport boundary for milestone four."""

from collections.abc import Mapping

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportResponse


class RequestsTransport:
    """Task transport that will own a ``requests.Session``."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> TransportResponse:
        incomplete(
            "milestone 4 requests call "
            f"{method} {path}, query={query!r}, json={json_body!r}"
        )

    def close(self) -> None:
        """Release the future session owned by this transport."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one Requests transport without importing the optional library."""

    return RequestsTransport(base_url, timeout)


__all__ = ["RequestsTransport", "create_transport"]
