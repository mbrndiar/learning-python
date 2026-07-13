"""
Exercises: 05 Modules and Files

Implement each function below, then run this file directly to check
your work.
"""

import os


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


if __name__ == "__main__":
    sample_path = os.path.join(os.path.dirname(__file__), "sample_exercise.txt")

    write_lines(sample_path, ["alpha", "beta", "gamma"])
    assert read_lines(sample_path) == ["alpha", "beta", "gamma"]
    os.remove(sample_path)
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

    print("\nAll checks passed!")
