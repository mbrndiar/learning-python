"""
Exercises: 05 Modules and Files

Implement each function below, then run this file directly to check
your work.
"""

import json
import sys
from contextlib import contextmanager
from pathlib import Path

# Make example_package importable from this exercise file.
sys.path.insert(0, str(Path(__file__).parents[2] / "lessons" / "05_modules_and_files"))


def write_lines(path, lines):
    """Write each string in `lines` to the file at `path`, one per line."""
    # TODO: implement this function
    raise NotImplementedError


def read_lines(path):
    """Return a list of lines from the file at `path`, without trailing
    newline characters."""
    # TODO: implement this function
    raise NotImplementedError


def safe_divide(a, b):
    """Return a / b, or None if `b` is zero (catch the exception instead
    of checking `b == 0` directly)."""
    # TODO: implement this function
    raise NotImplementedError


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""


def withdraw(balance, amount):
    """Return the new balance after withdrawing `amount`.

    Raise InsufficientFundsError if `amount` is greater than `balance`.
    """
    # TODO: implement this function
    raise NotImplementedError


def save_json(path, data):
    """Write data as indented JSON followed by one newline."""
    # TODO: implement this function
    raise NotImplementedError


def load_json(path):
    """Read and decode JSON from path."""
    # TODO: implement this function
    raise NotImplementedError


@contextmanager
def temporary_value(mapping, key, value):
    """Temporarily assign mapping[key] and restore its previous state."""
    # TODO: implement this context manager with try/finally and yield
    raise NotImplementedError


def describe_greeting(name: str) -> str:
    """Return a polite greeting for *name* by importing ``hello`` from
    ``example_package.greetings`` and calling it.

    Use an absolute import (``from example_package.greetings import hello``).
    ``example_package`` is already on sys.path at the top of this file.
    """
    # TODO: import hello from example_package.greetings and return hello(name)
    raise NotImplementedError


if __name__ == "__main__":
    sample_path = Path(__file__).with_name("sample_exercise.txt")

    write_lines(sample_path, ["alpha", "beta", "gamma"])
    assert read_lines(sample_path) == ["alpha", "beta", "gamma"]
    sample_path.unlink()
    print("write_lines/read_lines: OK")

    assert safe_divide(10, 2) == 5
    assert safe_divide(10, 0) is None
    print("safe_divide: OK")

    assert withdraw(100, 40) == 60
    try:
        withdraw(100, 150)
        raise AssertionError("expected InsufficientFundsError")
    except InsufficientFundsError:
        pass
    print("withdraw: OK")

    json_path = Path(__file__).with_name("sample_exercise.json")
    save_json(json_path, {"name": "Ada", "active": True})
    assert load_json(json_path) == {"name": "Ada", "active": True}
    assert json_path.read_text(encoding="utf-8").endswith("\n")
    json_path.unlink()
    print("save_json/load_json: OK")

    settings = {"mode": "normal"}
    with temporary_value(settings, "mode", "debug"):
        assert settings["mode"] == "debug"
    assert settings == {"mode": "normal"}
    with temporary_value(settings, "new", 1):
        assert settings["new"] == 1
    assert "new" not in settings
    print("temporary_value: OK")

    assert describe_greeting("Ada") == "Hello, Ada!"
    assert describe_greeting("grace hopper") == "Hello, Grace Hopper!"
    print("describe_greeting: OK")

    print("\nAll checks passed!")
