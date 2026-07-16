"""
Lesson 11.4: HTTP Client Transports

urllib, requests, and httpx have different request and lifetime APIs. A narrow
transport keeps those details at the edge while shared client policy validates
timeouts, checks status before success bodies, and classifies failures.
"""

import json
import math
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import TracebackType
from typing import Protocol, Self
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

import httpx
import requests


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class ClientError(Exception):
    """Base class for stable client-facing failures."""


class ApiError(ClientError):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(f"API error {status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


class MalformedResponse(ClientError):
    """The server replied, but not with the documented shape."""


class ConnectionFailure(ClientError):
    """The request could not produce an HTTP response."""


class TaskTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
        timeout: float,
    ) -> TransportResponse:
        """Send one request and return library-neutral response data."""


def validate_timeout(timeout: float) -> None:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")


def content_type(headers: Mapping[str, str]) -> str:
    value = next(
        (
            header_value
            for name, header_value in headers.items()
            if name.casefold() == "content-type"
        ),
        "",
    )
    return value.split(";", 1)[0].strip().casefold()


def decode_json(response: TransportResponse) -> object:
    if content_type(response.headers) != "application/json":
        raise MalformedResponse("response Content-Type was not application/json")
    try:
        value: object = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MalformedResponse("response body was not UTF-8 JSON") from error
    return value


def decode_api_error(response: TransportResponse) -> ApiError:
    value = decode_json(response)
    if not isinstance(value, dict) or set(value) != {"error"}:
        raise MalformedResponse("API error envelope was malformed")
    error = value["error"]
    if not isinstance(error, dict):
        raise MalformedResponse("API error details were malformed")
    code = error.get("code")
    message = error.get("message")
    if not isinstance(code, str) or not isinstance(message, str):
        raise MalformedResponse("API error code or message was malformed")
    return ApiError(response.status, code, message)


def decode_task(response: TransportResponse, expected_status: int = 200) -> Task:
    # Branch on status before interpreting the body as a successful Task.
    if response.status != expected_status:
        if 400 <= response.status <= 599:
            raise decode_api_error(response)
        raise MalformedResponse(f"unexpected HTTP status: {response.status}")

    value = decode_json(response)
    if not isinstance(value, dict) or set(value) != {
        "id",
        "title",
        "completed",
    }:
        raise MalformedResponse("Task response fields were malformed")

    task_id = value["id"]
    title = value["title"]
    completed = value["completed"]
    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
        or not isinstance(title, str)
        or not 1 <= len(title) <= 120
        or any(unicodedata.category(character) == "Cc" for character in title)
        or not isinstance(completed, bool)
    ):
        raise MalformedResponse("Task response values were malformed")
    return Task(task_id, title, completed)


def build_url(
    base_url: str,
    path: str,
    query: Mapping[str, str] | None,
) -> str:
    if not path.startswith("/"):
        raise ValueError("path must start with /")
    url = f"{base_url.rstrip('/')}{path}"
    return url if not query else f"{url}?{urlencode(query)}"


def encode_json_body(
    json_body: Mapping[str, object] | None,
) -> bytes | None:
    if json_body is None:
        return None
    return json.dumps(
        json_body,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


class UrllibResponse(Protocol):
    status: int
    headers: Mapping[str, str]

    def read(self) -> bytes:
        """Read response bytes."""

    def __enter__(self) -> Self:
        """Own the response lifetime."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the response."""


class UrlOpener(Protocol):
    def open(self, request: Request, *, timeout: float) -> UrllibResponse:
        """Open one urllib request."""


class UrllibTransport:
    def __init__(self, base_url: str, opener: UrlOpener) -> None:
        self._base_url = base_url
        self._opener = opener

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
        timeout: float,
    ) -> TransportResponse:
        validate_timeout(timeout)
        body = encode_json_body(json_body)
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(
            build_url(self._base_url, path, query),
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                return TransportResponse(
                    response.status,
                    dict(response.headers),
                    response.read(),
                )
        except HTTPError as error:
            with error:
                return TransportResponse(
                    error.code,
                    dict(error.headers),
                    error.read(),
                )
        except (URLError, TimeoutError, OSError) as error:
            raise ConnectionFailure("urllib request failed") from error


class RequestsResponse(Protocol):
    status_code: int
    headers: Mapping[str, str]
    content: bytes


class RequestsSession(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
    ) -> RequestsResponse:
        """Send one requests call."""


class RequestsTransport:
    def __init__(self, base_url: str, session: RequestsSession) -> None:
        self._base_url = base_url
        self._session = session

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
        timeout: float,
    ) -> TransportResponse:
        validate_timeout(timeout)
        try:
            response = self._session.request(
                method,
                build_url(self._base_url, path, None),
                params=query,
                json=json_body,
                timeout=timeout,
            )
        except requests.RequestException as error:
            raise ConnectionFailure("requests call failed") from error
        return TransportResponse(
            response.status_code,
            dict(response.headers),
            response.content,
        )


