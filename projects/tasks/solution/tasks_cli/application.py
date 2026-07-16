"""Shared command parsing and execution policy for all Task clients."""

import argparse
import json
import math
import sys
from collections.abc import Mapping, Sequence
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import NoReturn, TextIO, TypeAlias
from unicodedata import category

from tasks_core.errors import IncompleteImplementationError

from .transport import (
    JsonValue,
    TaskTransport,
    TransportConnectionError,
    TransportError,
    TransportFactory,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
    normalize_base_url,
)

EXIT_SUCCESS = 0
EXIT_USAGE = 2
EXIT_API = 3
EXIT_MALFORMED_RESPONSE = 4
EXIT_TRANSPORT = 5

_ERROR_CODE_BY_STATUS = {
    400: "invalid_json",
    404: "not_found",
    405: "method_not_allowed",
    422: "validation_error",
    500: "internal_error",
}


@dataclass(frozen=True, slots=True)
class ClientSettings:
    """Connection settings shared by every client transport."""

    base_url: str
    timeout: float


@dataclass(frozen=True, slots=True)
class AddCommand:
    """Create one task from a title."""

    title: str


@dataclass(frozen=True, slots=True)
class ListCommand:
    """List tasks with an optional completion filter."""

    completed: bool | None = None


@dataclass(frozen=True, slots=True)
class ShowCommand:
    """Fetch one task by ID."""

    task_id: int


@dataclass(frozen=True, slots=True)
class UpdateCommand:
    """Update one or both mutable task fields."""

    task_id: int
    title: str | None
    completed: bool | None


@dataclass(frozen=True, slots=True)
class CompleteCommand:
    """Mark one task complete."""

    task_id: int


@dataclass(frozen=True, slots=True)
class RemoveCommand:
    """Delete one task."""

    task_id: int


ClientCommand: TypeAlias = (
    AddCommand
    | ListCommand
    | ShowCommand
    | UpdateCommand
    | CompleteCommand
    | RemoveCommand
)


@dataclass(frozen=True, slots=True)
class ClientRequest:
    """One parsed CLI invocation before transport-specific execution."""

    settings: ClientSettings
    command: ClientCommand


@dataclass(frozen=True, slots=True)
class ClientResult:
    """Rendered process result returned by command execution."""

    exit_code: int
    stdout: str | None = None
    stderr: str | None = None


@dataclass(frozen=True, slots=True)
class _TaskPayload:
    task_id: int
    title: str
    completed: bool

    def as_json(self) -> dict[str, JsonValue]:
        return {
            "id": self.task_id,
            "title": self.title,
            "completed": self.completed,
        }


class _ApiFailure(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        self.status = status
        self.code = code
        self.message = message
        super().__init__(message)


class _MalformedResponse(Exception):
    pass


class _InvalidJsonValue(ValueError):
    pass


class _Arguments(argparse.Namespace):
    base_url: str
    timeout: float
    command: str
    title: str | None
    completed: str | None
    id: int | None


def _positive_id(value: str) -> int:
    try:
        task_id = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ID must be a positive integer") from error
    if task_id <= 0:
        raise argparse.ArgumentTypeError("ID must be a positive integer")
    return task_id


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "timeout must be positive and finite"
        ) from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be positive and finite")
    return timeout


