"""Low-level ``urllib`` transport boundary for milestone three."""

from collections.abc import Mapping

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportResponse


class UrllibTransport:
    """Task transport implemented with the Python standard library."""

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
            "milestone 3 urllib request "
            f"{method} {path}, query={query!r}, json={json_body!r}"
        )

    def close(self) -> None:
        """Release transport resources once milestone three owns some."""


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one standard-library transport."""

    return UrllibTransport(base_url, timeout)


__all__ = ["UrllibTransport", "create_transport"]
