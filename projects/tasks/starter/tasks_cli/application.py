"""Shared command parsing and execution policy for all Task clients."""

import argparse
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TextIO, TypeAlias

from tasks_core.errors import incomplete

from .transport import TransportFactory, normalize_base_url


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


def run(
    argv: Sequence[str] | None,
    transport_factory: TransportFactory,
    stdout: TextIO,
    stderr: TextIO,
    *,
    prog: str = "tasks-cli",
) -> int:
    """Implement shared request construction, validation, and rendering."""

    request = parse_request(argv, prog=prog)
    del transport_factory, stdout, stderr
    incomplete(f"client command execution for {request.command!r}")


def main(
    argv: Sequence[str] | None = None,
    *,
    transport_factory: TransportFactory,
    prog: str = "tasks-cli",
) -> int:
    """Compose the guided starter with process arguments and streams."""

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
