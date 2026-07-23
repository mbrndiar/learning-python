"""
Chapter 13, Lesson 3: Subcommands and Custom Validation

Purpose: reject invalid arguments at the boundary with a custom
`type=` validator that raises `argparse.ArgumentTypeError`, and build a
multi-command interface with `add_subparsers`, the same shape used by the
course's capstone CLI.

Prerequisites: Lesson 2 (simple parser construction). A custom validator
is just a function that converts one string argument and raises on bad
input; argparse turns that into clean usage output and a nonzero exit.

Run it from the repository root:

    python lessons/13_debugging_and_cli/03_subcommands_and_custom_validation.py
"""

import argparse
from collections.abc import Sequence


# Step 1: a custom validator converts and validates one argument value.
# ArgumentTypeError lets the validator supply a precise message such as
# "must be positive". argparse also catches ValueError and TypeError, but
# replaces them with a generic "invalid value" usage error.
def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


# Step 2: a subcommand interface. add_subparsers creates a slot for a
# command word; each add_parser defines that command's own arguments.
# required=True means the user must choose a command. dest="command"
# records which one they chose.
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage short notes.")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Add a note")
    add_parser.add_argument("text", help="Note text")
    # The custom validator is attached with type=, so argparse applies it
    # automatically and reports errors uniformly.
    add_parser.add_argument(
        "--priority",
        type=positive_int,
        default=1,
        help="Positive integer priority (default: 1)",
    )

    list_parser = commands.add_parser("list", help="List notes")
    list_parser.add_argument(
        "--pending-only",
        action="store_true",
        help="Show only pending notes",
    )
    return parser


def describe(args: argparse.Namespace) -> str:
    """Turn parsed arguments into a deterministic description string."""
    if args.command == "add":
        return f"add: text={args.text!r} priority={args.priority}"
    return f"list: pending_only={args.pending_only}"


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(describe(args))
    return 0


if __name__ == "__main__":
    # Deterministic examples covering both subcommands and the validator.
    print("Example: add a note with a valid priority")
    run(["add", "Read argparse docs", "--priority", "3"])

    print("\nExample: list with a flag")
    run(["list", "--pending-only"])

    print("\nExample: an invalid priority is rejected at the boundary")
    try:
        # parse_args calls sys.exit(2) on invalid input; catch it so the
        # lesson can show the behavior and keep running.
        run(["add", "Broken", "--priority", "0"])
    except SystemExit as exit_status:
        print(f"argparse exited with status {exit_status.code} (2 means usage error)")
