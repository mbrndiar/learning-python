"""Dependency-free REST API for tasks persisted in SQLite."""

import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

MAX_BODY_SIZE = 1_000_000
DEFAULT_DATABASE_PATH = Path(__file__).with_name("tasks.db")


class TaskStore:
    """Persist task records without depending on the HTTP layer."""

    def __init__(self, database_path):
        self.database_path = database_path
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _as_dict(row):
        if row is None:
            return None
        task = dict(row)
        # SQLite represents booleans as integers; JSON clients should see a
        # real boolean so all storage backends expose the same task shape.
        task["done"] = bool(task["done"])
        return task

    def list(self):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()
        return [self._as_dict(row) for row in rows]

    def get(self, task_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._as_dict(row)

    def create(self, title):
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, 0)", (title,)
            )
            task_id = cursor.lastrowid
        return self.get(task_id)

    def complete(self, task_id):
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET done = 1 WHERE id = ?", (task_id,)
            )
        return self.get(task_id) if cursor.rowcount else None

    def delete(self, task_id):
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


class TasksHandler(BaseHTTPRequestHandler):
    """Translate task HTTP requests into store operations."""

    server_version = "TasksAPI/1.0"

    def _route(self):
        parts = [part for part in urlsplit(self.path).path.split("/") if part]
        if parts == ["tasks"]:
            return "collection", None
        if len(parts) == 2 and parts[0] == "tasks":
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
        except ValueError as error:
            raise ValueError("Content-Length must be a number") from error
        if length <= 0:
            raise ValueError("Request body must contain JSON")
        if length > MAX_BODY_SIZE:
            raise ValueError("Request body is too large")
        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("Request body must be valid JSON") from error
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        return data

    def do_GET(self):
        route, task_id = self._route()
        if route == "collection":
            self._send_json(200, self.server.store.list())
        elif route == "item":
            task = self.server.store.get(task_id)
            self._send_json(200, task) if task else self._not_found()
        else:
            self._send_json(404, {"error": "Route not found"})

    def do_POST(self):
        route, _ = self._route()
        if route != "collection":
            self._send_json(404, {"error": "Route not found"})
            return
        try:
            data = self._read_json()
            title = data.get("title")
            if not isinstance(title, str) or not title.strip():
                raise ValueError("'title' must be a non-empty string")
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(201, self.server.store.create(title.strip()))

    def do_PATCH(self):
        route, task_id = self._route()
        if route != "item":
            self._send_json(404, {"error": "Route not found"})
            return
        try:
            data = self._read_json()
            if data != {"done": True}:
                raise ValueError("Completion requires exactly {'done': true}")
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        task = self.server.store.complete(task_id)
        self._send_json(200, task) if task else self._not_found()

    def do_DELETE(self):
        route, task_id = self._route()
        if route != "item":
            self._send_json(404, {"error": "Route not found"})
        elif self.server.store.delete(task_id):
            self.send_response(204)
            self.end_headers()
        else:
            self._not_found()

    def _not_found(self):
        self._send_json(404, {"error": "Task not found"})

    def log_message(self, format, *args):
        """Keep educational command output focused on explicit messages."""


def create_server(host="127.0.0.1", port=8000, database_path=DEFAULT_DATABASE_PATH):
    """Create a configurable server without starting its blocking loop."""

    server = ThreadingHTTPServer((host, port), TasksHandler)
    server.store = TaskStore(database_path)
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the tasks REST API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    args = parser.parse_args(argv)

    server = create_server(args.host, args.port, args.database)
    print(f"Tasks API listening on http://{args.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
