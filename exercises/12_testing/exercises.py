"""
Exercises: Chapter 12 - Automated Testing

This exercise is about writing tests yourself, in both frameworks:

1. unittest test methods on `TestCalculator` (mutation-checked in place);
2. pytest test functions using parameterization, a fixture, and
   `pytest.raises`;
3. one unittest method that verifies a collaborator boundary with a
   constrained `Mock(spec=...)`.

Run the evaluator from the repository root:

    python exercises/12_testing/exercises.py

pytest must be installed (see docs/SETUP.md). The evaluator runs your
pytest tests for you and temporarily replaces Calculator methods with
deliberately faulty versions to confirm your assertions catch real bugs.
"""

import importlib.util
import io
import sys
import unittest
from typing import Protocol
from unittest.mock import Mock, call


class Calculator:
    """The code under test."""

    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("cannot divide by zero")
        return a / b


class MessageSender(Protocol):
    def send(self, recipient: str, message: str) -> None: ...


def notify_all(sender: MessageSender, recipients: list[str], message: str) -> None:
    """Send a message to each recipient through an injected collaborator."""
    for recipient in recipients:
        sender.send(recipient, message)


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.calculator = Calculator()

    # TODO: write test_add asserting Calculator().add(2, 3) == 5.

    # TODO: write test_subtract asserting Calculator().subtract(5, 3) == 2.

    # TODO: write test_divide_by_zero_raises asserting that divide(1, 0)
    # raises ValueError (use self.assertRaises).

    # TODO: write test_add_examples_with_subtests. Loop over several
    # (a, b, expected) rows and use self.subTest(a=a, b=b) so one failing
    # row does not hide the others.

    # TODO: write test_notify_all_uses_sender_boundary. Build a
    # Mock(spec=...) sender, call notify_all for two recipients, and assert
    # on sender.send.call_args_list with the expected call(...) values.


# TODO: write a pytest test function named test_add_parametrized. Decorate
# it with @pytest.mark.parametrize over at least three (a, b, expected)
# rows and assert Calculator().add(a, b) == expected.


# TODO: write a pytest fixture named calculator that returns a Calculator,
# and a test function test_subtract_with_fixture(calculator) that asserts
# calculator.subtract(9, 4) == 5 using it.


# TODO: write a pytest test function named test_divide_by_zero_pytest that
# uses pytest.raises(ValueError, match="zero") around Calculator().divide.


REQUIRED_UNITTEST_METHODS = (
    "test_add",
    "test_subtract",
    "test_divide_by_zero_raises",
    "test_add_examples_with_subtests",
    "test_notify_all_uses_sender_boundary",
)
REQUIRED_PYTEST_OBJECTS = (
    "test_add_parametrized",
    "calculator",
    "test_subtract_with_fixture",
    "test_divide_by_zero_pytest",
)


def _missing_unittest_methods() -> list[str]:
    available = set(unittest.defaultTestLoader.getTestCaseNames(TestCalculator))
    return sorted(set(REQUIRED_UNITTEST_METHODS) - available)


def _missing_pytest_objects() -> list[str]:
    return [name for name in REQUIRED_PYTEST_OBJECTS if name not in globals()]


def _run_unittest_mutations() -> int:
    """Confirm each unittest method detects an intentionally faulty change."""
    mutations = (
        ("test_add", Calculator, "add", lambda self, a, b: a - b),
        ("test_subtract", Calculator, "subtract", lambda self, a, b: a + b),
        ("test_divide_by_zero_raises", Calculator, "divide", lambda self, a, b: 0.0),
        (
            "test_add_examples_with_subtests",
            Calculator,
            "add",
            lambda self, a, b: a + b + 1,
        ),
    )
    for test_name, owner, attribute, faulty in mutations:
        original = getattr(owner, attribute)
        setattr(owner, attribute, faulty)
        try:
            mutation = unittest.TextTestRunner(stream=io.StringIO()).run(
                unittest.TestSuite([TestCalculator(test_name)])
            )
        finally:
            setattr(owner, attribute, original)
        if mutation.wasSuccessful():
            print(
                f"{test_name} did not detect an intentionally faulty implementation",
                file=sys.stderr,
            )
            return 1

    observed_specs: list[object] = []
    real_mock = globals()["Mock"]

    def tracking_mock(*args: object, **kwargs: object) -> Mock:
        observed_specs.append(kwargs.get("spec", kwargs.get("spec_set")))
        return real_mock(*args, **kwargs)

    globals()["Mock"] = tracking_mock
    try:
        spec_result = unittest.TextTestRunner(stream=io.StringIO()).run(
            unittest.TestSuite([TestCalculator("test_notify_all_uses_sender_boundary")])
        )
    finally:
        globals()["Mock"] = real_mock
    if not spec_result.wasSuccessful() or MessageSender not in observed_specs:
        print(
            "test_notify_all_uses_sender_boundary must use "
            "Mock(spec=MessageSender) or Mock(spec_set=MessageSender)",
            file=sys.stderr,
        )
        return 1

    original_notify_all = globals()["notify_all"]
    globals()["notify_all"] = lambda sender, recipients, message: None
    try:
        mutation = unittest.TextTestRunner(stream=io.StringIO()).run(
            unittest.TestSuite([TestCalculator("test_notify_all_uses_sender_boundary")])
        )
    finally:
        globals()["notify_all"] = original_notify_all
    if mutation.wasSuccessful():
        print(
            "test_notify_all_uses_sender_boundary did not detect a no-op sender loop",
            file=sys.stderr,
        )
        return 1
    return 0


