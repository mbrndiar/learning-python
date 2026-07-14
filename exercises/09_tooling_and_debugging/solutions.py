"""
Solutions: 09 Tooling and Debugging
"""

import argparse
import logging


def build_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--verbose", action="store_true")
    return parser


def build_command_parser():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add")
    add_parser.add_argument("title")
    list_parser = commands.add_parser("list")
    list_parser.add_argument("--pending-only", action="store_true")
    return parser


def positive_int(text):
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def safe_int(text):
    try:
        return int(text)
    except ValueError:
        return None


def configure_logger(verbose):
    logger = logging.getLogger("exercise")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger


if __name__ == "__main__":
    parser = build_arg_parser()
    parsed = parser.parse_args(["myfile.txt", "--verbose"])
    assert parsed.path == "myfile.txt"
    assert parsed.verbose is True
    parsed_default = parser.parse_args(["myfile.txt"])
    assert parsed_default.verbose is False
    print("build_arg_parser: OK")

    command_parser = build_command_parser()
    add_args = command_parser.parse_args(["add", "Learn argparse"])
    assert (add_args.command, add_args.title) == ("add", "Learn argparse")
    list_args = command_parser.parse_args(["list", "--pending-only"])
    assert (list_args.command, list_args.pending_only) == ("list", True)
    print("build_command_parser: OK")

    assert positive_int("3") == 3
    try:
        positive_int("0")
        raise AssertionError("expected argparse.ArgumentTypeError")
    except argparse.ArgumentTypeError:
        pass
    print("positive_int: OK")

    assert safe_int("42") == 42
    assert safe_int("not a number") is None
    print("safe_int: OK")

    assert configure_logger(False).level == logging.INFO
    assert configure_logger(True).level == logging.DEBUG
    print("configure_logger: OK")

    print("\nAll checks passed!")
