"""Launch the FastAPI Task HTTP server."""

import argparse
from collections.abc import Sequence
from ipaddress import ip_address

from tasks_api.bootstrap import (
    build_server_parser,
    build_service,
    parse_server_settings,
)

from .app import serve


def build_parser() -> argparse.ArgumentParser:
    """Build this launcher's documented command parser."""

    return build_server_parser("tasks-api-fastapi")


def _is_loopback(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


def main(argv: Sequence[str] | None = None) -> int:
    """Compose local storage, the shared service, FastAPI, and Uvicorn."""

    settings = parse_server_settings(argv, prog="tasks-api-fastapi")
    if not _is_loopback(settings.host):
        build_parser().error("--host must identify a loopback interface")
    if not 1 <= settings.port <= 65535:
        build_parser().error("--port must be between 1 and 65535")
    serve(build_service(settings), settings.host, settings.port)


__all__ = ["build_parser", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