def _base_url(value: str) -> str:
    try:
        return normalize_base_url(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _completion_value(value: str | None) -> bool | None:
    if value is None:
        return None
    return value == "true"


def build_parser(prog: str = "tasks-cli") -> argparse.ArgumentParser:
    """Build the common parser for every documented client command."""

    parser = argparse.ArgumentParser(
        prog=prog,
        description="Call the Task REST API",
        allow_abbrev=False,
    )
    parser.set_defaults(title=None, completed=None, id=None)
    parser.add_argument(
        "--base-url",
        type=_base_url,
        default="http://127.0.0.1:8000",
    )
    parser.add_argument("--timeout", type=_positive_timeout, default=5.0)
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", allow_abbrev=False)
    add_parser.add_argument("title", metavar="TITLE")

    list_parser = commands.add_parser("list", allow_abbrev=False)
    list_parser.add_argument("--completed", choices=("true", "false"))

    show_parser = commands.add_parser("show", allow_abbrev=False)
    show_parser.add_argument("id", type=_positive_id, metavar="ID")

    update_parser = commands.add_parser("update", allow_abbrev=False)
    update_parser.add_argument("id", type=_positive_id, metavar="ID")
    update_parser.add_argument("--title")
    update_parser.add_argument("--completed", choices=("true", "false"))

    complete_parser = commands.add_parser("complete", allow_abbrev=False)
    complete_parser.add_argument("id", type=_positive_id, metavar="ID")

    remove_parser = commands.add_parser("remove", allow_abbrev=False)
    remove_parser.add_argument("id", type=_positive_id, metavar="ID")
    return parser


def parse_request(
    argv: Sequence[str] | None = None,
    *,
    prog: str = "tasks-cli",
) -> ClientRequest:
    """Parse and normalize one documented client invocation."""

    parser = build_parser(prog)
    arguments = _Arguments()
    parser.parse_args(argv, namespace=arguments)

    settings = ClientSettings(
        base_url=arguments.base_url,
        timeout=arguments.timeout,
    )
    if arguments.command == "add":
        if arguments.title is None:
            parser.error("add requires TITLE")
        command: ClientCommand = AddCommand(arguments.title)
    elif arguments.command == "list":
        command = ListCommand(_completion_value(arguments.completed))
    elif arguments.command == "show":
        if arguments.id is None:
            parser.error("show requires ID")
        command = ShowCommand(arguments.id)
    elif arguments.command == "update":
        if arguments.id is None:
            parser.error("update requires ID")
        completed = _completion_value(arguments.completed)
        if arguments.title is None and completed is None:
            parser.error("update requires --title, --completed, or both")
        command = UpdateCommand(arguments.id, arguments.title, completed)
    elif arguments.command == "complete":
        if arguments.id is None:
            parser.error("complete requires ID")
        command = CompleteCommand(arguments.id)
    elif arguments.command == "remove":
        if arguments.id is None:
            parser.error("remove requires ID")
        command = RemoveCommand(arguments.id)
    else:
        parser.error(f"unsupported command: {arguments.command}")

    return ClientRequest(settings=settings, command=command)


def _request_for(command: ClientCommand) -> TransportRequest:
    if isinstance(command, AddCommand):
        return TransportRequest("POST", "/tasks", json_body={"title": command.title})
    if isinstance(command, ListCommand):
        query = (
            {}
            if command.completed is None
            else {"completed": "true" if command.completed else "false"}
        )
        return TransportRequest("GET", "/tasks", query=query)
    if isinstance(command, ShowCommand):
        return TransportRequest("GET", f"/tasks/{command.task_id}")
    if isinstance(command, UpdateCommand):
        body: dict[str, JsonValue] = {}
        if command.title is not None:
            body["title"] = command.title
        if command.completed is not None:
            body["completed"] = command.completed
        return TransportRequest(
            "PATCH",
            f"/tasks/{command.task_id}",
            json_body=body,
        )
    if isinstance(command, CompleteCommand):
        return TransportRequest(
            "PATCH",
            f"/tasks/{command.task_id}",
            json_body={"completed": True},
        )
    return TransportRequest("DELETE", f"/tasks/{command.task_id}")


def _content_type(headers: Mapping[str, str]) -> str:
    values = [
        value
        for name, value in headers.items()
        if isinstance(name, str) and name.casefold() == "content-type"
    ]
    if len(values) != 1 or not isinstance(values[0], str):
        raise _MalformedResponse(
            "response Content-Type was not application/json"
        )
    return values[0].split(";", 1)[0].strip().casefold()


def _reject_duplicate_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _InvalidJsonValue(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise _InvalidJsonValue(f"invalid JSON constant: {value}")


def _decode_json(response: TransportResponse) -> object:
    if _content_type(response.headers) != "application/json":
        raise _MalformedResponse(
            "response Content-Type was not application/json"
        )
    try:
        text = response.body.decode("utf-8")
        value: object = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_fields,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, _InvalidJsonValue) as error:
        raise _MalformedResponse("response body was not strict UTF-8 JSON") from error
    return value


def _validate_response(response: TransportResponse) -> None:
    if (
        not isinstance(response.status, int)
        or isinstance(response.status, bool)
        or not 100 <= response.status <= 599
    ):
        raise _MalformedResponse("response status was invalid")
    if not isinstance(response.body, bytes):
        raise _MalformedResponse("response body was not bytes")
    if not isinstance(response.headers, Mapping):
        raise _MalformedResponse("response headers were invalid")


def _decode_error(response: TransportResponse) -> _ApiFailure:
    value = _decode_json(response)
    if not isinstance(value, dict) or set(value) != {"error"}:
        raise _MalformedResponse("API error envelope fields were malformed")
    error_value: object = value["error"]
    if not isinstance(error_value, dict):
        raise _MalformedResponse("API error value was not an object")
    if not {"code", "message"} <= set(error_value) <= {
        "code",
        "message",
        "details",
    }:
        raise _MalformedResponse("API error fields were malformed")

    code: object = error_value["code"]
    message: object = error_value["message"]
    if (
        not isinstance(code, str)
        or not isinstance(message, str)
        or not message
        or (
            "details" in error_value
            and not isinstance(error_value["details"], dict)
        )
    ):
        raise _MalformedResponse("API error values were malformed")

    expected_code = _ERROR_CODE_BY_STATUS.get(response.status)
    if expected_code is None:
        raise _MalformedResponse(f"unexpected HTTP status: {response.status}")
    if code != expected_code:
        raise _MalformedResponse(
            f"API error code {code!r} did not match HTTP status {response.status}"
        )
    return _ApiFailure(response.status, code, message)


def _expect_status(
    response: TransportResponse,
    expected_status: int,
    allowed_error_statuses: frozenset[int],
) -> None:
    _validate_response(response)
    if response.status == expected_status:
        return
    if response.status in allowed_error_statuses:
        raise _decode_error(response)
    raise _MalformedResponse(f"unexpected HTTP status: {response.status}")


def _decode_task(value: object) -> _TaskPayload:
    if not isinstance(value, dict) or set(value) != {
        "id",
        "title",
        "completed",
    }:
        raise _MalformedResponse("Task response fields were malformed")

    task_id: object = value["id"]
    title: object = value["title"]
    completed: object = value["completed"]
    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
        or not isinstance(title, str)
        or not 1 <= len(title) <= 120
        or title.strip() != title
        or len(title.splitlines()) != 1
        or any(category(character) == "Cc" for character in title)
        or not isinstance(completed, bool)
    ):
        raise _MalformedResponse("Task response values were malformed")
    return _TaskPayload(task_id, title, completed)


