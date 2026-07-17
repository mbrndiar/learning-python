"""Launch the FastAPI Task HTTP server."""

import argparse
from collections.abc import Sequence

from tasks_api.bootstrap import (
    build_server_parser,
    build_service,
    parse_server_settings,
)

from .app import serve


def build_parser() -> argparse.ArgumentParser:
    """Build this launcher's documented command parser."""

    return build_server_parser("tasks-api-fastapi")


def main(argv: Sequence[str] | None = None) -> int:
    """Compose local storage, the shared service, FastAPI, and Uvicorn."""

    settings = parse_server_settings(argv, prog="tasks-api-fastapi")
    serve(build_service(settings), settings.host, settings.port)
    return 0


__all__ = ["build_parser", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
