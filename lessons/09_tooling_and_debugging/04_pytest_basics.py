"""
Lesson 9.4: Introduction to pytest

`pytest` is the most widely used third-party testing framework in the
Python ecosystem. Unlike `unittest` (lesson 8.1), tests are plain
functions and assertions are plain `assert` statements - pytest rewrites
them to give readable failure messages.

This lesson requires an optional dependency. Install it with:
    pip install -r requirements-dev.txt

Then run the tests with:
    pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
"""


def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


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
    try:
        import pytest
    except ImportError:
        # Fall back to a plain assertion if pytest isn't installed, so
        # this file can still be executed with plain `python`.
        try:
            divide(10, 0)
            raise AssertionError("expected ValueError")
        except ValueError:
            return
    with pytest.raises(ValueError):
        divide(10, 0)


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
        "  pytest lessons/09_tooling_and_debugging/04_pytest_basics.py -v"
    )