def _decode_task_response(
    response: TransportResponse,
    expected_status: int,
    allowed_error_statuses: frozenset[int],
) -> _TaskPayload:
    _expect_status(response, expected_status, allowed_error_statuses)
    return _decode_task(_decode_json(response))


def _decode_list_response(
    response: TransportResponse,
    allowed_error_statuses: frozenset[int],
) -> list[_TaskPayload]:
    _expect_status(response, 200, allowed_error_statuses)
    value = _decode_json(response)
    if not isinstance(value, list):
        raise _MalformedResponse("Task list response was not an array")

    tasks = [_decode_task(item) for item in value]
    if any(
        current.task_id >= following.task_id
        for current, following in zip(tasks, tasks[1:], strict=False)
    ):
        raise _MalformedResponse("Task list was not ordered by ascending ID")
    return tasks


def _success_value(
    command: ClientCommand,
    response: TransportResponse,
) -> JsonValue:
    if isinstance(command, AddCommand):
        return _decode_task_response(
            response,
            201,
            frozenset({400, 405, 422, 500}),
        ).as_json()
    if isinstance(command, ListCommand):
        return [
            task.as_json()
            for task in _decode_list_response(
                response,
                frozenset({405, 422, 500}),
            )
        ]
    if isinstance(command, ShowCommand):
        return _decode_task_response(
            response,
            200,
            frozenset({404, 405, 422, 500}),
        ).as_json()
    if isinstance(command, (UpdateCommand, CompleteCommand)):
        return _decode_task_response(
            response,
            200,
            frozenset({400, 404, 405, 422, 500}),
        ).as_json()

    _expect_status(response, 204, frozenset({404, 405, 422, 500}))
    if response.body:
        raise _MalformedResponse("204 response body was not empty")
    return {"deleted": command.task_id}


