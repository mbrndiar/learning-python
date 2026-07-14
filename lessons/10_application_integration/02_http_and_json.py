"""
Lesson 10.2: HTTP and JSON Boundaries

This small local server demonstrates routing, status codes, JSON serialization
and a reusable client. Production services normally use a framework, but the
standard library exposes the underlying request/response concepts directly.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen


class MessageHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/message":
            self.send_error(404, "Route not found")
            return

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
            data = json.loads(response.read())
    except HTTPError as error:
        raise RuntimeError(f"HTTP request failed with status {error.code}") from error

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), MessageHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/message"
        print(fetch_json(url))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
