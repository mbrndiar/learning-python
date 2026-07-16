"""Library-neutral outbound HTTP transport contract."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal, Protocol, TypeAlias, runtime_checkable

HttpMethod: TypeAlias = Literal["GET", "POST", "PATCH", "DELETE"]
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = (
    JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
)


@dataclass(frozen=True, slots=True)
class TransportRequest:
    """One normalized HTTP request independent of a client library."""

    method: HttpMethod
    path: str
    query: Mapping[str, str] = field(default_factory=dict)
    json_body: Mapping[str, JsonValue] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "query", dict(self.query))
        if self.json_body is not None:
            object.__setattr__(self, "json_body", dict(self.json_body))


@dataclass(frozen=True, slots=True)
class TransportResponse:
    """Raw HTTP response information consumed by the command application."""

    status: int
    headers: Mapping[str, str]
    body: bytes

    def __post_init__(self) -> None:
        object.__setattr__(self, "headers", dict(self.headers))


class TransportError(Exception):
    """Library-neutral failure while sending or receiving a request."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TransportConnectionError(TransportError):
    """The client could not establish or maintain the HTTP exchange."""


class TransportTimeoutError(TransportConnectionError):
    """The HTTP exchange exceeded the configured finite timeout."""


@runtime_checkable
class TaskTransport(Protocol):
    """Send Task API requests and own transport cleanup."""

    def send(self, request: TransportRequest) -> TransportResponse:
        """Send one request without retrying it."""

        ...

    def close(self) -> None:
        """Release transport-owned resources."""

        ...


class TransportFactory(Protocol):
    """Construct one transport for a CLI invocation."""

    def __call__(self, base_url: str, timeout: float) -> TaskTransport: ...


__all__ = [
    "HttpMethod",
    "JsonScalar",
    "JsonValue",
    "TaskTransport",
    "TransportConnectionError",
    "TransportError",
    "TransportFactory",
    "TransportRequest",
    "TransportResponse",
    "TransportTimeoutError",
]
