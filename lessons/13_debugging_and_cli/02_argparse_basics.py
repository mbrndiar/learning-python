"""
Chapter 13, Lesson 2: argparse Basics

Purpose: build a small command-line interface with `argparse`, keep the
parsing at the program boundary, and keep the core behavior in a function
that knows nothing about argparse, terminal output, or exit codes.

Prerequisites: Chapter 5 (functions) and Chapter 13 Lesson 1. Subcommands
and custom validators come next, in Lesson 3.

Run it with no arguments to see the defaults, then try your own:

    python lessons/13_debugging_and_cli/02_argparse_basics.py
    python lessons/13_debugging_and_cli/02_argparse_basics.py Ada --count 2 --shout
"""

import argparse
from collections.abc import Sequence


# Step 1: the core behavior lives in a plain function. It takes ordinary
# arguments and returns a value; it does not print, read argv, or exit.
# That separation makes it reusable from tests, another CLI, or a web
# handler.
def build_greeting(name: str, *, shout: bool = False) -> str:
    message = f"Hello, {name}!"
    return message.upper() if shout else message


# Step 2: build the parser in its own function. Each add_argument call
# declares one input: a positional argument, an option with a value, or a
# boolean flag. argparse generates --help and usage text from these.
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Greet someone a configurable number of times."
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="World",
        help="Name to greet (default: World)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        help="How many times to print the greeting (default: 1)",
    )
    # store_true makes --shout a flag: present means True, absent means
    # False. No value follows it on the command line.
    parser.add_argument(
        "--shout",
        action="store_true",
        help="Print the greeting in uppercase",
    )
    return parser


# Step 3: parse once at the boundary, then call the core logic. Passing
# argv explicitly keeps the boundary testable; None tells argparse to read
# the real process command line.
def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for _ in range(args.count):
        print(build_greeting(args.name, shout=args.shout))
    return 0


if __name__ == "__main__":
    # A fixed example runs first so the lesson is deterministic even with
    # no arguments; then the real command line is parsed.
    print("Fixed example (['Ada', '--count', '2', '--shout']):")
    run(["Ada", "--count", "2", "--shout"])

    print("\n`input()` reads one typed line; it is commented out so this")
    print("lesson runs non-interactively. Try it locally by uncommenting:")
    # typed_name = input("What's your name? ")
    # print(build_greeting(typed_name))

    print("\nNow parsing the real command line (if you passed any):")
    raise SystemExit(run())
