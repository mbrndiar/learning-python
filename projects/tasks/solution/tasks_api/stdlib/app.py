"""Implement the Task HTTP boundary directly on ``http.server``.

Unlike Flask and FastAPI, this adapter owns routing, message framing, JSON
decoding, error translation, and socket-server lifecycle explicitly.
"""

import json
import logging
from collections.abc import Mapping
from dataclasses import asdict
from email.message import Message
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import NoReturn
from urllib.parse import parse_qs, unquote, urlsplit

from tasks_core.domain import UNSET, Task
from tasks_core.errors import StorageError, TaskError, ValidationError
from tasks_core.service import TaskService

MAX_REQUEST_BODY = 64 * 1024
_LOGGER = logging.getLogger(__name__)
_METHODS_BY_ROUTE = {
    "health": ("GET",),
    "tasks": ("GET", "POST"),
    "task": ("GET", "PATCH", "DELETE"),
}


class _BoundaryError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        *,
        details: Mapping[str, object] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.status = status
        self.code = code
        self.message = message
        self.details = dict(details or {})
        self.headers = dict(headers or {})
        super().__init__(message)


class _InvalidJson(ValueError):
    pass


def _reject_duplicate_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise _InvalidJson(f"duplicate JSON property: {key}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> NoReturn:
    raise _InvalidJson(f"invalid JSON constant: {value}")


def _task_payload(task: Task) -> dict[str, object]:
    return asdict(task)


def _error_payload(
    code: str,
    message: str,
    details: Mapping[str, object] | None = None,
) -> dict[str, object]:
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error["details"] = dict(details)
    return {"error": error}


def _handler_for(service: TaskService) -> type[BaseHTTPRequestHandler]:
    # ``ThreadingHTTPServer`` constructs handlers itself, so a factory closure
    # injects the process-owned service without using globals or changing the
    # handler constructor expected by the standard library.
    class TaskRequestHandler(BaseHTTPRequestHandler):
        """Translate explicit HTTP requests into Task service operations."""

        def do_GET(self) -> None:
            self._dispatch()

        def do_POST(self) -> None:
            self._dispatch()

        def do_PATCH(self) -> None:
            self._dispatch()

        def do_DELETE(self) -> None:
            self._dispatch()

        def do_PUT(self) -> None:
            self._dispatch()

        def do_HEAD(self) -> None:
            self._dispatch()

        def do_OPTIONS(self) -> None:
            self._dispatch()

        def do_TRACE(self) -> None:
            self._dispatch()

        def do_CONNECT(self) -> None:
            self._dispatch()

        def __getattr__(self, name: str) -> object:
            # BaseHTTPRequestHandler normally emits an HTML 501 before route
            # dispatch for an unknown method name. Route every syntactically
            # valid method through the shared contract so known paths return the
            # required JSON 405 response and unknown paths still return JSON 404.
            if name.startswith("do_"):
                return self._dispatch
            raise AttributeError(name)

        def log_message(self, format: str, *args: object) -> None:
            _LOGGER.info("%s - %s", self.address_string(), format % args)

        def _dispatch(self) -> None:
            # Boundary and domain failures have stable public mappings. Unknown
            # failures are logged server-side but deliberately sanitized on the
            # wire so implementation details do not become part of the API.
            try:
                self._dispatch_request()
            except _BoundaryError as error:
                self._send_json(
                    error.status,
                    _error_payload(error.code, error.message, error.details),
                    error.headers,
                )
            except StorageError:
                _LOGGER.exception("Task storage failed while handling the request")
                self._send_internal_error()
            except TaskError as error:
                self._send_task_error(error)
            except Exception:
                _LOGGER.exception("Unexpected standard-library API failure")
                self._send_internal_error()

        def _dispatch_request(self) -> None:
            # BaseHTTPRequestHandler leaves the request target as text. Split it
            # before routing so path decoding and query parsing follow separate
            # URL rules rather than treating the whole target as a file path.
            try:
                target = urlsplit(self.path, allow_fragments=False)
                path = unquote(target.path, encoding="utf-8", errors="strict")
            except (UnicodeDecodeError, ValueError) as error:
                raise _BoundaryError(
                    HTTPStatus.NOT_FOUND,
                    "not_found",
                    "route was not found",
                ) from error

            route, task_id_text = self._match_route(path)
            if route is None:
                raise _BoundaryError(
                    HTTPStatus.NOT_FOUND,
                    "not_found",
                    "route was not found",
                )

            allowed_methods = _METHODS_BY_ROUTE[route]
            # The handler methods all converge here; the route table is the
            # single source for dispatch and the Allow response header.
            if self.command not in allowed_methods:
                raise _BoundaryError(
                    HTTPStatus.METHOD_NOT_ALLOWED,
                    "method_not_allowed",
                    "method is not allowed for this path",
                    headers={"Allow": ", ".join(allowed_methods)},
                )

            query = self._parse_query(target.query)
            if route != "tasks" or self.command != "GET":
                self._reject_query(query)

            if route == "health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if route == "tasks":
                self._dispatch_tasks(query)
                return

            if task_id_text is None:
                raise RuntimeError("task route did not include an ID")
            self._dispatch_task(task_id_text)

        @staticmethod
        def _match_route(path: str) -> tuple[str | None, str | None]:
            if path == "/health":
                return "health", None
            if path == "/tasks":
                return "tasks", None
            if path.startswith("/tasks/"):
                task_id = path.removeprefix("/tasks/")
                if task_id and "/" not in task_id:
                    return "task", task_id
            return None, None

        @staticmethod
        def _parse_query(query: str) -> dict[str, list[str]]:
            try:
                return parse_qs(
                    query,
                    keep_blank_values=True,
                    strict_parsing=True,
                )
            except ValueError as error:
                raise ValidationError(
                    "query string was malformed",
                    field="query",
                ) from error

        @staticmethod
        def _reject_query(query: Mapping[str, list[str]]) -> None:
            if query:
                field = next(iter(query))
                raise ValidationError(
                    f"unknown query parameter: {field}",
                    field=field,
                )

        def _dispatch_tasks(self, query: Mapping[str, list[str]]) -> None:
            if self.command == "POST":
                body = self._read_json_object()
                self._reject_unknown_properties(body, {"title"})
                if "title" not in body:
                    raise ValidationError(
                        "missing property: title",
                        field="title",
                    )
                task = service.create_task(body["title"])
                self._send_json(HTTPStatus.CREATED, _task_payload(task))
                return

            unknown_query = set(query) - {"completed"}
            if unknown_query:
                field = sorted(unknown_query)[0]
                raise ValidationError(
                    f"unknown query parameter: {field}",
                    field=field,
                )
            completed_values = query.get("completed")
            completed: bool | None = None
            if completed_values is not None:
                if len(completed_values) != 1 or completed_values[0] not in {
                    "true",
                    "false",
                }:
                    raise ValidationError(
                        "completed filter must be true or false",
                        field="completed",
                    )
                completed = completed_values[0] == "true"
            tasks = service.list_tasks(completed)
            self._send_json(
                HTTPStatus.OK,
                [_task_payload(task) for task in tasks],
            )

        def _dispatch_task(self, task_id_text: str) -> None:
            if not task_id_text.isascii() or not task_id_text.isdecimal():
                raise ValidationError(
                    "task ID must be a positive integer",
                    field="id",
                )
            task_id = int(task_id_text, 10)

            if self.command == "GET":
                self._send_json(
                    HTTPStatus.OK,
                    _task_payload(service.get_task(task_id)),
                )
                return
            if self.command == "DELETE":
                service.delete_task(task_id)
                self._send_empty(HTTPStatus.NO_CONTENT)
                return

            body = self._read_json_object()
            self._reject_unknown_properties(body, {"title", "completed"})
            title: object = body["title"] if "title" in body else UNSET
            completed: object = body["completed"] if "completed" in body else UNSET
            task = service.update_task(
                task_id,
                title=title,
                completed=completed,
            )
            self._send_json(HTTPStatus.OK, _task_payload(task))

        @staticmethod
        def _reject_unknown_properties(
            body: Mapping[str, object],
            allowed: set[str],
        ) -> None:
            unknown = set(body) - allowed
            if unknown:
                field = sorted(unknown)[0]
                raise ValidationError(
                    f"unknown property: {field}",
                    field=field,
                )

        def _read_json_object(self) -> dict[str, object]:
            value = self._read_json()
            if not isinstance(value, dict):
                raise ValidationError(
                    "request body must be a JSON object",
                    field="body",
                )
            return value

        def _read_json(self) -> object:
            self._validate_content_type()
            # This handler does not decode transfer codings, so it requires one
            # unambiguous Content-Length before reading the body. Closing on
            # framing failures also protects request boundaries if HTTP/1.1
            # persistence is enabled later.
            if self.headers.get("Transfer-Encoding") is not None:
                self.close_connection = True
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request body must use Content-Length",
                )

            lengths = self.headers.get_all("Content-Length") or []
            if len(lengths) != 1:
                self.close_connection = True
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request body must include one Content-Length",
                )
            try:
                content_length = int(lengths[0], 10)
            except ValueError as error:
                self.close_connection = True
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request Content-Length was invalid",
                ) from error
            if content_length < 0:
                self.close_connection = True
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request Content-Length was invalid",
                )
            if content_length > MAX_REQUEST_BODY:
                self.close_connection = True
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request body is too large",
                )

            # Trust the validated length only up to the configured bound. Closing
            # after framing failures avoids reusing a connection whose unread
            # request bytes are no longer safely delimited.
            body = self.rfile.read(content_length)
            if len(body) != content_length:
                self.close_connection = True
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request body was incomplete",
                )
            try:
                # Decode bytes strictly at the HTTP boundary. The JSON hooks also
                # reject duplicate object names and non-standard NaN/Infinity
                # constants that Python's decoder otherwise accepts.
                text = body.decode("utf-8")
                return json.loads(
                    text,
                    object_pairs_hook=_reject_duplicate_fields,
                    parse_constant=_reject_json_constant,
                )
            except (UnicodeDecodeError, json.JSONDecodeError, _InvalidJson) as error:
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request body must be valid JSON",
                ) from error

        def _validate_content_type(self) -> None:
            values = self.headers.get_all("Content-Type") or []
            if len(values) != 1:
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request Content-Type must be application/json",
                )
            message = Message()
            message["content-type"] = values[0]
            if message.get_content_type().casefold() != "application/json":
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request Content-Type must be application/json",
                )
            charset = message.get_content_charset()
            if charset is not None and charset.casefold() != "utf-8":
                raise _BoundaryError(
                    HTTPStatus.BAD_REQUEST,
                    "invalid_json",
                    "request JSON charset must be UTF-8",
                )

        def _send_task_error(self, error: TaskError) -> None:
            if error.code == "validation_error":
                self._send_json(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    _error_payload(error.code, error.message, error.details),
                )
                return
            if error.code == "not_found":
                self._send_json(
                    HTTPStatus.NOT_FOUND,
                    _error_payload(error.code, error.message, error.details),
                )
                return
            _LOGGER.exception("Unexpected Task error crossed the service boundary")
            self._send_internal_error()

        def _send_internal_error(self) -> None:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                _error_payload(
                    "internal_error",
                    "the server could not complete the request",
                ),
            )

        def _send_json(
            self,
            status: int,
            payload: object,
            headers: Mapping[str, str] | None = None,
        ) -> None:
            body = json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            for name, value in (headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            # For a HEAD request reaching this helper, preserve the computed
            # headers but suppress body bytes. The route table currently rejects
            # HEAD itself with 405.
            if self.command != "HEAD":
                self.wfile.write(body)

        def _send_empty(self, status: int) -> None:
            self.send_response(status)
            self.send_header("Content-Length", "0")
            self.end_headers()

    return TaskRequestHandler


def create_server(
    service: TaskService,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    """Create a configured standard-library HTTP server without running it."""

    server = ThreadingHTTPServer((host, port), _handler_for(service))
    # Request threads must not keep the learning server process alive after the
    # main serve loop has been stopped; in-flight work is not given a shutdown
    # completion guarantee by this local adapter.
    server.daemon_threads = True
    return server


def serve(service: TaskService, host: str, port: int) -> None:
    """Run the blocking serve loop and always release its listening socket."""

    server = create_server(service, host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _LOGGER.info("Standard-library Task API interrupted")
    finally:
        server.server_close()


__all__ = ["create_server", "serve"]
