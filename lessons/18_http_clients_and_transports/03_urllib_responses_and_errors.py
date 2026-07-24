"""
Chapter 18, Lesson 3: urllib Responses and Errors

Purpose: handle the two failure shapes urllib produces. `HTTPError` is raised
for non-2xx statuses but *is itself a response* carrying status, headers, and a
readable body. `URLError` means no HTTP response arrived at all; its `reason`
distinguishes a finite-timeout expiry from other connection failures.

Prerequisite: Lesson 1's opener/response ownership and Lesson 2's status-first
validation. This lesson stays offline by injecting a fake opener that returns a
success, raises `HTTPError`, or raises `URLError` on demand.

Rule: catch only the transport exceptions you understand. Do not wrap unrelated
exceptions (for example a `ValueError` from your own code) in a connection
category, because that would hide real bugs.

Run from the repository root:

    python lessons/18_http_clients_and_transports/03_urllib_responses_and_errors.py
"""

import io
import math
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import Message
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class TransportTimeout(Exception):
    """The finite timeout expired before any response arrived."""


class ConnectionFailure(Exception):
    """No HTTP response was produced for a non-timeout reason."""


# Step 0: describe the opener and response as structural Protocols. Anything with
# the right shape satisfies them, so a real urllib response and an HTTPError both
# fit without casts or `# type: ignore`. `ResponseBody` is the read/close surface
# shared by a success response and an HTTPError (which *is* a response). The
# opener's response also exposes a numeric `status`.
class ResponseBody(Protocol):
    headers: Message

    def read(self) -> bytes:
        """Read the full body as bytes."""

    def close(self) -> None:
        """Release the network handle."""


class OpenerResponse(ResponseBody, Protocol):
    status: int


class UrlOpener(Protocol):
    def open(self, request: Request, *, timeout: float) -> OpenerResponse:
        """Open one request with a finite timeout and return one response."""


# Step 1: capture a live response into owned bytes, then close the handle. The
# same helper serves both the success path and the HTTPError path, because an
# HTTPError exposes read()/headers/close() just like a normal response.
def _capture(response: ResponseBody, status: int) -> TransportResponse:
    try:
        body = response.read()
        headers = dict(response.headers)
        return TransportResponse(status, headers, body)
    finally:
        response.close()


# Step 2: reject an unusable timeout before opening anything. A real, finite,
# positive number is required; bool (an int subclass), NaN, and infinity are not
# valid finite timeouts.
def _validated_timeout(timeout: object) -> float:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a real number")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    return float(timeout)


# Step 3: send one request and translate urllib's failure shapes. The order of
# except clauses matters: HTTPError is a subclass of URLError, so it must be
# caught first to preserve the response it carries.
def send(opener: UrlOpener, request: Request, *, timeout: object) -> TransportResponse:
    checked_timeout = _validated_timeout(timeout)
    try:
        response = opener.open(request, timeout=checked_timeout)
        return _capture(response, response.status)
    except HTTPError as error:
        # Non-2xx: still a full response. Keep its status/headers/body and make
        # sure the body is read and the handle is closed.
        return _capture(error, error.code)
    except URLError as error:
        # No response at all. reason tells us whether the finite timeout expired
        # or the connection failed for another reason.
        if isinstance(error.reason, TimeoutError):
            raise TransportTimeout("request timed out") from error
        raise ConnectionFailure(str(error.reason)) from error
    except TimeoutError as error:
        # A bare socket timeout can also surface directly.
        raise TransportTimeout("request timed out") from error


# --- Offline fake opener -------------------------------------------------------


def _headers(pairs: dict[str, str]) -> Message:
    message = Message()
    for name, value in pairs.items():
        message[name] = value
    return message


class ScriptedOpener:
    """Return a canned response or raise a scripted urllib failure."""

    def __init__(self, outcome: str) -> None:
        self._outcome = outcome
        self.closed = False
        self.opened = False

    def open(self, request: Request, *, timeout: float) -> OpenerResponse:
        del timeout
        self.opened = True
        if self._outcome == "ok":
            return _CannedResponse(
                200,
                _headers({"Content-Type": "application/json; charset=utf-8"}),
                b'{"id":1}',
                self,
            )
        if self._outcome == "http_error":
            raise HTTPError(
                request.full_url,
                404,
                "Not Found",
                _headers({"Content-Type": "application/json; charset=utf-8"}),
                io.BytesIO(b'{"error":{"code":"not_found","message":"gone"}}'),
            )
        if self._outcome == "timeout":
            raise URLError(TimeoutError("timed out"))
        raise URLError("connection refused")


class _CannedResponse:
    def __init__(
        self, status: int, headers: Message, body: bytes, owner: ScriptedOpener
    ) -> None:
        self.status = status
        self.headers = headers
        self._body = body
        self._owner = owner

    def read(self) -> bytes:
        return self._body

    def close(self) -> None:
        self._owner.closed = True


if __name__ == "__main__":
    request = Request("http://tasks.invalid/tasks/1", method="GET")

    opener = ScriptedOpener("ok")
    ok = send(opener, request, timeout=2.0)
    assert ok.status == 200
    assert ok.body == b'{"id":1}'
    assert opener.closed is True

    # HTTPError still carries the response, so status/headers/body survive.
    http_error = send(ScriptedOpener("http_error"), request, timeout=2.0)
    assert http_error.status == 404
    assert http_error.body.startswith(b'{"error"')
    assert http_error.headers["Content-Type"] == "application/json; charset=utf-8"

    try:
        send(ScriptedOpener("timeout"), request, timeout=2.0)
    except TransportTimeout:
        pass
    else:
        raise AssertionError("timeout reason must map to TransportTimeout")

    try:
        send(ScriptedOpener("refused"), request, timeout=2.0)
    except ConnectionFailure:
        pass
    else:
        raise AssertionError("non-timeout URLError must map to ConnectionFailure")

    # Every invalid timeout is rejected before the opener is ever consulted.
    for bad in (True, "2", float("nan"), float("inf"), 0, -1.0):
        guard = ScriptedOpener("ok")
        try:
            send(guard, request, timeout=bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"timeout {bad!r} must be rejected")
        assert guard.opened is False, "backend must not be reached"

    print("success status:", ok.status)
    print("HTTPError-as-response status:", http_error.status, http_error.body)
    print("timeout and connection failures classified distinctly")
