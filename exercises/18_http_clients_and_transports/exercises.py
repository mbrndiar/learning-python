"""Exercises: Chapter 18 - HTTP Clients and Transports.

Implement raw query parsing, URL encoding, strict response decoding, and three
transports (urllib, Requests, HTTPX) behind one shared contract. Every check is
offline: the evaluator injects fake openers, sessions, and clients, so no socket
is ever opened.

Run from the repository root:

    python exercises/18_http_clients_and_transports/exercises.py

The untouched starter fails first in the "query parsing and URL encoding" group.
Implement the TODO blocks until all five groups pass. The reference solution
stays locked until you have attempted the exercise.
"""

import io
import json
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from email.message import Message
from typing import Protocol, Self
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode
from urllib.request import Request

import httpx
import requests


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
    """The server replied, but not with the documented representation."""


class ApiError(Exception):
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


# --- Injected backend and transport Protocols --------------------------------
# Typed structural interfaces let each transport describe exactly what it needs
# from its backend, so TaskClient depends on `Transport` rather than `object`.


class UrllibResponseLike(Protocol):
    status: int
    headers: Message

    def read(self) -> bytes: ...

    def close(self) -> None: ...


class OpenerLike(Protocol):
    def open(self, request: Request, *, timeout: float) -> UrllibResponseLike: ...

    def close(self) -> None: ...


class LibResponseLike(Protocol):
    @property
    def status_code(self) -> int: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def content(self) -> bytes: ...

    def close(self) -> None: ...


class SessionLike(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
        allow_redirects: bool,
    ) -> LibResponseLike: ...

    def close(self) -> None: ...


class ClientLike(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
        follow_redirects: bool,
    ) -> LibResponseLike: ...

    def close(self) -> None: ...


class Transport(Protocol):
    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> TransportResponse:
        """Make exactly one attempt and return neutral response data."""

    def close(self) -> None:
        """Release the owned backend resource, idempotently."""

    def __enter__(self) -> Self:
        """Transfer transport ownership to a context manager."""

    def __exit__(self, *exc: object) -> None:
        """Release the transport when leaving the context."""


# Provided helper: serialize an optional JSON body to bytes and the matching
# request headers. urllib has no `json=` convenience, so its transport uses this.
def _encode_json_body(
    json_body: Mapping[str, object] | None,
) -> tuple[bytes | None, dict[str, str]]:
    headers = {"Accept": "application/json"}
    if json_body is None:
        return None, headers
    body = json.dumps(dict(json_body)).encode("utf-8")
    headers["Content-Type"] = "application/json"
    return body, headers


# --- Group 1: raw query parsing and URL encoding ------------------------------


def parse_raw_query(query: str) -> dict[str, list[str]]:
    """Parse a raw query string, preserving repeated values as lists.

    An empty string returns an empty dict. Blank values are kept.
    """
    # TODO: use parse_qs; keep blank values and preserve repeated keys as lists
    raise NotImplementedError


def build_url(base_url: str, path: str, query: Mapping[str, str] | None) -> str:
    """Join base + path and append one correctly encoded query string.

    The path must start with "/". A missing or empty query adds no "?".
    """
    # TODO: validate the path, join base and path, and urlencode the query
    raise NotImplementedError


# --- Group 2: case-insensitive headers and strict decoding --------------------


def header_value(headers: Mapping[str, str], name: str) -> str | None:
    """Return one header value looked up case-insensitively, or None."""
    # TODO: compare field names with casefold()
    raise NotImplementedError


def decode_task(response: TransportResponse) -> Task:
    """Validate a response status-first and return a strict Task.

    - A non-200 status in 400..599 raises ApiError from the error envelope;
      any other non-200 status raises MalformedResponse.
    - The Content-Type must be application/json (ignore case and parameters).
    - The body must be UTF-8 JSON with exactly {"id", "title", "completed"}.
    - id is a positive int (NOT a bool), title is a non-empty str, completed is
      a real bool. Remember bool is a subclass of int.
    - Malformed bytes, malformed JSON, and malformed error envelopes all become
      MalformedResponse, never a raw UnicodeDecodeError or JSONDecodeError.
    """
    # TODO: branch on status, decode UTF-8 JSON, and validate shape and values
    raise NotImplementedError


