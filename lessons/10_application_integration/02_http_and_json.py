"""
Lesson 10.2: HTTP and JSON Boundaries

This small local server demonstrates routing, status codes, JSON serialization
and a reusable client. Production services normally use a framework, but the
standard library exposes the underlying request/response concepts directly.
"""

import json
import threading
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class MessageHandler(BaseHTTPRequestHandler):
    # BaseHTTPRequestHandler dispatches GET requests to this specially named
    # method. Other HTTP methods would use their own do_* handlers.
    def do_GET(self) -> None:
        if self.path != "/message":
            self.send_error(404, "Route not found")
            return

        # HTTP bodies are bytes. Serialize Python values to JSON text, encode
        # that text, then report the byte length rather than character count.
        body = json.dumps({"message": "Hello over HTTP"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """Keep lesson output focused on explicit messages."""


def fetch_json(url: str) -> dict[str, object]:
    try:
        with urlopen(url, timeout=2) as response:
            # response.read() returns bytes; json.loads accepts UTF-8 JSON bytes
            # and produces ordinary Python values that still need validation.
            data = json.loads(response.read())
    except HTTPError as error:
        # HTTPError represents a completed HTTP response with a failure status.
        # Keep that separate from connection, timeout, and malformed-body errors.
        raise RuntimeError(f"HTTP request failed with status {error.code}") from error
    except (URLError, TimeoutError, HTTPException, ConnectionError) as error:
        reason = getattr(error, "reason", str(error))
        raise RuntimeError(
            f"HTTP request could not reach or finish reading the server: {reason}"
        ) from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("HTTP response did not contain valid JSON") from error

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


if __name__ == "__main__":
    # Port 0 asks the operating system for an available local test port.
    server = ThreadingHTTPServer(("127.0.0.1", 0), MessageHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/message"
        print(fetch_json(url))
    finally:
        # Stop accepting work, release the listening socket, then join the
        # thread so the process never leaves background work running.
        server.shutdown()
        server.server_close()
        thread.join()