def _parametrize_rows() -> list[tuple[object, object, object]]:
    """Return the declared three-column rows from the learner's pytest mark."""
    test = globals()["test_add_parametrized"]
    for mark in getattr(test, "pytestmark", []):
        if getattr(mark, "name", None) != "parametrize" or len(mark.args) < 2:
            continue
        rows: list[tuple[object, object, object]] = []
        for row in mark.args[1]:
            values = getattr(row, "values", row)
            if isinstance(values, (list, tuple)) and len(values) == 3:
                rows.append(tuple(values))
        if len(rows) >= 3:
            return rows
    return []


def _fixture_factory():
    """Return the original function wrapped by @pytest.fixture, if present."""
    fixture = globals()["calculator"]
    wrapped = getattr(fixture, "__pytest_wrapped__", None)
    factory = getattr(wrapped, "obj", None)
    if callable(factory):
        return factory
    if hasattr(fixture, "_fixture_function_marker"):
        return getattr(fixture, "__wrapped__", None)
    return None


def _detects_fault(
    test,
    owner: type,
    attribute: str,
    faulty,
    args: tuple[object, ...],
    pytest_failure: type[BaseException],
) -> bool:
    """Return whether one test fails while a dependency is deliberately wrong."""
    original = getattr(owner, attribute)
    setattr(owner, attribute, faulty)
    try:
        try:
            test(*args)
        except (AssertionError, pytest_failure):
            return True
        return False
    finally:
        setattr(owner, attribute, original)


def run_tests() -> int:
    missing_unittest = _missing_unittest_methods()
    if missing_unittest:
        print(
            "Add the requested unittest methods: " + ", ".join(missing_unittest),
            file=sys.stderr,
        )
        return 1

    missing_pytest = _missing_pytest_objects()
    if missing_pytest:
        print(
            "Add the requested pytest objects: " + ", ".join(missing_pytest),
            file=sys.stderr,
        )
        return 1

    if importlib.util.find_spec("pytest") is None:
        print(
            "pytest is not installed; run python -m pip install -r requirements-dev.txt",
            file=sys.stderr,
        )
        return 1
    pytest = __import__("pytest")

    rows = _parametrize_rows()
    if not rows:
        print(
            "test_add_parametrized must use @pytest.mark.parametrize "
            "with at least three (a, b, expected) rows",
            file=sys.stderr,
        )
        return 1
    fixture_factory = _fixture_factory()
    if not callable(fixture_factory):
        print("calculator must be decorated with @pytest.fixture", file=sys.stderr)
        return 1

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalculator)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        return 1

    if _run_unittest_mutations():
        return 1

    pytest_tests = [
        "test_add_parametrized",
        "test_subtract_with_fixture",
        "test_divide_by_zero_pytest",
    ]
    node_ids = [f"{__file__}::{name}" for name in pytest_tests]
    if pytest.main([*node_ids, "-q", "-p", "no:cacheprovider"]) != 0:
        print(
            "your pytest tests did not pass; run them with -v to see why",
            file=sys.stderr,
        )
        return 1

    pytest_failure = pytest.fail.Exception
    add_test = globals()["test_add_parametrized"]
    if not any(
        _detects_fault(
            add_test,
            Calculator,
            "add",
            lambda self, a, b: a + b + 1,
            row,
            pytest_failure,
        )
        for row in rows
    ):
        print("test_add_parametrized did not detect an add fault", file=sys.stderr)
        return 1

    fixture = fixture_factory()
    if not _detects_fault(
        globals()["test_subtract_with_fixture"],
        Calculator,
        "subtract",
        lambda self, a, b: a + b,
        (fixture,),
        pytest_failure,
    ):
        print(
            "test_subtract_with_fixture did not detect a subtract fault",
            file=sys.stderr,
        )
        return 1

    if not _detects_fault(
        globals()["test_divide_by_zero_pytest"],
        Calculator,
        "divide",
        lambda self, a, b: 0.0,
        (),
        pytest_failure,
    ):
        print(
            "test_divide_by_zero_pytest did not detect a divide fault", file=sys.stderr
        )
        return 1

    print("\nAll checks passed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
