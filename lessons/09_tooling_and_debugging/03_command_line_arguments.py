"""
Lesson 9.3: Reading Input and Command-Line Arguments

Two common ways a script receives data from its user: interactively via
`input()`, and non-interactively via command-line arguments parsed with
`argparse`, including subcommands for multi-operation programs.
"""

import argparse
import sys


def build_parser():
    parser = argparse.ArgumentParser(
        description="Greet someone a configurable number of times."
    )
    parser.add_argument("name", nargs="?", default="World", help="Name to greet")
    parser.add_argument(
        "-c",
        "--count",
        type=int,
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


if __name__ == "__main__":
    parser = build_parser()
    # sys.argv[1:] holds whatever the script was invoked with, e.g.:
    #   python 03_command_line_arguments.py Ada --count 2 --shout
    args = parser.parse_args(sys.argv[1:])

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
