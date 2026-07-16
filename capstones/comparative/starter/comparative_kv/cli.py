"""Command parser and execution boundary for the comparative capstone."""

import argparse
from collections.abc import Sequence

from .errors import incomplete


def build_parser() -> argparse.ArgumentParser:
    """Build the canonical command shape without implementing behavior."""

    parser = argparse.ArgumentParser(
        prog="comparative-kv",
        description="A versioned SQLite key/value configuration store",
        allow_abbrev=False,
    )
    parser.add_argument("--db", required=True, metavar="PATH")
    commands = parser.add_subparsers(dest="command", required=True)

    set_parser = commands.add_parser("set", allow_abbrev=False)
    set_parser.add_argument("key", metavar="KEY")
    set_parser.add_argument("--value-json", required=True, dest="value_json")
    set_parser.add_argument("--expect", default="any")

    get_parser = commands.add_parser("get", allow_abbrev=False)
    get_parser.add_argument("key", metavar="KEY")

    delete_parser = commands.add_parser("delete", allow_abbrev=False)
    delete_parser.add_argument("key", metavar="KEY")
    delete_parser.add_argument("--expect", default="any")

    commands.add_parser("list", allow_abbrev=False)
    return parser


def run(arguments: argparse.Namespace) -> int:
    """TODO(m2): validate, execute, and emit exactly one JSON envelope."""

    incomplete(f"comparative command execution for {arguments.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse one command and return its eventual process exit code."""

    return run(build_parser().parse_args(argv))
