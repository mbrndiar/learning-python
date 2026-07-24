"""
Chapter 18, Lesson 1: URLs, Queries, and urllib.request

Purpose: build a request URL with correct percent-encoding, construct a
`urllib.request.Request`, and open it through an *opener* with a finite timeout
while owning the response lifetime with a context manager.

Prerequisite: Chapter 16's URL components and query parsing, the `with`
statement from Chapter 7, and the custom context-manager protocol
(`__enter__`/`__exit__`) from Chapter 10. This lesson introduces the client side
of one HTTP exchange; Chapter 16 built the server side.

This demo performs no real networking. It injects a fake opener that satisfies
the same small interface the real `urllib.request` opener exposes, so every
result is deterministic and offline.

Run from the repository root:

    python lessons/18_http_clients_and_transports/01_urls_queries_and_urllib_request.py
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import Protocol, Self
from urllib.parse import urlencode
from urllib.request import Request


@dataclass(frozen=True)
class TransportResponse:
    """Library-neutral response captured after the network handle is closed."""

    status: int
    headers: Mapping[str, str]
    body: bytes


# Step 1: build the URL yourself with urlencode() so query values are
# percent-encoded exactly once. A base URL plus a path plus an encoded query is
# far safer than string concatenation, which would mishandle spaces and "&".
def build_url(base_url: str, path: str, query: Mapping[str, str] | None) -> str:
    if not path.startswith("/"):
        raise ValueError("path must start with /")
    url = f"{base_url.rstrip('/')}{path}"
    if not query:
        return url
    return f"{url}?{urlencode(query)}"


# Step 2: a Request bundles the target, method, headers, and optional body bytes.
# The method is explicit; the body must already be bytes, never str. Building the
# Request does not open a connection, so it is cheap to inspect and test.
def build_request(url: str, method: str, body: bytes | None) -> Request:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    return Request(url, data=body, headers=headers, method=method)


# Step 3: an *opener* performs the actual exchange. The real
# urllib.request.build_opener() returns an object with this same open() shape.
# We inject one so the lesson stays offline. The opener never keeps a persistent
# process open; each call yields one response we must close.
class UrllibResponse(Protocol):
    status: int
    headers: Mapping[str, str]

    def read(self) -> bytes:
        """Read the full response body as bytes."""

    def __enter__(self) -> Self:
        """Enter the response context, transferring ownership to the caller."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the network handle when leaving the context."""


class UrlOpener(Protocol):
    def open(self, request: Request, *, timeout: float) -> UrllibResponse:
        """Open one request with a finite timeout and return one response."""


# Step 4: fetch owns the response lifetime. The `with` block guarantees the
# handle is closed even if read() raises, and the timeout is validated to be a
# real, finite, positive number so a stalled peer cannot block the program
# forever. `bool` is an `int` subclass, so it is rejected before the numeric
# checks; NaN and infinity are not finite and are rejected too.
def _validated_timeout(timeout: object) -> float:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a real number")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    return float(timeout)


def fetch(opener: UrlOpener, request: Request, *, timeout: object) -> TransportResponse:
    checked_timeout = _validated_timeout(timeout)
    with opener.open(request, timeout=checked_timeout) as response:
        return TransportResponse(
            response.status,
            dict(response.headers),
            response.read(),
        )


# --- Offline fake opener -------------------------------------------------------
# The fake records the timeout and whether the response was closed so the demo
# can prove ownership without touching a socket.


class FakeResponse:
    def __init__(self, status: int, headers: Mapping[str, str], body: bytes) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.closed = False

    def read(self) -> bytes:
        return self.body

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
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.seen_url: str | None = None
        self.seen_method: str | None = None
        self.seen_timeout: float | None = None

    def open(self, request: Request, *, timeout: float) -> UrllibResponse:
        self.seen_url = request.full_url
        self.seen_method = request.get_method()
        self.seen_timeout = timeout
        return self.response


if __name__ == "__main__":
    url = build_url(
        "http://tasks.invalid/",
        "/tasks",
        {"completed": "false", "q": "read http"},
    )
    assert url == "http://tasks.invalid/tasks?completed=false&q=read+http"

    request = build_request(url, "GET", None)
    assert request.get_method() == "GET"
    assert request.full_url == url
    assert request.data is None

    response = FakeResponse(
        200,
        {"Content-Type": "application/json; charset=utf-8"},
        b'{"tasks":[]}',
    )
    opener = FakeOpener(response)
    result = fetch(opener, request, timeout=2.5)

    assert result.status == 200
    assert result.body == b'{"tasks":[]}'
    assert opener.seen_timeout == 2.5
    assert opener.seen_method == "GET"
    assert response.closed is True

    # Every invalid timeout is rejected before the opener is ever consulted.
    for bad in (True, "2", float("nan"), float("inf"), 0, -1.0):
        guard = FakeOpener(FakeResponse(200, {}, b""))
        try:
            fetch(guard, request, timeout=bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"timeout {bad!r} must be rejected")
        assert guard.seen_timeout is None, "backend must not be reached"

    print("url:", url)
    print("method:", request.get_method())
    print("status:", result.status, "body:", result.body)
    print("timeout seen by opener:", opener.seen_timeout)
    print("response closed:", response.closed)