# --- Group 5 policy: timeout validation ---------------------------------------


def validate_timeout(timeout: object) -> float:
    """Return a finite timeout; reject bool, non-numbers, and invalid values."""
    # TODO: reject invalid values and return the normalized float
    raise NotImplementedError


# --- Groups 3/4: concrete transports over injected backends -------------------


class UrllibTransport:
    """Send via an injected urllib-style opener with a finite timeout.

    Owns the opener: close() closes it once (idempotently), the context manager
    closes it on exit, and any send after close raises TransportError.
    """

    def __init__(self, base_url: str, opener: OpenerLike, timeout: object) -> None:
        # TODO: validate the timeout; store base URL, opener, and timeout; start
        # in the open state
        raise NotImplementedError

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> TransportResponse:
        # TODO: reject use after close (TransportError); encode params into the
        # URL and serialize json_body with a Content-Type header; open with the
        # stored timeout; capture and close the response; return an HTTPError as
        # a response and close its body stream; map a URLError timeout reason to
        # TransportTimeout and any other reason to ConnectionFailure.
        raise NotImplementedError

    def close(self) -> None:
        # TODO: close the opener exactly once, idempotently
        raise NotImplementedError

    def __enter__(self) -> "UrllibTransport":
        # TODO: return self
        raise NotImplementedError

    def __exit__(self, *exc: object) -> None:
        # TODO: close on exit
        raise NotImplementedError


class RequestsTransport:
    """Send via an injected Requests-style session.

    Owns the session: close() closes it once (idempotently), the context manager
    closes it on exit, and any send after close raises TransportError.
    """

    def __init__(self, base_url: str, session: SessionLike, timeout: object) -> None:
        # TODO: validate the timeout; store base URL, session, and timeout; start
        # in the open state
        raise NotImplementedError

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> TransportResponse:
        # TODO: reject use after close (TransportError); call session.request with
        # params=, json=, the stored timeout, and allow_redirects=False; copy the
        # status/headers/raw bytes and close the response even if the copy fails;
        # classify Timeout, ConnectionError, and other RequestException into the
        # transport exceptions. Never call raise_for_status().
        raise NotImplementedError

    def close(self) -> None:
        # TODO: close the session exactly once, idempotently
        raise NotImplementedError

    def __enter__(self) -> "RequestsTransport":
        # TODO: return self
        raise NotImplementedError

    def __exit__(self, *exc: object) -> None:
        # TODO: close on exit
        raise NotImplementedError


class HttpxTransport:
    """Send via an injected HTTPX-style client.

    Owns the client: close() closes it once (idempotently), the context manager
    closes it on exit, and any send after close raises TransportError.
    """

    def __init__(self, base_url: str, client: ClientLike, timeout: object) -> None:
        # TODO: validate the timeout; store base URL, client, and timeout; start
        # in the open state
        raise NotImplementedError

    def send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> TransportResponse:
        # TODO: reject use after close (TransportError); call client.request with
        # params=, json=, the stored timeout, and follow_redirects=False; copy the
        # status/headers/raw bytes and close the response even if the copy fails;
        # classify TimeoutException, NetworkError, and other HTTPError into the
        # transport exceptions. Never call raise_for_status().
        raise NotImplementedError

    def close(self) -> None:
        # TODO: close the client exactly once, idempotently
        raise NotImplementedError

    def __enter__(self) -> "HttpxTransport":
        # TODO: return self
        raise NotImplementedError

    def __exit__(self, *exc: object) -> None:
        # TODO: close on exit
        raise NotImplementedError


class TaskClient:
    """Fetch tasks over any Transport using shared status-first policy."""

    def __init__(self, transport: Transport) -> None:
        # TODO: store the transport
        raise NotImplementedError

    def get_task(self, task_id: object) -> Task:
        # TODO: reject bool/non-int/non-positive ids, send one GET, decode the task
        raise NotImplementedError


