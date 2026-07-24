"""
Chapter 18, Lesson 6: Transport Contract and Client Policy

Purpose: only *after* each concrete client lifecycle is understood, unify them
behind one small `Protocol`. A `Transport` sends one request with a caller-chosen
timeout and returns library-neutral response data. A `TaskClient` then holds the
shared policy: validate the timeout once, pass it to every attempt, branch on
status first, and make exactly one attempt per call.

Prerequisite: Lessons 1-5. urllib (Lesson 3), Requests (Lesson 4), and HTTPX
(Lesson 5) already reduced their libraries to the same captured response. This
lesson proves those three are interchangeable under one interface and that the
client's timeout is really observed by each backend.

Policy decisions made explicit here:
- The timeout must be a real, positive, finite number (a bool is not a valid
  timeout, because bool is an int subclass). The client validates it once and
  threads the same value through `send()`; each transport revalidates and passes
  it to its backend, so `TaskClient(timeout=2.5)` makes every backend observe
  2.5 rather than a hidden hard-coded default.
- There are NO automatic retries in this chapter. Retrying a non-idempotent
  request (POST/PATCH) could duplicate effects, so the contract makes exactly
  one network attempt per call. Retry policy belongs to a later layer.
- Responses are interpreted status-first with the full Lesson 2 validation
  (content type, UTF-8 JSON, exact shape, strict values, and structured API
  errors), so a raw JSON or Unicode error never leaks to the caller.

Run from the repository root:

    python lessons/18_http_clients_and_transports/06_transport_contract_and_client_policy.py
"""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import Message
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

import httpx
import requests
from requests.adapters import BaseAdapter
from requests.models import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict

JsonScalar = str | int | float | bool | None


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


class MalformedResponse(Exception):
    """The response was not the documented representation."""


class ApiError(Exception):
    """A structured error the server reported with a 4xx or 5xx status."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(f"API error {status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


class TransportTimeout(Exception):
    """The finite timeout expired before a response arrived."""


class ConnectionFailure(Exception):
    """No HTTP response was produced for a non-timeout reason."""


class TransportError(Exception):
    """Any other transport-level failure that is not an HTTP status."""


# Step 1: the shared contract. Every transport reduces its library to this one
# method. `send()` takes the timeout as an argument so the client's policy value
# reaches the wire; nothing above this line knows which client is in use.
class Transport(Protocol):
    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, JsonScalar] | None = None,
        timeout: float,
    ) -> TransportResponse:
        """Make exactly one attempt with this timeout and return neutral data."""

    def close(self) -> None:
        """Release transport-owned resources."""


# Step 2: shared policy helpers.
def validate_timeout(timeout: object) -> float:
    """Reject non-real, non-finite, and non-positive timeouts (bool included)."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a real number")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    return float(timeout)


def _build_url(base_url: str, path: str, params: Mapping[str, str] | None) -> str:
    url = f"{base_url.rstrip('/')}{path}"
    if not params:
        return url
    return f"{url}?{urlencode(dict(params))}"


def _encode_json_body(
    json_body: Mapping[str, JsonScalar] | None,
) -> tuple[bytes | None, dict[str, str]]:
    headers = {"Accept": "application/json"}
    if json_body is None:
        return None, headers
    body = json.dumps(dict(json_body)).encode("utf-8")
    headers["Content-Type"] = "application/json"
    return body, headers


def _media_type(headers: Mapping[str, str]) -> str:
    value = next(
        (v for name, v in headers.items() if name.casefold() == "content-type"),
        "",
    )
    return value.split(";", 1)[0].strip().casefold()


def _decode_json(response: TransportResponse) -> object:
    if _media_type(response.headers) != "application/json":
        raise MalformedResponse("Content-Type was not application/json")
    try:
        return json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MalformedResponse("body was not UTF-8 JSON") from error


def _decode_api_error(response: TransportResponse) -> ApiError:
    value = _decode_json(response)
    if not isinstance(value, dict) or set(value) != {"error"}:
        raise MalformedResponse("error envelope was malformed")
    error = value["error"]
    if not isinstance(error, dict):
        raise MalformedResponse("error details were malformed")
    code = error.get("code")
    message = error.get("message")
    if not isinstance(code, str) or not isinstance(message, str):
        raise MalformedResponse("error code or message was malformed")
    return ApiError(response.status, code, message)


