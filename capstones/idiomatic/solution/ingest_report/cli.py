"""Command parser and execution boundary for the idiomatic capstone."""

import argparse
from collections.abc import Sequence

from .errors import incomplete


def build_parser() -> argparse.ArgumentParser:
    """Build documented ingest/report command shapes."""

    parser = argparse.ArgumentParser(
        prog="ingest-report",
        description="Ingest operational events and produce reports",
        allow_abbrev=False,
    )
    parser.add_argument("--db", required=True, metavar="PATH")
    parser.add_argument("--json-errors", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)

    ingest_parser = commands.add_parser("ingest", allow_abbrev=False)
    ingest_parser.add_argument("--import-id", required=True)
    ingest_parser.add_argument(
        "--format",
        choices=("csv", "jsonl", "http"),
        required=True,
    )
    ingest_parser.add_argument("--input")
    ingest_parser.add_argument("--url")
    ingest_parser.add_argument("--workers", type=int, default=4)
    ingest_parser.add_argument("--allow-partial", action="store_true")

    report_parser = commands.add_parser("report", allow_abbrev=False)
    report_parser.add_argument("--from", dest="from_timestamp")
    report_parser.add_argument("--to", dest="to_timestamp")
    report_parser.add_argument("--category")
    report_parser.add_argument("--status", choices=("success", "warning", "failure"))
    report_parser.add_argument("--output", choices=("json", "text"), default="text")
    return parser


def run(arguments: argparse.Namespace) -> int:
    """Execute parsed arguments once application behavior is implemented."""

    incomplete(f"idiomatic command execution for {arguments.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse one command and return its eventual process exit code."""

    return run(build_parser().parse_args(argv))
