"""
Solutions: 09 Tooling and Debugging
"""

import argparse
import logging
import os
import subprocess
import sys
from collections.abc import Mapping


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


def parse_process_timeout(environment: Mapping[str, str]) -> int:
    """Return a validated timeout without reading or changing os.environ."""
    raw_timeout = environment.get("PROCESS_TIMEOUT", "5")
    try:
        timeout = int(raw_timeout)
    except ValueError as error:
        raise ValueError("PROCESS_TIMEOUT must be an integer") from error
    if not 1 <= timeout <= 30:
        raise ValueError("PROCESS_TIMEOUT must be between 1 and 30")
    return timeout


def build_child_command(message: str) -> list[str]:
    """Build a command whose message remains one literal argument."""
    child_code = "import sys; print(sys.argv[1])"
    return [sys.executable, "-c", child_code, message]


def run_child_process(
    message: str, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    """Run a portable child process without invoking a command shell."""
    return subprocess.run(
        build_child_command(message),
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
        env=dict(environment),
    )


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

    sample_environment = {"PROCESS_TIMEOUT": "7"}
    assert parse_process_timeout(sample_environment) == 7
    assert parse_process_timeout({}) == 5
    assert sample_environment == {"PROCESS_TIMEOUT": "7"}
    try:
        parse_process_timeout({"PROCESS_TIMEOUT": "0"})
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    print("parse_process_timeout: OK")

    message = "hello; this is one argument"
    command = build_child_command(message)
    assert command[0] == sys.executable
    assert command[-1] == message
    child = run_child_process(message, os.environ)
    assert child.stdout == "hello; this is one argument\n"
    assert child.stderr == ""
    assert child.returncode == 0
    print("run_child_process: OK")

    print("\nAll checks passed!")
