"""Idiomatic Requests transport for the shared Task client application."""

import math
from urllib.parse import quote

import requests

from tasks_cli.transport import (
    TaskTransport,
    TransportConnectionError,
    TransportError,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
    normalize_base_url,
)


class RequestsTransport:
    """Task transport that owns one reusable ``requests.Session`` per CLI run."""

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
        self._session = requests.Session()
        self._session.trust_env = False
        self._closed = False

    def send(self, request: TransportRequest) -> TransportResponse:
        """Make one wire request using Requests-native query and JSON serialization."""

        if self._closed:
            raise TransportError("transport is closed")

        url = f"{self.base_url}{quote(request.path, safe='/')}"
        try:
            # ``params`` and ``json`` delegate component encoding to Requests
            # instead of rebuilding URL/query/body rules in this adapter.
            response = self._session.request(
                method=request.method,
                url=url,
                params=dict(request.query),
                json=(
                    dict(request.json_body) if request.json_body is not None else None
                ),
                timeout=self.timeout,
                allow_redirects=False,
            )
            try:
                # Copy the complete body before closing: TransportResponse owns
                # bytes and does not keep a live Requests response or socket.
                return TransportResponse(
                    status=response.status_code,
                    headers=dict(response.headers),
                    body=bytes(response.content),
                )
            finally:
                response.close()
        # Translate library exceptions into the finite categories understood by
        # the shared application; an HTTP status itself remains a response.
        except requests.Timeout as error:
            raise TransportTimeoutError("request timed out") from error
        except requests.ConnectionError as error:
            raise TransportConnectionError("request failed") from error
        except requests.RequestException as error:
            raise TransportError("request failed") from error

    def close(self) -> None:
        """Idempotently release the one session owned by this transport."""

        if not self._closed:
            try:
                self._session.close()
            except requests.Timeout as error:
                raise TransportTimeoutError("request timed out") from error
            except requests.ConnectionError as error:
                raise TransportConnectionError("request failed") from error
            except requests.RequestException as error:
                raise TransportError("request failed") from error
            finally:
                self._closed = True


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one Requests transport for a CLI invocation."""

    return RequestsTransport(base_url, timeout)


__all__ = ["RequestsTransport", "create_transport"]
