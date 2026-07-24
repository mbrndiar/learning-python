"""
Chapter 18, Lesson 5: HTTPX Clients

Purpose: use a synchronous `httpx.Client` idiomatically. A Client owns a
connection pool and a configuration bundle: a `base_url`, a timeout policy,
redirect and proxy behavior. Like Requests it encodes `params`/`json` and
exposes raw bytes as `.content`, and like a Session it must be closed.

Prerequisite: Lesson 4's Requests transport. This lesson highlights what differs
from Requests: HTTPX has a *default* timeout of five seconds of network
inactivity (Requests has none), and it does not follow redirects unless you opt
in with `follow_redirects=True`.

Offline strategy: a real `httpx.Client` is driven by an `httpx.MockTransport`
handler, so URL/query/JSON encoding is genuine while no socket is opened.

Run from the repository root:

    python lessons/18_http_clients_and_transports/05_httpx_clients.py
"""

import math
from collections.abc import Mapping

import httpx


class TransportTimeout(Exception):
    """The configured timeout expired (connect, read, write, or pool)."""


class ConnectionFailure(Exception):
    """A network-level failure prevented a response."""


class TransportError(Exception):
    """Any other HTTPX-level failure that is not a status code."""


# Step 1: the Client bundles configuration once. base_url makes each call use a
# relative path; timeout is explicit even though HTTPX would otherwise default to
# five seconds of inactivity; redirects and proxies are turned off so behavior is
# predictable and hermetic.
def build_client(
    base_url: str, transport: httpx.BaseTransport, timeout: object
) -> httpx.Client:
    # A real, finite, positive number is required. bool is an int subclass, so
    # it is rejected before the numeric checks; NaN and infinity are not finite.
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a real number")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    checked_timeout = float(timeout)
    return httpx.Client(
        base_url=base_url,
        timeout=httpx.Timeout(checked_timeout),
        follow_redirects=False,
        trust_env=False,
        transport=transport,
    )


class HttpxTransport:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client
        self._closed = False

    # Step 2: HTTPX encodes params and json. Read the raw bytes with
    # response.read()/response.content and copy them out. Never call
    # raise_for_status(): a 4xx/5xx stays an ordinary response for later
    # status-first validation.
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        if self._closed:
            raise TransportError("transport is closed")
        try:
            response = self._client.request(
                method,
                path,
                params=dict(params) if params else None,
                json=dict(json_body) if json_body is not None else None,
            )
            return (
                response.status_code,
                dict(response.headers),
                bytes(response.content),
            )
        # Step 3: classify. TimeoutException and NetworkError are both subclasses
        # of httpx.HTTPError, so catch the specific families before the general
        # one. An HTTP status is not an exception unless raise_for_status is used.
        except httpx.TimeoutException as error:
            raise TransportTimeout("request timed out") from error
        except httpx.NetworkError as error:
            raise ConnectionFailure("network error") from error
        except httpx.HTTPError as error:
            raise TransportError("request could not be sent") from error

    # Step 4: cleanup. Close the one owned Client (and its pool) idempotently, and
    # support the context-manager protocol.
    def close(self) -> None:
        if not self._closed:
            self._client.close()
            self._closed = True

    def __enter__(self) -> "HttpxTransport":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


# --- Offline handlers ----------------------------------------------------------
# A recorder object is clearer than stashing attributes on a function: it holds
# the last-seen URL and body as ordinary instance state and is callable, so it
# plugs straight into httpx.MockTransport.


class RecordingHandler:
    def __init__(self) -> None:
        self.last_url: str | None = None
        self.last_body: bytes | None = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.last_url = str(request.url)
        self.last_body = request.content
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json; charset=utf-8"},
            content=b'{"id":1,"title":"Read HTTP","completed":false}',
        )


def _timeout_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("slow", request=request)


def _network_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("down", request=request)


if __name__ == "__main__":
    recorder = RecordingHandler()
    with HttpxTransport(
        build_client("http://tasks.invalid", httpx.MockTransport(recorder), 2.5)
    ) as transport:
        status, headers, body = transport.request(
            "GET", "/tasks", params={"completed": "false"}
        )
        assert status == 200
        assert body == b'{"id":1,"title":"Read HTTP","completed":false}'
        # base_url + relative path + encoded query.
        assert recorder.last_url == "http://tasks.invalid/tasks?completed=false"

        transport.request("POST", "/tasks", json_body={"title": "Write bytes"})
        # HTTPX serializes JSON compactly (no spaces), unlike Requests.
        assert recorder.last_body == b'{"title":"Write bytes"}'

    timeout_transport = HttpxTransport(
        build_client("http://tasks.invalid", httpx.MockTransport(_timeout_handler), 1.0)
    )
    try:
        timeout_transport.request("GET", "/tasks")
    except TransportTimeout:
        pass
    else:
        raise AssertionError("httpx.TimeoutException must map to TransportTimeout")
    finally:
        timeout_transport.close()

    network_transport = HttpxTransport(
        build_client("http://tasks.invalid", httpx.MockTransport(_network_handler), 1.0)
    )
    try:
        network_transport.request("GET", "/tasks")
    except ConnectionFailure:
        pass
    else:
        raise AssertionError("httpx.NetworkError must map to ConnectionFailure")
    finally:
        network_transport.close()

    # Every invalid timeout is rejected before a Client is ever built.
    for bad in (True, "2", float("nan"), float("inf"), 0, -1.0):
        try:
            build_client("http://tasks.invalid", httpx.MockTransport(recorder), bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"timeout {bad!r} must be rejected")

    print("GET url:", recorder.last_url)
    print("HTTPX default timeout is 5s of inactivity; here it is set explicitly")
    print("client ownership and exception classification verified")
