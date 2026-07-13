"""
Solutions: 05 Modules and Files
"""

import os


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")


def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""


def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(
            f"Cannot withdraw {amount}, balance is only {balance}"
        )
    return balance - amount


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
