"""
Exercises: 09 Tooling and Debugging

Implement each function below, then run this file directly to check
your work.
"""

import argparse
import logging


def build_arg_parser():
    """Return an argparse.ArgumentParser with:
    - a required positional argument "path"
    - an optional "--verbose" flag (True/False, default False)
    """
    # TODO: implement this function
    raise NotImplementedError


def build_command_parser():
    """Return a parser with `add TITLE` and `list --pending-only` commands."""
    # TODO: implement this function with add_subparsers(required=True)
    raise NotImplementedError


def positive_int(text):
    """Convert text to a positive int or raise argparse.ArgumentTypeError."""
    # TODO: implement this function
    raise NotImplementedError


def safe_int(text):
    """Return int(text), or None after catching only ValueError."""
    # TODO: implement this function
    raise NotImplementedError


def configure_logger(verbose):
    """Return a named logger set to DEBUG when verbose, otherwise INFO."""
    # TODO: implement this function
    raise NotImplementedError


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