# --- Offline fakes and evaluator ----------------------------------------------

JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}
TASK_BYTES = b'{"id":1,"title":"Compare clients","completed":false}'
ERROR_BYTES = b'{"error":{"code":"not_found","message":"missing"}}'


def _message(pairs: dict[str, str]) -> Message:
    message = Message()
    for name, value in pairs.items():
        message[name] = value
    return message


class FakeUrllibResponse:
    def __init__(self) -> None:
        self.status = 200
        self.headers = _message(JSON_HEADERS)
        self.closed = False
        self.close_calls = 0

    def read(self) -> bytes:
        return TASK_BYTES

    def close(self) -> None:
        self.closed = True
        self.close_calls += 1


class FakeOpener:
    def __init__(self, outcome: str = "ok") -> None:
        self._outcome = outcome
        self.response = FakeUrllibResponse()
        self.calls = 0
        self.closed = False
        self.close_calls = 0
        self.seen_timeout: float | None = None
        self.seen_url: str | None = None
        self.seen_method: str | None = None
        self.seen_body: bytes | None = None
        self.seen_content_type: str | None = None
        self.error_stream: io.BytesIO | None = None

    def open(self, request: Request, *, timeout: float) -> FakeUrllibResponse:
        self.calls += 1
        self.seen_timeout = timeout
        self.seen_url = request.full_url
        self.seen_method = request.get_method()
        request_body = request.data
        self.seen_body = request_body if isinstance(request_body, bytes) else None
        self.seen_content_type = request.get_header("Content-type")
        if self._outcome == "ok":
            return self.response
        if self._outcome == "http_error":
            self.error_stream = io.BytesIO(ERROR_BYTES)
            raise HTTPError(
                request.full_url,
                404,
                "Not Found",
                _message(JSON_HEADERS),
                self.error_stream,
            )
        if self._outcome == "timeout":
            raise URLError(TimeoutError("timed out"))
        raise URLError("connection refused")

    def close(self) -> None:
        self.closed = True
        self.close_calls += 1


@dataclass
class FakeLibResponse:
    status_code: int = 200
    headers: Mapping[str, str] = field(default_factory=lambda: dict(JSON_HEADERS))
    content: bytes = TASK_BYTES
    closed: bool = False
    close_calls: int = 0

    def close(self) -> None:
        self.closed = True
        self.close_calls += 1

    def raise_for_status(self) -> None:
        raise AssertionError("transport must not call raise_for_status()")


class FakeFailingResponse:
    """A response whose body read fails, to prove the handle is still closed."""

    def __init__(self, error: Exception) -> None:
        self.status_code = 200
        self.headers = dict(JSON_HEADERS)
        self._error = error
        self.closed = False
        self.close_calls = 0

    @property
    def content(self) -> bytes:
        raise self._error

    def close(self) -> None:
        self.closed = True
        self.close_calls += 1

    def raise_for_status(self) -> None:
        raise AssertionError("transport must not call raise_for_status()")


class FakeRequestsSession:
    def __init__(
        self,
        outcome: str = "ok",
        response: LibResponseLike | None = None,
    ) -> None:
        self._outcome = outcome
        self._response = response
        self.calls = 0
        self.closed = False
        self.close_calls = 0
        self.last_response: LibResponseLike | None = None
        self.last_created_response: FakeLibResponse | None = None
        self.seen_method: str | None = None
        self.seen_url: str | None = None
        self.seen_params: object = "unset"
        self.seen_json: object = "unset"
        self.seen_timeout: float | None = None
        self.seen_allow_redirects: object = "unset"

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
        allow_redirects: bool,
    ) -> LibResponseLike:
        self.calls += 1
        self.seen_method = method
        self.seen_url = url
        self.seen_params = params
        self.seen_json = json
        self.seen_timeout = timeout
        self.seen_allow_redirects = allow_redirects
        if self._outcome == "timeout":
            raise requests.Timeout("slow")
        if self._outcome == "connection":
            raise requests.ConnectionError("down")
        if self._outcome == "other":
            raise requests.TooManyRedirects("loop")
        if self._response is not None:
            self.last_response = self._response
        else:
            self.last_created_response = FakeLibResponse()
            self.last_response = self.last_created_response
        return self.last_response

    def close(self) -> None:
        self.closed = True
        self.close_calls += 1