def decode_task(response: TransportResponse) -> Task:
    """Status-first validation: the full Lesson 2 pipeline, no raw exceptions."""
    if response.status != 200:
        if 400 <= response.status <= 599:
            raise _decode_api_error(response)
        raise MalformedResponse(f"unexpected status: {response.status}")

    value = _decode_json(response)
    if not isinstance(value, dict) or set(value) != {"id", "title", "completed"}:
        raise MalformedResponse("task fields were malformed")

    task_id = value["id"]
    title = value["title"]
    completed = value["completed"]
    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
        or not isinstance(title, str)
        or not title
        or not isinstance(completed, bool)
    ):
        raise MalformedResponse("task values were malformed")
    return Task(task_id, title, completed)


# Step 3: the client depends only on the Protocol. It validates the timeout once,
# then threads that same value through every send(). It never retries: one call
# to transport.send() means exactly one network attempt.
class TaskClient:
    def __init__(self, transport: Transport, *, timeout: object) -> None:
        self._transport = transport
        self._timeout = validate_timeout(timeout)

    def get_task(self, task_id: int) -> Task:
        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("task id must be a positive int")
        response = self._transport.send(
            "GET", f"/tasks/{task_id}", timeout=self._timeout
        )
        return decode_task(response)


# Step 4: three concrete transports, one per library, each satisfying Transport.
# Each revalidates the timeout and passes it to its backend, and urllib now
# honors params (query encoding) and json_body (serialization + Content-Type)
# instead of discarding them. They preserve the exception classification each
# library exposes.


class Opener(Protocol):
    def open(self, request: Request, *, timeout: float) -> "OpenerResponse":
        """Open one request with a finite timeout and return one response."""

    def close(self) -> None:
        """Release opener-owned resources."""


class OpenerResponse(Protocol):
    status: int
    headers: Message

    def read(self) -> bytes:
        """Read the full body as bytes."""

    def close(self) -> None:
        """Release the network handle."""


class UrllibTransport:
    def __init__(self, base_url: str, opener: Opener) -> None:
        self._base_url = base_url.rstrip("/")
        self._opener = opener
        self._closed = False

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, JsonScalar] | None = None,
        timeout: float,
    ) -> TransportResponse:
        if self._closed:
            raise TransportError("transport is closed")
        checked_timeout = validate_timeout(timeout)
        body, headers = _encode_json_body(json_body)
        request = Request(
            _build_url(self._base_url, path, params),
            data=body,
            headers=headers,
            method=method,
        )
        try:
            response = self._opener.open(request, timeout=checked_timeout)
            try:
                return TransportResponse(
                    response.status, dict(response.headers), response.read()
                )
            finally:
                response.close()
        except HTTPError as error:
            # HTTPError *is* a response: read and close its body, keep the status.
            with error:
                return TransportResponse(error.code, dict(error.headers), error.read())
        except URLError as error:
            if isinstance(error.reason, TimeoutError):
                raise TransportTimeout("request timed out") from error
            raise ConnectionFailure(str(error.reason)) from error
        except TimeoutError as error:
            raise TransportTimeout("request timed out") from error

    def close(self) -> None:
        if not self._closed:
            self._opener.close()
            self._closed = True


class RequestsTransport:
    def __init__(self, base_url: str, session: requests.Session) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._closed = False

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, JsonScalar] | None = None,
        timeout: float,
    ) -> TransportResponse:
        if self._closed:
            raise TransportError("transport is closed")
        checked_timeout = validate_timeout(timeout)
        try:
            response = self._session.request(
                method,
                f"{self._base_url}{path}",
                params=dict(params) if params else None,
                json=dict(json_body) if json_body is not None else None,
                timeout=checked_timeout,
                allow_redirects=False,
            )
            try:
                return TransportResponse(
                    response.status_code,
                    dict(response.headers),
                    bytes(response.content),
                )
            finally:
                response.close()
        except requests.Timeout as error:
            raise TransportTimeout("request timed out") from error
        except requests.ConnectionError as error:
            raise ConnectionFailure("request failed") from error
        except requests.RequestException as error:
            raise TransportError("request could not be sent") from error

    def close(self) -> None:
        if not self._closed:
            self._session.close()
            self._closed = True


class HttpxTransport:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client
        self._closed = False

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, JsonScalar] | None = None,
        timeout: float,
    ) -> TransportResponse:
        if self._closed:
            raise TransportError("transport is closed")
        checked_timeout = validate_timeout(timeout)
        try:
            response = self._client.request(
                method,
                path,
                params=dict(params) if params else None,
                json=dict(json_body) if json_body is not None else None,
                timeout=httpx.Timeout(checked_timeout),
                follow_redirects=False,
            )
        except httpx.TimeoutException as error:
            raise TransportTimeout("request timed out") from error
        except httpx.NetworkError as error:
            raise ConnectionFailure("network error") from error
        except httpx.HTTPError as error:
            raise TransportError("request could not be sent") from error
        try:
            return TransportResponse(
                response.status_code,
                dict(response.headers),
                bytes(response.content),
            )
        finally:
            response.close()

    def close(self) -> None:
        if not self._closed:
            self._client.close()
            self._closed = True


