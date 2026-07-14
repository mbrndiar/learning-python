"""Dependency-free REST API for tasks persisted in SQLite."""

import argparse
import json
import sqlite3
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TypedDict, cast
from urllib.parse import urlsplit

MAX_BODY_SIZE = 1_000_000
DEFAULT_DATABASE_PATH = Path(__file__).with_name("tasks.db")


class TaskRecord(TypedDict):
    id: int
    title: str
    done: bool


class TaskStore:
    """Persist task records without depending on the HTTP layer."""

    def __init__(self, database_path: str | Path):
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

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _as_dict(row: sqlite3.Row | None) -> TaskRecord | None:
        if row is None:
            return None
        # SQLite represents booleans as integers; JSON clients should see a
        # real boolean so all storage backends expose the same task shape.
        return {
            "id": int(row["id"]),
            "title": str(row["title"]),
            "done": bool(row["done"]),
        }

    def list(self) -> list[TaskRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()
        return [task for row in rows if (task := self._as_dict(row)) is not None]

    def get(self, task_id: int) -> TaskRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._as_dict(row)

    def create(self, title: str) -> TaskRecord:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, 0)", (title,)
            )
            task_id = cursor.lastrowid
        if task_id is None:
            raise RuntimeError("SQLite did not return a task ID")
        task = self.get(task_id)
        if task is None:
            raise RuntimeError("Created task could not be read back")
        return task

    def complete(self, task_id: int) -> TaskRecord | None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET done = 1 WHERE id = ?", (task_id,)
            )
        return self.get(task_id) if cursor.rowcount else None

    def delete(self, task_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


class TasksServer(ThreadingHTTPServer):
    store: TaskStore


class TasksHandler(BaseHTTPRequestHandler):
    """Translate task HTTP requests into store operations."""

    server_version = "TasksAPI/1.0"

    @property
    def task_server(self) -> TasksServer:
        return cast(TasksServer, self.server)

    def _route(self) -> tuple[str | None, int | None]:
        parts = [part for part in urlsplit(self.path).path.split("/") if part]
        if parts == ["tasks"]:
            return "collection", None
        if len(parts) == 2 and parts[0] == "tasks":
            try:
                return "item", int(parts[1])
            except ValueError:
                pass
        return None, None

    def _send_json(self, status: int, data: object) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, object]:
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

    def do_GET(self) -> None:
        route, task_id = self._route()
        if route == "collection":
            self._send_json(200, self.task_server.store.list())
        elif route == "item":
            assert task_id is not None
            task = self.task_server.store.get(task_id)
            self._send_json(200, task) if task else self._not_found()
        else:
            self._send_json(404, {"error": "Route not found"})

    def do_POST(self) -> None:
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
        self._send_json(201, self.task_server.store.create(title.strip()))

    def do_PATCH(self) -> None:
        route, task_id = self._route()
        if route != "item":
            self._send_json(404, {"error": "Route not found"})
            return
        assert task_id is not None
        try:
            data = self._read_json()
            if data != {"done": True}:
                raise ValueError("Completion requires exactly {'done': true}")
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        task = self.task_server.store.complete(task_id)
        self._send_json(200, task) if task else self._not_found()

    def do_DELETE(self) -> None:
        route, task_id = self._route()
        if route != "item":
            self._send_json(404, {"error": "Route not found"})
            return
        assert task_id is not None
        if self.task_server.store.delete(task_id):
            self.send_response(204)
            self.end_headers()
        else:
            self._not_found()

    def _not_found(self) -> None:
        self._send_json(404, {"error": "Task not found"})

    def log_message(self, format: str, *args: object) -> None:
        """Keep educational command output focused on explicit messages."""


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> TasksServer:
    """Create a configurable server without starting its blocking loop."""

    server = TasksServer((host, port), TasksHandler)
    server.store = TaskStore(database_path)
    return server


def main(argv: Sequence[str] | None = None) -> None:
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
