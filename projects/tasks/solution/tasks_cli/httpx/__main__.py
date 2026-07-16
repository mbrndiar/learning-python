"""Launch the HTTPX Task client."""

import argparse
from collections.abc import Sequence

from tasks_cli.application import build_parser as build_client_parser
from tasks_cli.application import main as application_main

from .adapter import create_transport


def build_parser() -> argparse.ArgumentParser:
    """Build this launcher's documented command parser."""

    return build_client_parser("tasks-cli-httpx")


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command through the HTTPX transport."""

    return application_main(
        argv,
        transport_factory=create_transport,
        prog="tasks-cli-httpx",
    )


__all__ = ["build_parser", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
