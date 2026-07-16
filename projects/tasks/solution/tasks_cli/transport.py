"""Library-neutral outbound HTTP transport contract."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class TransportResponse:
    """Raw HTTP response information consumed by the command application."""

    status: int
    headers: Mapping[str, str]
    body: bytes


@runtime_checkable
class TaskTransport(Protocol):
    """Send one Task API request and own transport cleanup."""

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> TransportResponse:
        """Send one request without retrying it."""

        ...

    def close(self) -> None:
        """Release transport-owned resources."""

        ...


class TransportFactory(Protocol):
    """Construct one transport for a CLI invocation."""

    def __call__(self, base_url: str, timeout: float) -> TaskTransport: ...


__all__ = ["TaskTransport", "TransportFactory", "TransportResponse"]