class HttpxResponse(Protocol):
    status_code: int
    headers: Mapping[str, str]
    content: bytes


class HttpxClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
    ) -> HttpxResponse:
        """Send one httpx call."""


class HttpxTransport:
    def __init__(self, base_url: str, client: HttpxClient) -> None:
        self._base_url = base_url
        self._client = client

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
        timeout: float,
    ) -> TransportResponse:
        validate_timeout(timeout)
        try:
            response = self._client.request(
                method,
                build_url(self._base_url, path, None),
                params=query,
                json=json_body,
                timeout=timeout,
            )
        except httpx.RequestError as error:
            raise ConnectionFailure("httpx call failed") from error
        return TransportResponse(
            response.status_code,
            dict(response.headers),
            response.content,
        )


class TaskClient:
    def __init__(self, transport: TaskTransport) -> None:
        self._transport = transport

    def get_task(self, task_id: int, *, timeout: float = 5.0) -> Task:
        if task_id <= 0:
            raise ValueError("task ID must be positive")
        response = self._transport.request(
            "GET",
            f"/tasks/{task_id}",
            timeout=timeout,
        )
        return decode_task(response)


TASK_BODY = json.dumps(
    {"id": 1, "title": "Compare clients", "completed": False}
).encode("utf-8")
JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}


class FakeUrllibResponse:
    def __init__(self) -> None:
        self.status = 200
        self.headers: Mapping[str, str] = JSON_HEADERS
        self.closed = False

    def read(self) -> bytes:
        return TASK_BODY

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.closed = True


class FakeOpener:
    def __init__(self) -> None:
        self.response = FakeUrllibResponse()
        self.timeout: float | None = None

    def open(self, request: Request, *, timeout: float) -> UrllibResponse:
        assert request.full_url.endswith("/tasks/1")
        self.timeout = timeout
        return self.response


@dataclass
class FakeLibraryResponse:
    status_code: int = 200
    headers: Mapping[str, str] = field(default_factory=lambda: JSON_HEADERS)
    content: bytes = TASK_BODY


class FakeRequestsSession:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.timeout: float | None = None

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
    ) -> RequestsResponse:
        del params, json
        if self.fail:
            raise requests.ConnectionError("offline fake")
        assert method == "GET" and url.endswith("/tasks/1")
        self.timeout = timeout
        return FakeLibraryResponse()


class FakeHttpxClient:
    def __init__(self) -> None:
        self.timeout: float | None = None

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
    ) -> HttpxResponse:
        del params, json
        assert method == "GET" and url.endswith("/tasks/1")
        self.timeout = timeout
        return FakeLibraryResponse()


def test_http_clients() -> None:
    opener = FakeOpener()
    requests_session = FakeRequestsSession()
    httpx_client = FakeHttpxClient()
    transports: list[TaskTransport] = [
        UrllibTransport("http://example.invalid", opener),
        RequestsTransport("http://example.invalid", requests_session),
        HttpxTransport("http://example.invalid", httpx_client),
    ]

    for transport in transports:
        assert TaskClient(transport).get_task(
            1,
            timeout=1.25,
        ) == Task(1, "Compare clients", False)

    assert opener.timeout == requests_session.timeout == httpx_client.timeout == 1.25
    assert opener.response.closed

    api_response = TransportResponse(
        404,
        JSON_HEADERS,
        b'{"error":{"code":"not_found","message":"task 9 was not found"}}',
    )
    try:
        decode_task(api_response)
    except ApiError as error:
        assert (error.status, error.code) == (404, "not_found")
    else:
        raise AssertionError("non-success status should raise ApiError")

    malformed = TransportResponse(
        200,
        JSON_HEADERS,
        b'{"id":true,"title":"Bad ID","completed":false}',
    )
    try:
        decode_task(malformed)
    except MalformedResponse:
        pass
    else:
        raise AssertionError("malformed success body should be rejected")

    failing = RequestsTransport(
        "http://example.invalid",
        FakeRequestsSession(fail=True),
    )
    try:
        TaskClient(failing).get_task(1, timeout=1.0)
    except ConnectionFailure:
        pass
    else:
        raise AssertionError("connection errors should be translated")


if __name__ == "__main__":
    test_http_clients()
    print("urllib, requests, and httpx client checks passed!")
