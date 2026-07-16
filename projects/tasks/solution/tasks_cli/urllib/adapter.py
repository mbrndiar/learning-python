"""Low-level ``urllib`` transport boundary for milestone three."""

import json
import math
from email.message import Message
from http.client import HTTPException
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from tasks_cli.transport import (
    TaskTransport,
    TransportConnectionError,
    TransportError,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
    build_url,
    normalize_base_url,
)


class _ReadableResponse(Protocol):
    status: int
    headers: Message

    def read(self) -> bytes: ...

    def close(self) -> None: ...


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        return None


def _open(request: Request, timeout: float) -> _ReadableResponse:
    return cast(
        _ReadableResponse,
        build_opener(_NoRedirectHandler()).open(request, timeout=timeout),
    )


def _message(value: object, fallback: str) -> str:
    message = str(value).strip()
    return message or fallback


class UrllibTransport:
    """Task transport implemented with the Python standard library."""

    def __init__(self, base_url: str, timeout: float) -> None:
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be positive and finite")
        self.base_url = normalize_base_url(base_url)
        self.timeout = timeout
        self._closed = False

    def send(self, request: TransportRequest) -> TransportResponse:
        if self._closed:
            raise TransportError("transport is closed")

        body: bytes | None = None
        headers = {"Accept": "application/json"}
        if request.json_body is not None:
            body = json.dumps(
                dict(request.json_body),
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
            headers["Content-Type"] = "application/json"

        try:
            urllib_request = Request(
                build_url(self.base_url, request),
                data=body,
                headers=headers,
                method=request.method,
            )
            try:
                response = _open(urllib_request, self.timeout)
                status = response.status
            except HTTPError as error:
                response = cast(_ReadableResponse, error)
                status = error.code
            return self._capture_response(response, status)
        except URLError as error:
            if isinstance(error.reason, TimeoutError):
                raise TransportTimeoutError("request timed out") from error
            raise TransportConnectionError(
                _message(error.reason, "request failed"),
            ) from error
        except TimeoutError as error:
            raise TransportTimeoutError("request timed out") from error
        except (HTTPException, OSError) as error:
            raise TransportConnectionError(
                _message(error, "request failed"),
            ) from error
        except (TypeError, ValueError, UnicodeError) as error:
            raise TransportError("request could not be sent") from error

    @staticmethod
    def _capture_response(
        response: _ReadableResponse,
        status: int,
    ) -> TransportResponse:
        try:
            body = response.read()
            headers = {name: value for name, value in response.headers.items()}
            return TransportResponse(status=status, headers=headers, body=body)
        finally:
            response.close()

    def close(self) -> None:
        """Mark this one-shot transport closed."""

        self._closed = True


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one standard-library transport."""

    return UrllibTransport(base_url, timeout)


__all__ = ["UrllibTransport", "create_transport"]
