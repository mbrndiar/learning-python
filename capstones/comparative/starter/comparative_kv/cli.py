"""Milestone 2 command boundary.

The only forms are::

    --db PATH set KEY --value-json JSON [--expect EXPECTATION]
    --db PATH get KEY
    --db PATH delete KEY [--expect EXPECTATION]
    --db PATH list

Shared options are case-sensitive, separate arguments, positioned as shown,
and accepted exactly once; aliases, ``--name=value``, extras, and abbreviation
are usage errors.  See ``test_m2_cli.py`` and ``fixtures/invalid.json``.
"""

import argparse
from collections.abc import Sequence

from .errors import incomplete


def build_parser() -> argparse.ArgumentParser:
    """Build the public parser for the frozen grammar.

    The completed milestone must translate every parser failure into the
    contract's JSON usage response rather than argparse prose or stderr.
    """

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
    """Validate, execute, and emit the command's one response.

    Preserve precedence: grammar/database-path form; key and expectation;
    set-value byte, syntax, and tree checks; storage open/progression; command
    execution.  Thus invalid input wins over missing or malformed storage and
    cannot create it.  Every covered outcome writes one compact JSON object plus
    LF to stdout, nothing to stderr, and returns its specified exit code.
    """

    # TODO(m2): Preserve validation order and emit exactly one contract envelope.
    incomplete(f"comparative command execution for {arguments.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse one non-interactive command and return its process exit code."""

    return run(build_parser().parse_args(argv))
