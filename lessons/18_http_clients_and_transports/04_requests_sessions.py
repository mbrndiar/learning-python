"""
Chapter 18, Lesson 4: Requests Sessions

Purpose: use a `requests.Session` idiomatically. A Session is an owned resource:
it holds a connection pool and must be closed. Requests builds the query and
JSON body for you (`params=`, `json=`), exposes the raw response bytes as
`.content`, and requires an *explicit* finite timeout because it has no default.

Prerequisite: Lessons 1-3. This lesson keeps the same `TransportResponse` shape
so a Requests response and a urllib response become interchangeable data.

Offline strategy: a real `requests.Session` prepares each request (so `params`
and `json` are genuinely encoded), but a mounted adapter returns canned bytes
instead of touching the network. No socket is opened.

Run from the repository root:

    python lessons/18_http_clients_and_transports/04_requests_sessions.py
"""

import math
from collections.abc import Mapping

import requests
from requests.adapters import BaseAdapter
from requests.models import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict

JsonScalar = str | int | float | bool | None


class TransportTimeout(Exception):
    """The explicit finite timeout expired."""


class ConnectionFailure(Exception):
    """The request could not reach the server or complete its transfer."""


class TransportError(Exception):
    """Any other Requests-level failure that is not a status code."""


# Step 1: the Session is the unit of ownership. Create one, reuse it for many
# requests, and close it. `trust_env = False` keeps the demo hermetic by
# ignoring ambient proxy environment variables.
def _validated_timeout(timeout: object) -> float:
    # A real, finite, positive number is required. bool is an int subclass, so
    # it is rejected before the numeric checks; NaN and infinity are not finite.
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a real number")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    return float(timeout)


class RequestsTransport:
    def __init__(
        self, base_url: str, session: requests.Session, timeout: object
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._session.trust_env = False
        self._timeout = _validated_timeout(timeout)
        self._closed = False

    # Step 2: let Requests encode the URL query (params) and the JSON body
    # (json). Read the raw bytes from response.content, and copy them so the
    # returned value does not keep the live Response alive. Do NOT call
    # raise_for_status(): a 4xx/5xx is an ordinary transport response here, to be
    # validated later by status-first logic.
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, JsonScalar] | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        if self._closed:
            raise TransportError("transport is closed")
        url = f"{self._base_url}{path}"
        try:
            response = self._session.request(
                method,
                url,
                params=dict(params) if params else None,
                json=dict(json_body) if json_body is not None else None,
                timeout=self._timeout,
                allow_redirects=False,
            )
            try:
                return (
                    response.status_code,
                    dict(response.headers),
                    bytes(response.content),
                )
            finally:
                response.close()
        # Step 3: classify failures from most specific to least specific.
        # Timeout and ConnectionError are both subclasses of RequestException,
        # so the specific clauses must come before the general one.
        except requests.Timeout as error:
            raise TransportTimeout("request timed out") from error
        except requests.ConnectionError as error:
            raise ConnectionFailure("request failed") from error
        except requests.RequestException as error:
            raise TransportError("request could not be sent") from error

    # Step 4: cleanup. Support both explicit close() and the context-manager
    # protocol so callers can pick whichever ownership style is clearer.
    def close(self) -> None:
        if not self._closed:
            self._session.close()
            self._closed = True

    def __enter__(self) -> "RequestsTransport":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


# --- Offline adapter -----------------------------------------------------------
# Mounted on the Session so real request preparation happens, but send() returns
# canned data or raises a scripted Requests exception.


class CannedAdapter(BaseAdapter):
    def __init__(self, outcome: str = "ok") -> None:
        super().__init__()
        self._outcome = outcome
        self.last_url: str | None = None
        self.last_body: bytes | None = None
        self.last_timeout: object = None

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
        self.last_url = request.url
        request_body = request.body
        if isinstance(request_body, bytes):
            self.last_body = request_body
        elif isinstance(request_body, str):
            self.last_body = request_body.encode()
        else:
            self.last_body = None
        self.last_timeout = timeout
        if self._outcome == "timeout":
            raise requests.Timeout("slow")
        if self._outcome == "connection":
            raise requests.ConnectionError("down")
        response = Response()
        response.status_code = 200
        response.headers = CaseInsensitiveDict(
            {"Content-Type": "application/json; charset=utf-8"}
        )
        response._content = b'{"id":1,"title":"Read HTTP","completed":false}'
        response.url = request.url or ""
        response.request = request
        return response

    def close(self) -> None:
        pass


def _session_with(adapter: BaseAdapter) -> requests.Session:
    session = requests.Session()
    session.mount("http://", adapter)
    return session


if __name__ == "__main__":
    adapter = CannedAdapter()
    with RequestsTransport(
        "http://tasks.invalid", _session_with(adapter), timeout=2.5
    ) as transport:
        status, headers, body = transport.request(
            "GET", "/tasks", params={"completed": "false"}
        )
        assert status == 200
        assert body == b'{"id":1,"title":"Read HTTP","completed":false}'
        # Requests encoded the query into the URL for us.
        assert adapter.last_url == "http://tasks.invalid/tasks?completed=false"
        assert adapter.last_timeout == 2.5

        # Requests serialized the JSON body from a mapping.
        transport.request("POST", "/tasks", json_body={"title": "Write bytes"})
        assert adapter.last_body == b'{"title": "Write bytes"}'

    timeout_transport = RequestsTransport(
        "http://tasks.invalid", _session_with(CannedAdapter("timeout")), timeout=1.0
    )
    try:
        timeout_transport.request("GET", "/tasks")
    except TransportTimeout:
        pass
    else:
        raise AssertionError("requests.Timeout must map to TransportTimeout")
    finally:
        timeout_transport.close()

    conn_transport = RequestsTransport(
        "http://tasks.invalid", _session_with(CannedAdapter("connection")), timeout=1.0
    )
    try:
        conn_transport.request("GET", "/tasks")
    except ConnectionFailure:
        pass
    else:
        raise AssertionError("requests.ConnectionError must map to ConnectionFailure")
    finally:
        conn_transport.close()

    # Every invalid timeout is rejected at construction, before any Session use.
    for bad in (True, "2", float("nan"), float("inf"), 0, -1.0):
        try:
            RequestsTransport("http://tasks.invalid", requests.Session(), timeout=bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"timeout {bad!r} must be rejected")

    print("GET url:", adapter.last_url)
    print("timeout passed to Requests:", adapter.last_timeout)
    print("session ownership and exception classification verified")
