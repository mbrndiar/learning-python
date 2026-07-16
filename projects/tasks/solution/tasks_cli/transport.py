"""Library-neutral outbound HTTP transport contract.

Adapters expose only status, headers, and body bytes so the application, rather
than an HTTP library, owns response decoding and validation policy.
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal, Protocol, TypeAlias, runtime_checkable
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

HttpMethod: TypeAlias = Literal["GET", "POST", "PATCH", "DELETE"]
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
_HTTP_METHODS = frozenset({"GET", "POST", "PATCH", "DELETE"})


def normalize_base_url(value: str) -> str:
    """Return an unambiguous HTTP(S) base URL safe for path composition."""

    if not value or value != value.strip():
        raise ValueError("base URL must be an absolute HTTP or HTTPS URL")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise ValueError("base URL must be an absolute HTTP or HTTPS URL") from error

    # Credentials, query strings, and fragments would make later path/query
    # composition ambiguous, so they are rejected at the configuration boundary.
    scheme = parsed.scheme.casefold()
    hostname = parsed.hostname
    if (
        scheme not in {"http", "https"}
        or hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "base URL must use HTTP or HTTPS without credentials, query, or fragment"
        )
    if any(character.isspace() for character in value):
        raise ValueError("base URL must not contain whitespace")

    host = hostname.casefold()
    if ":" in host:
        host = f"[{host}]"
    netloc = host if port is None else f"{host}:{port}"
    path = quote(
        parsed.path.rstrip("/"),
        safe="/:@-._~!$&'()*+,;=%",
    )
    return urlunsplit((scheme, netloc, path, "", ""))


def build_url(base_url: str, request: "TransportRequest") -> str:
    """Encode path and query components without letting either change the URL shape."""

    # Quote the path separately from urlencode so data such as ``?`` or ``#`` in
    # a path cannot become URL syntax, while slash remains a path separator.
    url = f"{normalize_base_url(base_url)}{quote(request.path, safe='/')}"
    if not request.query:
        return url
    # ``urlencode`` gives query keys and values their own escaping rules instead
    # of relying on error-prone string concatenation.
    return f"{url}?{urlencode(request.query, quote_via=quote)}"


def _is_json_value(value: object) -> bool:
    if value is None or isinstance(value, (str, bool, int)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _is_json_value(item) for key, item in value.items()
        )
    return False


@dataclass(frozen=True, slots=True)
class TransportRequest:
    """One validated request that any supported HTTP library can represent."""

    method: HttpMethod
    path: str
    query: Mapping[str, str] = field(default_factory=dict)
    json_body: Mapping[str, JsonValue] | None = None

    def __post_init__(self) -> None:
        # Validate and shallow-copy top-level mappings so later key changes
        # cannot alter the request; nested JSON containers remain shared.
        if self.method not in _HTTP_METHODS:
            raise ValueError("unsupported HTTP method")
        if not self.path.startswith("/"):
            raise ValueError("request path must start with /")
        if not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in self.query.items()
        ):
            raise ValueError("request query keys and values must be strings")
        if self.json_body is not None and not _is_json_value(dict(self.json_body)):
            raise ValueError("request body must contain JSON-compatible values")
        object.__setattr__(self, "query", dict(self.query))
        if self.json_body is not None:
            object.__setattr__(self, "json_body", dict(self.json_body))


@dataclass(frozen=True, slots=True)
class TransportResponse:
    """Raw status, headers, and owned body bytes for application validation."""

    status: int
    headers: Mapping[str, str]
    body: bytes

    def __post_init__(self) -> None:
        object.__setattr__(self, "headers", dict(self.headers))


class TransportError(Exception):
    """Library-neutral non-HTTP-response failure during one exchange."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TransportConnectionError(TransportError):
    """The client could not establish or maintain the HTTP exchange."""


class TransportTimeoutError(TransportConnectionError):
    """The HTTP exchange exceeded its required positive, finite timeout."""


@runtime_checkable
class TaskTransport(Protocol):
    """Send once per call and release all adapter-owned network resources."""

    def send(self, request: TransportRequest) -> TransportResponse:
        """Send one request without retries, preserving non-idempotent semantics."""

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
    "build_url",
    "normalize_base_url",
]