class FakeHttpxClient:
    def __init__(
        self,
        outcome: str = "ok",
        response: LibResponseLike | None = None,
    ) -> None:
        self._outcome = outcome
        self._response = response
        self.calls = 0
        self.closed = False
        self.close_calls = 0
        self.last_response: LibResponseLike | None = None
        self.last_created_response: FakeLibResponse | None = None
        self.seen_method: str | None = None
        self.seen_url: str | None = None
        self.seen_params: object = "unset"
        self.seen_json: object = "unset"
        self.seen_timeout: float | None = None
        self.seen_follow_redirects: object = "unset"

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None,
        json: Mapping[str, object] | None,
        timeout: float,
        follow_redirects: bool,
    ) -> LibResponseLike:
        self.calls += 1
        self.seen_method = method
        self.seen_url = url
        self.seen_params = params
        self.seen_json = json
        self.seen_timeout = timeout
        self.seen_follow_redirects = follow_redirects
        if self._outcome == "timeout":
            raise httpx.ReadTimeout("slow")
        if self._outcome == "network":
            raise httpx.ConnectError("down")
        if self._outcome == "other":
            raise httpx.HTTPError("boom")
        if self._response is not None:
            self.last_response = self._response
        else:
            self.last_created_response = FakeLibResponse()
            self.last_response = self.last_created_response
        return self.last_response

    def close(self) -> None:
        self.closed = True
        self.close_calls += 1


def _json_response(
    status: int, headers: Mapping[str, str], body: bytes
) -> TransportResponse:
    return TransportResponse(status, headers, body)


def evaluate_query_and_url() -> None:
    assert parse_raw_query("") == {}
    assert parse_raw_query("completed=false") == {"completed": ["false"]}
    assert parse_raw_query("tag=a&tag=b") == {"tag": ["a", "b"]}
    assert parse_raw_query("completed=") == {"completed": [""]}

    assert (
        build_url("http://api.invalid/", "/tasks", None) == "http://api.invalid/tasks"
    )
    assert (
        build_url("http://api.invalid", "/tasks", {"completed": "false", "q": "a b"})
        == "http://api.invalid/tasks?completed=false&q=a+b"
    )
    try:
        build_url("http://api.invalid", "tasks", None)
    except ValueError:
        pass
    else:
        raise AssertionError("a path without a leading / must be rejected")


