"""A small, dependency-free REST API for an in-memory notes collection."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

MAX_BODY_SIZE = 1_000_000


class NoteStore:
    def __init__(self):
        self.notes = {}
        self.next_id = 1

    def list(self):
        return list(self.notes.values())

    def get(self, note_id):
        return self.notes.get(note_id)

    def create(self, title, body):
        note = {"id": self.next_id, "title": title, "body": body}
        self.notes[note["id"]] = note
        self.next_id += 1
        return note

    def update(self, note_id, title, body):
        note = self.get(note_id)
        if note is None:
            return None
        note.update(title=title, body=body)
        return note

    def delete(self, note_id):
        return self.notes.pop(note_id, None) is not None


class NotesHandler(BaseHTTPRequestHandler):
    server_version = "NotesAPI/1.0"

    def _route(self):
        parts = [part for part in urlsplit(self.path).path.split("/") if part]
        if parts == ["notes"]:
            return "collection", None
        if len(parts) == 2 and parts[0] == "notes":
            try:
                return "item", int(parts[1])
            except ValueError:
                pass
        return None, None

    def _send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Content-Length must be a number")
        if length <= 0:
            raise ValueError("Request body must contain JSON")
        if length > MAX_BODY_SIZE:
            raise ValueError("Request body is too large")

        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Request body must be valid JSON")
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        return data

    def _note_fields(self):
        data = self._read_json()
        title = data.get("title")
        body = data.get("body", "")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("'title' must be a non-empty string")
        if not isinstance(body, str):
            raise ValueError("'body' must be a string")
        return title.strip(), body

    def do_GET(self):
        route, note_id = self._route()
        if route == "collection":
            self._send_json(200, self.server.store.list())
        elif route == "item":
            note = self.server.store.get(note_id)
            if note is None:
                self._send_json(404, {"error": "Note not found"})
            else:
                self._send_json(200, note)
        else:
            self._send_json(404, {"error": "Route not found"})

    def do_POST(self):
        route, _ = self._route()
        if route != "collection":
            self._send_json(404, {"error": "Route not found"})
            return
        try:
            title, body = self._note_fields()
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(201, self.server.store.create(title, body))

    def do_PUT(self):
        route, note_id = self._route()
        if route != "item":
            self._send_json(404, {"error": "Route not found"})
            return
        try:
            title, body = self._note_fields()
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        note = self.server.store.update(note_id, title, body)
        if note is None:
            self._send_json(404, {"error": "Note not found"})
        else:
            self._send_json(200, note)

    def do_DELETE(self):
        route, note_id = self._route()
        if route != "item":
            self._send_json(404, {"error": "Route not found"})
        elif self.server.store.delete(note_id):
            self.send_response(204)
            self.end_headers()
        else:
            self._send_json(404, {"error": "Note not found"})

    def log_message(self, format, *args):
        return


def create_server(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), NotesHandler)
    server.store = NoteStore()
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the notes REST API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    server = create_server(args.host, args.port)
    print(f"Notes API listening on http://{args.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