# --- Offline backends ----------------------------------------------------------
JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}
TASK_BODY = b'{"id":1,"title":"Compare clients","completed":false}'


def _message(pairs: dict[str, str]) -> Message:
    message = Message()
    for name, value in pairs.items():
        message[name] = value
    return message


class _UrllibResponse:
    def __init__(self) -> None:
        self.status = 200
        self.headers = _message(JSON_HEADERS)
        self.closed = False

    def read(self) -> bytes:
        return TASK_BODY

    def close(self) -> None:
        self.closed = True


class FakeOpener:
    def __init__(self) -> None:
        self.response = _UrllibResponse()
        self.calls = 0
        self.seen_timeout: float | None = None
        self.seen_url: str | None = None
        self.seen_body: bytes | None = None
        self.seen_content_type: str | None = None
        self.closed = False

    def open(self, request: Request, *, timeout: float) -> _UrllibResponse:
        self.calls += 1
        self.seen_timeout = timeout
        self.seen_url = request.full_url
        request_body = request.data
        self.seen_body = request_body if isinstance(request_body, bytes) else None
        self.seen_content_type = request.get_header("Content-type")
        return self.response

    def close(self) -> None:
        self.closed = True


class CannedAdapter(BaseAdapter):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0
        self.seen_timeout: object = None

    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: float | tuple[float | None, float | None] | None = None,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        del stream, verify, cert, proxies
        self.calls += 1
        self.seen_timeout = timeout
        response = Response()
        response.status_code = 200
        response.headers = CaseInsensitiveDict(JSON_HEADERS)
        response._content = TASK_BODY
        response.url = request.url or ""
        response.request = request
        return response

    def close(self) -> None:
        pass


class RecordingHandler:
    def __init__(self) -> None:
        self.calls = 0
        self.seen_read_timeout: float | None = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        timeout = request.extensions.get("timeout", {})
        self.seen_read_timeout = timeout.get("read")
        return httpx.Response(200, headers=JSON_HEADERS, content=TASK_BODY)


if __name__ == "__main__":
    opener = FakeOpener()

    requests_adapter = CannedAdapter()
    requests_session = requests.Session()
    requests_session.mount("http://", requests_adapter)

    httpx_recorder = RecordingHandler()
    httpx_client = httpx.Client(
        base_url="http://tasks.invalid",
        transport=httpx.MockTransport(httpx_recorder),
        timeout=httpx.Timeout(5.0),
        follow_redirects=False,
        trust_env=False,
    )

    transports: list[Transport] = [
        UrllibTransport("http://tasks.invalid", opener),
        RequestsTransport("http://tasks.invalid", requests_session),
        HttpxTransport(httpx_client),
    ]

    expected = Task(1, "Compare clients", False)
    results = [TaskClient(t, timeout=2.5).get_task(1) for t in transports]
    assert results == [expected, expected, expected]

    # The client's timeout is not dead policy: every backend observed 2.5.
    assert opener.seen_timeout == 2.5
    assert requests_adapter.seen_timeout == 2.5
    assert httpx_recorder.seen_read_timeout == 2.5

    # Exactly one attempt per call: no retries anywhere.
    assert opener.calls == 1
    assert requests_adapter.calls == 1
    assert httpx_recorder.calls == 1
    assert opener.response.closed is True

    # urllib now honors params (query encoding) and json_body (serialization).
    probe = FakeOpener()
    probe_transport = UrllibTransport("http://tasks.invalid", probe)
    probe_transport.send(
        "POST",
        "/tasks",
        params={"completed": "false"},
        json_body={"title": "Write bytes"},
        timeout=2.5,
    )
    assert probe.seen_url == "http://tasks.invalid/tasks?completed=false"
    assert probe.seen_body == b'{"title": "Write bytes"}'
    assert probe.seen_content_type == "application/json"

    probe_transport.close()
    for transport in transports:
        transport.close()
    assert opener.closed is True

    for bad in (0, -1, float("inf"), float("nan"), True, "1"):
        try:
            validate_timeout(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"timeout {bad!r} must be rejected")

    print("parity across urllib, Requests, and HTTPX:", results[0])
    print("client timeout observed by every backend:", opener.seen_timeout)
    print("one attempt per call; no automatic retries in this chapter")
    print("shared contract and client policy verified")
