"""Idiomatic synchronous HTTPX transport for milestone five."""

import math
from types import TracebackType

import httpx

from tasks_cli.transport import (
    TaskTransport,
    TransportConnectionError,
    TransportError,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
    normalize_base_url,
)


class HttpxTransport:
    """Own one finite-timeout ``httpx.Client`` for a complete CLI invocation."""

    def __init__(self, base_url: str, timeout: float) -> None:
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be positive and finite")
        self.base_url = normalize_base_url(base_url)
        self.timeout = float(timeout)
        self._client = httpx.Client(
            base_url=f"{self.base_url}/",
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=False,
            trust_env=False,
            # Retrying here could repeat POST/PATCH effects; the transport
            # contract deliberately makes one network attempt per send call.
            transport=httpx.HTTPTransport(retries=0),
        )
        self._closed = False

    def send(self, request: TransportRequest) -> TransportResponse:
        """Send once and return owned status, headers, and raw body bytes."""

        if self._closed:
            raise TransportError("HTTPX transport is closed")
        try:
            # HTTPX owns URL/query and JSON encoding. ``read`` materializes the
            # body and releases the connection back to the client pool; the
            # stream context guarantees response closure.
            with self._client.stream(
                request.method,
                request.path.removeprefix("/"),
                params=dict(request.query),
                json=(
                    dict(request.json_body) if request.json_body is not None else None
                ),
            ) as response:
                body = response.read()
                return TransportResponse(
                    status=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                )
        # Timeout is a distinct connection category. Other HTTPX protocol or
        # network failures become connection errors, while HTTP status failures
        # remain ordinary responses because ``raise_for_status`` is not called.
        except httpx.TimeoutException as error:
            raise TransportTimeoutError(
                str(error).strip() or "request timed out"
            ) from error
        except httpx.HTTPError as error:
            raise TransportConnectionError(
                str(error).strip() or "HTTP request failed"
            ) from error

    def close(self) -> None:
        """Idempotently close the one client and its connection pool."""

        if not self._closed:
            self._client.close()
            self._closed = True

    def __enter__(self) -> "HttpxTransport":
        """Allow callers to make transport ownership explicit with ``with``."""

        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Release the owned client when leaving a context for any reason."""

        del exception_type, exception, traceback
        self.close()


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one owned HTTPX client transport."""

    return HttpxTransport(base_url, timeout)


__all__ = ["HttpxTransport", "create_transport"]
