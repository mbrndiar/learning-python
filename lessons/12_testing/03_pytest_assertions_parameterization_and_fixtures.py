"""
Chapter 12, Lesson 3: pytest Assertions, Parameterization, and Fixtures

Purpose: write tests as plain functions with plain `assert`; expect
exceptions with `pytest.raises`; turn one behavior into many reported
cases with `@pytest.mark.parametrize`; and isolate resources with
fixtures, including the built-in `tmp_path`.

Prerequisites: Lessons 1-2. pytest is a third-party tool already listed in
`requirements-dev.txt`; install it with
`python -m pip install -r requirements-dev.txt` if needed.

This lesson is meant to be run *by pytest* so its assertions are rewritten
into readable failure messages:

    python -m pytest lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py -v

Running `python <this file>` simply hands the file to pytest for you.
"""

from pathlib import Path

import pytest


# Step 1: the code under test.
def add(a: int, b: int) -> int:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b


def write_report(path: Path, values: list[int]) -> None:
    """Write one integer per line so a test can read it back."""
    path.write_text("\n".join(str(value) for value in values) + "\n", encoding="utf-8")


# Step 2: pytest discovers any function named test_*. No class or base
# class is required, and a bare `assert` is enough: pytest rewrites the
# expression so a failure shows both operands.
def test_add_returns_sum() -> None:
    assert add(2, 3) == 5


# Step 3: pytest.raises is the pytest equivalent of assertRaises. The
# `match` argument checks the message with a regular expression, so an
# unrelated ValueError cannot satisfy the test by accident.
def test_divide_by_zero_raises() -> None:
    with pytest.raises(ValueError, match="zero"):
        divide(10, 0)


# Step 4: parameterization runs the same test body once per row and
# reports each row as a separate result. Unlike a loop, a failing row does
# not prevent the remaining rows from running and being reported.
@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(2, 3, 5), (-1, -1, -2), (0, 5, 5)],
)
def test_add_examples(a: int, b: int, expected: int) -> None:
    assert add(a, b) == expected


# Step 5: a fixture is a function that produces test input. A test
# requests it by naming a parameter after the fixture. This keeps setup in
# one reusable place and out of every test body.
@pytest.fixture
def sample_values() -> list[int]:
    return [3, 5, 8]


def test_fixture_supplies_values(sample_values: list[int]) -> None:
    assert sum(sample_values) == 16


# Step 6: tmp_path is a built-in fixture giving each test a unique, empty
# directory. Tests that touch the filesystem must use it instead of real
# project files, so they stay isolated and deterministic.
def test_write_report_uses_isolated_directory(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"

    write_report(report, [3, 5])

    assert report.read_text(encoding="utf-8") == "3\n5\n"


if __name__ == "__main__":
    # Hand this file to the real pytest runner instead of re-implementing
    # one. When pytest imports the module for collection, __name__ is not
    # "__main__", so this line does not run recursively.
    raise SystemExit(pytest.main([__file__, "-v"]))
