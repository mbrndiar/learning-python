"""Shared command parsing and execution policy for all Task clients."""

import argparse
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from tasks_core.errors import incomplete

from .transport import TaskTransport, TransportFactory


@dataclass(frozen=True, slots=True)
class ClientSettings:
    """Connection settings shared by every client transport."""

    base_url: str
    timeout: float


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


def build_parser(prog: str = "tasks-cli") -> argparse.ArgumentParser:
    """Build the common parser for every documented client command."""

    parser = argparse.ArgumentParser(
        prog=prog,
        description="Call the Task REST API",
        allow_abbrev=False,
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
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


def run(arguments: argparse.Namespace, transport: TaskTransport) -> int:
    """Execute one parsed command through the selected transport."""

    del transport
    incomplete(f"client command execution for {arguments.command!r}")


def main(
    argv: Sequence[str] | None = None,
    *,
    transport_factory: TransportFactory,
    prog: str = "tasks-cli",
) -> int:
    """Parse, execute, and close one client invocation."""

    arguments = build_parser(prog).parse_args(argv)
    settings = ClientSettings(
        base_url=cast(str, arguments.base_url),
        timeout=cast(float, arguments.timeout),
    )
    transport = transport_factory(settings.base_url, settings.timeout)
    try:
        return run(arguments, transport)
    finally:
        transport.close()


__all__ = ["ClientSettings", "build_parser", "main", "run"]