def evaluate_headers_and_decoding() -> None:
    assert header_value({"Content-Type": "application/json"}, "content-type") == (
        "application/json"
    )
    assert header_value({"X-Trace": "abc"}, "x-trace") == "abc"
    assert header_value({}, "missing") is None

    ok = decode_task(_json_response(200, JSON_HEADERS, TASK_BYTES))
    assert ok == Task(1, "Compare clients", False)

    try:
        decode_task(_json_response(404, JSON_HEADERS, ERROR_BYTES))
    except ApiError as error:
        assert (error.status, error.code) == (404, "not_found")
    else:
        raise AssertionError("a 404 must not decode as a Task")

    # Every malformed body becomes MalformedResponse, never a raw exception.
    malformed_bodies = [
        b'{"id":true,"title":"x","completed":false}',  # bool is an int subclass
        b'{"id":0,"title":"x","completed":false}',
        b'{"id":1,"title":"","completed":false}',
        b'{"id":1,"title":"x","completed":"no"}',
        b'{"id":1,"title":"x"}',
        b"\xff\xfe\xfa",  # not valid UTF-8
        b'{"id":1,"title":',  # not valid JSON
    ]
    for body in malformed_bodies:
        try:
            decode_task(_json_response(200, JSON_HEADERS, body))
        except MalformedResponse:
            pass
        else:
            raise AssertionError(f"body should be malformed: {body!r}")

    # Malformed structured error envelopes are MalformedResponse, not ApiError.
    malformed_envelopes = [
        (500, b'{"error":"oops"}'),  # error is not an object
        (400, b'{"nope":1}'),  # missing error key
        (503, b"\xff\xfe"),  # not valid UTF-8
    ]
    for status, body in malformed_envelopes:
        try:
            decode_task(_json_response(status, JSON_HEADERS, body))
        except MalformedResponse:
            pass
        else:
            raise AssertionError(f"envelope should be malformed: {status} {body!r}")

    # An unexpected non-2xx, non-4xx/5xx status is malformed, not an ApiError.
    try:
        decode_task(_json_response(302, JSON_HEADERS, TASK_BYTES))
    except MalformedResponse:
        pass
    else:
        raise AssertionError("an unexpected status must be MalformedResponse")

    try:
        decode_task(_json_response(200, {"Content-Type": "text/plain"}, TASK_BYTES))
    except MalformedResponse:
        pass
    else:
        raise AssertionError("a non-JSON content type must be rejected")


def evaluate_urllib_transport() -> None:
    opener = FakeOpener("ok")
    transport = UrllibTransport("http://api.invalid", opener, timeout=3.5)
    response = transport.send("GET", "/tasks", params={"completed": "false"})
    assert response.status == 200
    assert response.body == TASK_BYTES
    assert opener.seen_url == "http://api.invalid/tasks?completed=false"
    assert opener.seen_method == "GET"
    assert opener.seen_timeout == 3.5
    assert opener.seen_body is None
    assert opener.response.closed is True
    assert opener.response.close_calls == 1
    assert opener.calls == 1

    # A JSON body is serialized with an explicit Content-Type; exact bytes seen.
    post_opener = FakeOpener("ok")
    UrllibTransport("http://api.invalid", post_opener, timeout=1.0).send(
        "POST", "/tasks", json_body={"title": "Write bytes"}
    )
    assert post_opener.seen_method == "POST"
    assert post_opener.seen_body == b'{"title": "Write bytes"}'
    assert post_opener.seen_content_type == "application/json"

    # HTTPError is response-bearing: status and body survive, stream is closed.
    err_opener = FakeOpener("http_error")
    http_error = UrllibTransport("http://api.invalid", err_opener, timeout=1.0).send(
        "GET", "/tasks/9"
    )
    assert http_error.status == 404
    assert http_error.body == ERROR_BYTES
    assert err_opener.error_stream is not None
    assert err_opener.error_stream.closed is True
    assert err_opener.calls == 1

    for outcome, expected in (
        ("timeout", TransportTimeout),
        ("refused", ConnectionFailure),
    ):
        failing = FakeOpener(outcome)
        try:
            UrllibTransport("http://api.invalid", failing, timeout=1.0).send(
                "GET", "/tasks/1"
            )
        except expected:
            pass
        else:
            raise AssertionError(f"{outcome} must raise {expected.__name__}")
        assert failing.calls == 1  # exactly one attempt, no retry

    # Ownership: closing the transport closes the opener, idempotently, and a
    # send after close is rejected.
    owned = FakeOpener("ok")
    with UrllibTransport("http://api.invalid", owned, timeout=1.0) as ctx:
        ctx.send("GET", "/tasks/1")
    assert owned.closed is True
    try:
        ctx.send("GET", "/tasks/1")
    except TransportError:
        pass
    else:
        raise AssertionError("a send after close must raise TransportError")
    ctx.close()  # idempotent
    assert owned.close_calls == 1


