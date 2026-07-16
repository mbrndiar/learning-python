"""Typed command parsing and dependency construction for server launchers."""

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
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


def build_server_parser(prog: str = "tasks-api") -> argparse.ArgumentParser:
    """Build the common server launcher parser."""

    parser = argparse.ArgumentParser(
        prog=prog,
        description="Serve the Task REST API",
        allow_abbrev=False,
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
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
    """Parse one server launch without starting network resources."""

    arguments = _ServerArguments()
    build_server_parser(prog).parse_args(argv, namespace=arguments)
    return ServerSettings(
        host=arguments.host,
        port=arguments.port,
        backend=arguments.backend,
        data=arguments.data,
    )


def build_repository(backend: Backend, data: str | Path) -> TaskRepository:
    """Construct the selected milestone-two persistence adapter."""

    if backend == "sqlite":
        return SQLiteTaskRepository(data)
    return MarkdownTaskRepository(data)


def build_service(settings: ServerSettings) -> TaskService:
    """Construct the shared service for one server process."""

    return TaskService(build_repository(settings.backend, settings.data))


__all__ = [
    "Backend",
    "ServerSettings",
    "build_repository",
    "build_server_parser",
    "build_service",
    "parse_server_settings",
]
