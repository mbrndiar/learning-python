"""
Lesson 9.4: Introduction to pytest

`pytest` is a widely used third-party testing framework in the
Python ecosystem. Unlike `unittest` (lesson 8.1), tests are plain
functions and assertions are plain `assert` statements - pytest rewrites
them to give readable failure messages.

This lesson requires an optional dependency. Install it with:
    python -m pip install -r requirements-dev.txt

Then run the tests with:
    python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
"""

from pathlib import Path

try:
    import pytest
except ImportError:  # The direct-run fallback below still demonstrates assert.
    pytest = None


def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def write_report(path: Path, values: list[int]) -> None:
    """Write one value per line so a test can use an isolated directory."""
    path.write_text("\n".join(str(value) for value in values) + "\n", encoding="utf-8")


# --- pytest test functions -------------------------------------------------
# pytest auto-discovers any function whose name starts with `test_`.
# No class or base class is required (though pytest can also run
# unittest.TestCase classes).


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -1) == -2


def test_divide_normal_case():
    assert divide(10, 4) == 2.5


def test_divide_by_zero_raises():
    if pytest is None:
        try:
            divide(10, 0)
            raise AssertionError("expected ValueError")
        except ValueError:
            return
    with pytest.raises(ValueError, match="zero"):
        divide(10, 0)


if pytest is not None:

    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [(2, 3, 5), (-1, -1, -2), (0, 5, 5)],
    )
    def test_add_examples(a, b, expected):
        assert add(a, b) == expected

    def test_write_report_uses_isolated_directory(tmp_path):
        report = tmp_path / "report.txt"

        write_report(report, [3, 5])

        assert report.read_text(encoding="utf-8") == "3\n5\n"


if __name__ == "__main__":
    # Running this file directly (without pytest installed) just executes
    # the test functions manually and reports pass/fail, so the lesson
    # still works with no external dependencies.
    tests = [
        test_add_positive_numbers,
        test_add_negative_numbers,
        test_divide_normal_case,
        test_divide_by_zero_raises,
    ]
    print("Running tests without pytest (plain assertions):")
    for test in tests:
        test()
        print(f"  PASSED: {test.__name__}")

    print(
        "\nWith pytest installed, run instead:\n"
        "  python -m pytest "
        "lessons/09_tooling_and_debugging/04_pytest_basics.py -v\n"
        "pytest will also run the parameterized and tmp_path examples."
    )