def _render(value: JsonValue) -> str:
    return json.dumps(value, ensure_ascii=False)


def _execute(request: ClientRequest, transport: TaskTransport) -> ClientResult:
    raw_response: object = transport.send(_request_for(request.command))
    if not isinstance(raw_response, TransportResponse):
        raise _MalformedResponse("transport response was invalid")
    return ClientResult(
        EXIT_SUCCESS,
        stdout=_render(_success_value(request.command, raw_response)),
    )


def _transport_result(error: BaseException) -> ClientResult:
    if isinstance(error, TransportTimeoutError):
        message = error.message.strip() or "request timed out"
        return ClientResult(
            EXIT_TRANSPORT,
            stderr=f"connection: timeout: {message}",
        )
    if isinstance(error, TransportConnectionError):
        message = error.message.strip() or "request failed"
        return ClientResult(EXIT_TRANSPORT, stderr=f"connection: {message}")
    if isinstance(error, TransportError):
        message = error.message.strip() or "request failed"
        return ClientResult(EXIT_TRANSPORT, stderr=f"transport: {message}")
    return ClientResult(EXIT_TRANSPORT, stderr="transport: request failed")


def _execute_with_factory(
    request: ClientRequest,
    transport_factory: TransportFactory,
) -> ClientResult:
    try:
        transport = transport_factory(
            request.settings.base_url,
            request.settings.timeout,
        )
    except IncompleteImplementationError:
        raise
    except Exception as error:
        return _transport_result(error)

    try:
        try:
            result = _execute(request, transport)
        except IncompleteImplementationError:
            raise
        except _ApiFailure as error:
            result = ClientResult(
                EXIT_API,
                stderr=(
                    f"api: {error.status} {error.code}: {error.message}"
                ),
            )
        except _MalformedResponse as error:
            result = ClientResult(
                EXIT_MALFORMED_RESPONSE,
                stderr=f"malformed-response: {error}",
            )
        except Exception as error:
            result = _transport_result(error)
    finally:
        try:
            transport.close()
        except IncompleteImplementationError:
            raise
        except Exception as error:
            if "result" not in locals() or result.exit_code == EXIT_SUCCESS:
                result = _transport_result(error)
    return result


def _usage_message(parser_stderr: str) -> str:
    line = parser_stderr.strip().splitlines()[-1]
    marker = ": error: "
    if marker in line:
        return line.split(marker, 1)[1]
    return line


def run(
    argv: Sequence[str] | None,
    transport_factory: TransportFactory,
    stdout: TextIO,
    stderr: TextIO,
    *,
    prog: str = "tasks-cli",
) -> int:
    """Parse, execute, and render one client invocation through injected I/O."""

    parser_stdout = StringIO()
    parser_stderr = StringIO()
    try:
        with redirect_stdout(parser_stdout), redirect_stderr(parser_stderr):
            request = parse_request(argv, prog=prog)
    except SystemExit as error:
        exit_code = error.code if isinstance(error.code, int) else EXIT_USAGE
        if exit_code == EXIT_SUCCESS:
            stdout.write(parser_stdout.getvalue())
            return EXIT_SUCCESS
        stderr.write(f"usage: {_usage_message(parser_stderr.getvalue())}\n")
        return EXIT_USAGE

    result = _execute_with_factory(request, transport_factory)
    if result.stdout is not None:
        stdout.write(f"{result.stdout}\n")
    if result.stderr is not None:
        stderr.write(f"{result.stderr}\n")
    return result.exit_code


def main(
    argv: Sequence[str] | None = None,
    *,
    transport_factory: TransportFactory,
    prog: str = "tasks-cli",
) -> int:
    """Compose the shared application with process arguments and streams."""

    return run(
        argv,
        transport_factory,
        sys.stdout,
        sys.stderr,
        prog=prog,
    )


__all__ = [
    "AddCommand",
    "ClientCommand",
    "ClientRequest",
    "ClientResult",
    "ClientSettings",
    "CompleteCommand",
    "ListCommand",
    "RemoveCommand",
    "ShowCommand",
    "UpdateCommand",
    "build_parser",
    "main",
    "parse_request",
    "run",
]
