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
    """Task transport that owns one ``requests.Session``."""

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
        self._closed = False

    def send(self, request: TransportRequest) -> TransportResponse:
        """Send one request using Requests' native query and JSON arguments."""

        if self._closed:
            raise TransportError("transport is closed")

        url = f"{self.base_url}{quote(request.path, safe='/')}"
        try:
            response = self._session.request(
                method=request.method,
                url=url,
                params=dict(request.query),
                json=(
                    dict(request.json_body) if request.json_body is not None else None
                ),
                timeout=self.timeout,
            )
            try:
                return TransportResponse(
                    status=response.status_code,
                    headers=dict(response.headers),
                    body=bytes(response.content),
                )
            finally:
                response.close()
        except requests.Timeout as error:
            raise TransportTimeoutError("request timed out") from error
        except requests.ConnectionError as error:
            raise TransportConnectionError("request failed") from error
        except requests.RequestException as error:
            raise TransportError("request failed") from error

    def close(self) -> None:
        """Release the owned Requests session."""

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
