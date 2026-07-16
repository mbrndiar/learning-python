"""Launch the standard-library Task HTTP server."""

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from tasks_core.service import TaskService

from tasks_api.bootstrap import build_repository

from .app import serve

RepositoryName = Literal["sqlite", "markdown"]


class _Arguments(argparse.Namespace):
    host: str
    port: int
    repository: RepositoryName
    storage: Path


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535") from error
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return port


def _repository(value: str) -> RepositoryName:
    if value == "sqlite":
        return "sqlite"
    if value == "markdown":
        return "markdown"
    raise argparse.ArgumentTypeError("repository must be sqlite or markdown")


def build_parser() -> argparse.ArgumentParser:
    """Build this launcher's documented command parser."""

    parser = argparse.ArgumentParser(
        prog="tasks-api-stdlib",
        description="Serve the Task REST API with the Python standard library",
        allow_abbrev=False,
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=_port, default=8000)
    parser.add_argument(
        "--repository",
        type=_repository,
        choices=("sqlite", "markdown"),
        required=True,
    )
    parser.add_argument("--storage", type=Path, required=True, metavar="PATH")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse settings and start the standard-library adapter."""

    arguments = _Arguments()
    build_parser().parse_args(argv, namespace=arguments)
    service = TaskService(
        build_repository(arguments.repository, arguments.storage),
    )
    serve(service, arguments.host, arguments.port)
    return 0


__all__ = ["build_parser", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
