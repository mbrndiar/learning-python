"""Compose persistence and service dependencies at the process boundary.

HTTP adapters receive an already-built service, so selecting storage remains a
launcher concern rather than leaking infrastructure choices into route code.
"""

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
from typing import Literal

from tasks_core.repositories import (
    MarkdownTaskRepository,
    SQLiteTaskRepository,
    TaskRepository,
)
from tasks_core.service import TaskService

Backend = Literal["sqlite", "markdown"]


@dataclass(frozen=True, slots=True)
class ServerSettings:
    """Validated launcher settings shared by every server implementation."""

    host: str
    port: int
    backend: Backend
    data: Path


class _ServerArguments(argparse.Namespace):
    host: str
    port: int
    backend: Backend
    data: Path


def _backend(value: str) -> Backend:
    if value == "sqlite":
        return "sqlite"
    if value == "markdown":
        return "markdown"
    raise argparse.ArgumentTypeError("backend must be sqlite or markdown")


def _loopback_host(value: str) -> str:
    if value.casefold() == "localhost":
        return value
    try:
        if ip_address(value).is_loopback:
            return value
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("host must identify a loopback interface")


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "port must be an integer between 0 and 65535"
        ) from None
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return port


def build_server_parser(prog: str = "tasks-api") -> argparse.ArgumentParser:
    """Build the common server launcher parser."""

    parser = argparse.ArgumentParser(
        prog=prog,
        description="Serve the Task REST API",
        allow_abbrev=False,
    )
    parser.add_argument("--host", type=_loopback_host, default="127.0.0.1")
    parser.add_argument("--port", type=_port, default=8000)
    parser.add_argument(
        "--backend",
        choices=("sqlite", "markdown"),
        type=_backend,
        required=True,
    )
    parser.add_argument("--data", type=Path, required=True, metavar="PATH")
    return parser


def parse_server_settings(
    argv: Sequence[str] | None = None,
    *,
    prog: str = "tasks-api",
) -> ServerSettings:
    """Convert command-line strings into typed settings without opening resources."""

    arguments = _ServerArguments()
    build_server_parser(prog).parse_args(argv, namespace=arguments)
    return ServerSettings(
        host=arguments.host,
        port=arguments.port,
        backend=arguments.backend,
        data=arguments.data,
    )


def build_repository(backend: Backend, data: str | Path) -> TaskRepository:
    """Construct the persistence adapter selected at the application edge."""

    if backend == "sqlite":
        return SQLiteTaskRepository(data)
    if backend == "markdown":
        return MarkdownTaskRepository(data)
    raise ValueError(f"unsupported backend: {backend}")


def build_service(settings: ServerSettings) -> TaskService:
    """Assemble the dependency graph shared by one server process."""

    # The composition root is the only layer that needs to know which concrete
    # repository satisfies the service's TaskRepository dependency.
    return TaskService(build_repository(settings.backend, settings.data))


__all__ = [
    "Backend",
    "ServerSettings",
    "build_repository",
    "build_server_parser",
    "build_service",
    "parse_server_settings",
]