def evaluate_requests_and_httpx_transports() -> None:
    session = FakeRequestsSession("ok")
    requests_transport = RequestsTransport("http://api.invalid", session, timeout=2.5)
    response = requests_transport.send("GET", "/tasks", params={"completed": "false"})
    assert response.body == TASK_BYTES
    assert session.seen_url == "http://api.invalid/tasks"
    assert session.seen_params == {"completed": "false"}
    assert session.seen_json is None
    assert session.seen_timeout == 2.5
    assert session.seen_allow_redirects is False
    assert session.calls == 1
    assert session.last_created_response is not None
    assert session.last_created_response.close_calls == 1
    requests_transport.send("POST", "/tasks", json_body={"title": "Write bytes"})
    assert session.seen_json == {"title": "Write bytes"}

    # A non-2xx response is preserved verbatim; raise_for_status is never called.
    not_found = FakeLibResponse(status_code=404, content=ERROR_BYTES)
    nf_session = FakeRequestsSession("ok", response=not_found)
    nf = RequestsTransport("http://api.invalid", nf_session, timeout=1.0).send(
        "GET", "/tasks/9"
    )
    assert nf.status == 404
    assert nf.body == ERROR_BYTES
    assert not_found.closed is True

    # A body-read failure still closes the response and is classified.
    failing_body = FakeFailingResponse(requests.ConnectionError("boom"))
    fb_session = FakeRequestsSession("ok", response=failing_body)
    try:
        RequestsTransport("http://api.invalid", fb_session, timeout=1.0).send(
            "GET", "/tasks/1"
        )
    except ConnectionFailure:
        pass
    else:
        raise AssertionError("a failed body read must map to ConnectionFailure")
    assert failing_body.closed is True
    assert fb_session.calls == 1

    client = FakeHttpxClient("ok")
    httpx_transport = HttpxTransport("http://api.invalid", client, timeout=4.0)
    httpx_transport.send("POST", "/tasks", json_body={"title": "Write bytes"})
    assert client.seen_url == "http://api.invalid/tasks"
    assert client.seen_json == {"title": "Write bytes"}
    assert client.seen_params is None
    assert client.seen_timeout == 4.0
    assert client.seen_follow_redirects is False
    assert client.calls == 1
    assert client.last_created_response is not None
    assert client.last_created_response.close_calls == 1

    httpx_not_found = FakeLibResponse(status_code=404, content=ERROR_BYTES)
    nf_client = FakeHttpxClient("ok", response=httpx_not_found)
    nf2 = HttpxTransport("http://api.invalid", nf_client, timeout=1.0).send(
        "GET", "/tasks/9"
    )
    assert nf2.status == 404
    assert nf2.body == ERROR_BYTES
    assert httpx_not_found.close_calls == 1

    httpx_failing_body = FakeFailingResponse(httpx.ConnectError("boom"))
    failing_client = FakeHttpxClient("ok", response=httpx_failing_body)
    try:
        HttpxTransport("http://api.invalid", failing_client, timeout=1.0).send(
            "GET", "/tasks/1"
        )
    except ConnectionFailure:
        pass
    else:
        raise AssertionError("a failed body read must map to ConnectionFailure")
    assert httpx_failing_body.close_calls == 1

    requests_cases = (
        ("timeout", TransportTimeout),
        ("connection", ConnectionFailure),
        ("other", TransportError),
    )
    for outcome, expected in requests_cases:
        failing_session = FakeRequestsSession(outcome)
        try:
            RequestsTransport("http://api.invalid", failing_session, timeout=1.0).send(
                "GET", "/tasks/1"
            )
        except expected:
            pass
        else:
            raise AssertionError(f"requests {outcome} must raise {expected.__name__}")
        assert failing_session.calls == 1

    httpx_cases = (
        ("timeout", TransportTimeout),
        ("network", ConnectionFailure),
        ("other", TransportError),
    )
    for outcome, expected in httpx_cases:
        failing_httpx_client = FakeHttpxClient(outcome)
        try:
            HttpxTransport(
                "http://api.invalid",
                failing_httpx_client,
                timeout=1.0,
            ).send("GET", "/tasks/1")
        except expected:
            pass
        else:
            raise AssertionError(f"httpx {outcome} must raise {expected.__name__}")
        assert failing_httpx_client.calls == 1

    # Ownership: closing each transport closes its backend and blocks reuse.
    owned_session = FakeRequestsSession("ok")
    with RequestsTransport("http://api.invalid", owned_session, timeout=1.0) as rt:
        rt.send("GET", "/tasks/1")
    assert owned_session.closed is True
    try:
        rt.send("GET", "/tasks/1")
    except TransportError:
        pass
    else:
        raise AssertionError("a send after close must raise TransportError")
    rt.close()
    assert owned_session.close_calls == 1

    owned_client = FakeHttpxClient("ok")
    with HttpxTransport("http://api.invalid", owned_client, timeout=1.0) as ht:
        ht.send("GET", "/tasks/1")
    assert owned_client.closed is True
    try:
        ht.send("GET", "/tasks/1")
    except TransportError:
        pass
    else:
        raise AssertionError("a send after close must raise TransportError")
    ht.close()
    assert owned_client.close_calls == 1


