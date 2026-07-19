"""
Solutions: 08 Testing
"""

import io
import sys
import unittest
from unittest.mock import Mock, call


class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


def notify_all(sender, recipients, message):
    """Send a message through an injected collaborator."""
    for recipient in recipients:
        sender.send(recipient, message)


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_add(self):
        self.assertEqual(self.calculator.add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(self.calculator.subtract(5, 3), 2)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            self.calculator.divide(1, 0)

    def test_add_examples_with_subtests(self):
        examples = ((2, 3, 5), (-1, -1, -2), (0, 4, 4))
        for a, b, expected in examples:
            with self.subTest(a=a, b=b):
                self.assertEqual(self.calculator.add(a, b), expected)

    def test_notify_all_uses_sender_boundary(self):
        sender = Mock()

        notify_all(sender, ["Ada", "Grace"], "Review the tests")

        self.assertEqual(
            sender.send.call_args_list,
            [
                call("Ada", "Review the tests"),
                call("Grace", "Review the tests"),
            ],
        )


def run_tests():
    required = {
        "test_add",
        "test_subtract",
        "test_divide_by_zero_raises",
        "test_add_examples_with_subtests",
        "test_notify_all_uses_sender_boundary",
    }
    available = set(unittest.defaultTestLoader.getTestCaseNames(TestCalculator))
    missing = sorted(required - available)
    if missing:
        raise RuntimeError(f"Missing expected tests: {', '.join(missing)}")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalculator)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1

    mutations = (
        ("test_add", Calculator, "add", lambda self, a, b: a - b),
        ("test_subtract", Calculator, "subtract", lambda self, a, b: a + b),
        (
            "test_divide_by_zero_raises",
            Calculator,
            "divide",
            lambda self, a, b: 0,
        ),
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

    original_notify_all = notify_all
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


if __name__ == "__main__":
    raise SystemExit(run_tests())
