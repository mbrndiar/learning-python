"""
Chapter 16, Lesson 3: A Standard-Library HTTP Server Adapter

Purpose: adapt BaseHTTPRequestHandler attributes and binary streams to a pure
request/response function while keeping server startup explicit and optional.

Prerequisite: Lessons 1-2, Chapter 7 stream ownership, and Chapter 13 CLI flags.

Default run from the repository root (no socket is opened):

    python lessons/16_http_fundamentals_and_stdlib/03_stdlib_http_server.py

Optional loopback server (stop with Ctrl+C):

    python lessons/16_http_fundamentals_and_stdlib/03_stdlib_http_server.py --serve
"""

import argparse
import io
import json
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import Message
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer


@dataclass(frozen=True)
class HttpRequest:
    method: str
    target: str
    headers: Mapping[str, str]
    body: bytes = b""


@dataclass(frozen=True)
class HttpResponse:
    status: HTTPStatus
    headers: Mapping[str, str]
    body: bytes


def json_response(status: HTTPStatus, payload: object) -> HttpResponse:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return HttpResponse(
        status,
        {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body)),
        },
        body,
    )


# Step 1: protocol-independent behavior remains a normal function.
def dispatch_request(request: HttpRequest) -> HttpResponse:
    if request.target == "/health" and request.method == "GET":
        return json_response(HTTPStatus.OK, {"status": "ok"})
    if request.target == "/health":
        response = json_response(
            HTTPStatus.METHOD_NOT_ALLOWED,
            {"error": {"code": "method_not_allowed"}},
        )
        return HttpResponse(
            response.status,
            {**response.headers, "Allow": "GET"},
            response.body,
        )
    return json_response(
        HTTPStatus.NOT_FOUND,
        {"error": {"code": "not_found"}},
    )


class TaskRequestHandler(BaseHTTPRequestHandler):
    """Translate http.server state to and from the pure boundary."""

    # Step 2: BaseHTTPRequestHandler dispatches GET to this method. `path`
    # already includes the query component.
    def do_GET(self) -> None:
        request = HttpRequest(
            method=self.command,
            target=self.path,
            headers=dict(self.headers.items()),
        )
        self.send_http_response(dispatch_request(request))

    # Step 3: response headers are buffered until end_headers(), then the body
    # bytes are written to wfile.
    def send_http_response(self, response: HttpResponse) -> None:
        self.send_response(response.status)
        for name, value in response.headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(response.body)

    # Deterministic lessons and tests do not need timestamped stderr logs.
    def log_message(self, format: str, *args: object) -> None:
        del format, args


# Step 4: construct one handler without invoking its socket-reading __init__.
# This exercises the real send_response/send_header/end_headers machinery while
# keeping the default lesson run in memory and offline.
def run_handler_in_memory(method: str, target: str) -> bytes:
    handler = object.__new__(TaskRequestHandler)
    handler.command = method
    handler.path = target
    handler.request_version = "HTTP/1.1"
    handler.requestline = f"{method} {target} HTTP/1.1"
    handler.client_address = ("127.0.0.1", 12345)
    handler.headers = Message()
    handler.rfile = io.BytesIO()
    handler.wfile = io.BytesIO()
    handler.close_connection = True

    method_handler = getattr(handler, f"do_{method}", None)
    if method_handler is None:
        handler.send_error(HTTPStatus.NOT_IMPLEMENTED)
    else:
        method_handler()
    return handler.wfile.getvalue()


def serve_loopback() -> None:
    # The creator of HTTPServer owns serve_forever() and socket cleanup.
    address = ("127.0.0.1", 8000)
    with HTTPServer(address, TaskRequestHandler) as server:
        print("Serving http://127.0.0.1:8000; press Ctrl+C to stop")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Chapter 16 HTTP demo")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="start the optional loopback server",
    )
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    if arguments.serve:
        serve_loopback()
    else:
        raw_response = run_handler_in_memory("GET", "/health")
        headers, body = raw_response.split(b"\r\n\r\n", 1)
        assert headers.startswith(b"HTTP/1.0 200 OK\r\n")
        assert b"Content-Type: application/json; charset=utf-8\r\n" in headers
        assert b"Content-Length: 15" in headers
        assert json.loads(body) == {"status": "ok"}

        header_lines = headers.decode("iso-8859-1").splitlines()
        print(header_lines[0])
        print(next(line for line in header_lines if line.startswith("Content-Type:")))
        print(next(line for line in header_lines if line.startswith("Content-Length:")))
        print()
        print(body.decode("utf-8"))