def evaluate_common_contract() -> None:
    for bad in (0, -1, float("inf"), float("nan"), True, "1"):
        try:
            validate_timeout(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"timeout {bad!r} must be rejected")
    validate_timeout(0.25)

    opener = FakeOpener("ok")
    session = FakeRequestsSession("ok")
    client = FakeHttpxClient("ok")
    transports: list[Transport] = [
        UrllibTransport("http://api.invalid", opener, timeout=2.0),
        RequestsTransport("http://api.invalid", session, timeout=2.0),
        HttpxTransport("http://api.invalid", client, timeout=2.0),
    ]
    expected = Task(1, "Compare clients", False)
    for transport in transports:
        assert TaskClient(transport).get_task(1) == expected
    assert opener.calls == 1
    assert session.calls == 1
    assert client.calls == 1

    # TaskClient rejects bool, non-int, and non-positive ids before sending.
    guard = FakeOpener("ok")
    bad_client = TaskClient(UrllibTransport("http://api.invalid", guard, timeout=1.0))
    for bad_id in (0, -1, True, "1", 1.0):
        try:
            bad_client.get_task(bad_id)
        except ValueError:
            pass
        else:
            raise AssertionError(f"task id {bad_id!r} must be rejected")
    assert guard.calls == 0

    failing = UrllibTransport("http://api.invalid", FakeOpener("timeout"), timeout=1.0)
    try:
        TaskClient(failing).get_task(1)
    except TransportTimeout:
        pass
    else:
        raise AssertionError("client must surface transport failures")

    # Every backend resource is released through the context-manager protocol.
    owned_opener = FakeOpener("ok")
    owned_session = FakeRequestsSession("ok")
    owned_client = FakeHttpxClient("ok")
    owned_transports: list[Transport] = [
        UrllibTransport("http://api.invalid", owned_opener, timeout=1.0),
        RequestsTransport("http://api.invalid", owned_session, timeout=1.0),
        HttpxTransport("http://api.invalid", owned_client, timeout=1.0),
    ]
    for transport in owned_transports:
        with transport as active:
            active.send("GET", "/tasks/1")
    assert owned_opener.closed is True
    assert owned_session.closed is True
    assert owned_client.closed is True
    assert owned_opener.close_calls == 1
    assert owned_session.close_calls == 1
    assert owned_client.close_calls == 1


def run_evaluation(label: str, evaluation: Callable[[], None]) -> None:
    try:
        evaluation()
    except NotImplementedError as error:
        raise AssertionError(f"{label}: implement the remaining TODO") from error
    print(f"{label}: OK")


if __name__ == "__main__":
    run_evaluation("query parsing and URL encoding", evaluate_query_and_url)
    run_evaluation("headers and strict decoding", evaluate_headers_and_decoding)
    run_evaluation("urllib transport", evaluate_urllib_transport)
    run_evaluation(
        "requests and httpx transports", evaluate_requests_and_httpx_transports
    )
    run_evaluation("common contract", evaluate_common_contract)
    print("\nAll checks passed!")
