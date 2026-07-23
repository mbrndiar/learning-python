"""
Exercises: Chapter 13 - Debugging and Command-Line Interfaces

Implement each function below, then run this file directly to check your
work:

    python exercises/13_debugging_and_cli/exercises.py

Each starter raises NotImplementedError until you implement it. The checks
run in order and stop at the first failure, so implement the functions from
top to bottom. A separate guided pdb lab in the README practices interactive
debugging without leaving broken files in the repository.
"""

import argparse
import logging


def build_arg_parser() -> argparse.ArgumentParser:
    """Return a simple parser (no subcommands) with:

    - a required positional argument "path";
    - an optional "--verbose" flag that stores True when present and
      defaults to False.
    """
    # TODO: create an ArgumentParser, add the positional and the flag, return it
    raise NotImplementedError


def positive_int(text: str) -> int:
    """Convert text to a positive int for use as an argparse `type=`.

    Raise argparse.ArgumentTypeError when the text is not an integer or is
    not strictly greater than zero, so argparse reports your precise message
    instead of its generic "invalid value" text.
    """
    # TODO: convert with int(); on failure or non-positive, raise
    # argparse.ArgumentTypeError
    raise NotImplementedError


def safe_int(text: str) -> int | None:
    """Return int(text), or None after catching only ValueError.

    Do not catch other exceptions; only the conversion error is expected
    and handleable here.
    """
    # TODO: try int(text); return None only on ValueError
    raise NotImplementedError


def build_command_parser() -> argparse.ArgumentParser:
    """Return a parser with two subcommands:

    - `add TITLE` (a positional "title" argument);
    - `list --pending-only` (a boolean flag).

    Use add_subparsers(dest="command", required=True) and attach the
    positive_int validator to an `--priority` option on `add`.
    """
    # TODO: build subparsers with required=True and both commands
    raise NotImplementedError


def configure_logger(verbose: bool) -> logging.Logger:
    """Return a named logger set to DEBUG when verbose, otherwise INFO."""
    # TODO: get a named logger, set its level from verbose, return it
    raise NotImplementedError


parser = build_arg_parser()
parsed = parser.parse_args(["myfile.txt", "--verbose"])
assert parsed.path == "myfile.txt"
assert parsed.verbose is True
default = parser.parse_args(["myfile.txt"])
assert default.verbose is False
print("build_arg_parser: OK")

assert positive_int("3") == 3
for bad in ("0", "-2", "not a number"):
    try:
        positive_int(bad)
    except argparse.ArgumentTypeError:
        pass
    else:
        raise AssertionError(f"positive_int({bad!r}) should raise ArgumentTypeError")
print("positive_int: OK")

assert safe_int("42") == 42
assert safe_int("not a number") is None
try:
    safe_int(None)  # type: ignore[arg-type]
except TypeError:
    pass
else:
    raise AssertionError("safe_int must not swallow unexpected TypeError")
print("safe_int: OK")

command_parser = build_command_parser()
add_args = command_parser.parse_args(["add", "Learn argparse", "--priority", "3"])
assert (add_args.command, add_args.title, add_args.priority) == (
    "add",
    "Learn argparse",
    3,
)
list_args = command_parser.parse_args(["list", "--pending-only"])
assert (list_args.command, list_args.pending_only) == ("list", True)
try:
    command_parser.parse_args(["add", "Broken", "--priority", "0"])
except SystemExit:
    pass
else:
    raise AssertionError("an invalid --priority must be rejected at the boundary")
print("build_command_parser: OK")

normal_logger = configure_logger(False)
assert normal_logger.level == logging.INFO
verbose_logger = configure_logger(True)
assert normal_logger.name == "exercise"
assert verbose_logger.name == "exercise"
assert verbose_logger.level == logging.DEBUG
print("configure_logger: OK")

print("\nAll checks passed!")
