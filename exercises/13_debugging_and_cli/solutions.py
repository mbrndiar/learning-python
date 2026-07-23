"""
Solutions: Chapter 13 - Debugging and Command-Line Interfaces
"""

import argparse
import logging


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--verbose", action="store_true")
    return parser


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def safe_int(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None


def build_command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add")
    add_parser.add_argument("title")
    add_parser.add_argument("--priority", type=positive_int, default=1)

    list_parser = commands.add_parser("list")
    list_parser.add_argument("--pending-only", action="store_true")
    return parser


def configure_logger(verbose: bool) -> logging.Logger:
    logger = logging.getLogger("exercise")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger


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
assert normal_logger.name == "exercise"
assert normal_logger.level == logging.INFO
verbose_logger = configure_logger(True)
assert verbose_logger.name == "exercise"
assert verbose_logger.level == logging.DEBUG
print("configure_logger: OK")

print("\nAll checks passed!")
