"""
Lesson 9.3: Reading Input and Command-Line Arguments

Two common ways a script receives data from its user: interactively via
`input()`, and non-interactively via command-line arguments parsed with
`argparse`, including subcommands for multi-operation programs.
"""

import argparse


def positive_int(text):
    """Convert CLI text to a positive integer for argparse."""
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Greet someone a configurable number of times."
    )
    parser.add_argument("name", nargs="?", default="World", help="Name to greet")
    parser.add_argument(
        "-c",
        "--count",
        type=positive_int,
        default=1,
        help="Number of times to print the greeting (default: 1)",
    )
    parser.add_argument(
        "--shout",
        action="store_true",
        help="Print the greeting in uppercase",
    )
    return parser


def build_greeting(name, shout=False):
    """Return core application output without depending on argparse."""
    message = f"Hello, {name}!"
    return message.upper() if shout else message


def build_command_parser():
    """Build a small multi-command interface like the capstone CLI."""
    parser = argparse.ArgumentParser(description="Manage short notes")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Add a note")
    add_parser.add_argument("text")
    commands.add_parser("list", help="List notes")
    return parser


def run(argv=None):
    """Parse the CLI boundary, call core logic, and return an exit status."""
    args = build_parser().parse_args(argv)

    for _ in range(args.count):
        print(build_greeting(args.name, shout=args.shout))

    command_args = build_command_parser().parse_args(["add", "Read argparse help"])
    print("\nParsed subcommand:", command_args.command, command_args.text)

    print(
        "\n`input()` reads a line of text typed by the user. It is "
        "commented out here so the lesson can run non-interactively "
        "(e.g. in CI), but try uncommenting it locally:"
    )
    # typed_name = input("What's your name? ")
    # print(build_greeting(typed_name))

    print(
        "\nTry running this file yourself with arguments, for example:\n"
        "  python lessons/09_tooling_and_debugging/03_command_line_arguments.py Ada --count 2 --shout"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
