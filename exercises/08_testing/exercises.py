"""
Exercises: 08 Testing

Write unittest tests for the small `Calculator` class below. This
exercise is about writing tests yourself, not just implementing
functions.
"""

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

    # TODO: write test_add, asserting Calculator().add(2, 3) == 5

    # TODO: write test_subtract, asserting Calculator().subtract(5, 3) == 2

    # TODO: write test_divide_by_zero_raises, asserting that
    # calling divide(1, 0) raises ValueError (use self.assertRaises)

    # TODO: write test_add_examples_with_subtests. Loop over several
    # (a, b, expected) examples and use self.subTest(a=a, b=b) so one failing
    # example does not hide the others.

    # TODO: write test_notify_all_uses_sender_boundary. Use Mock as the sender,
    # call notify_all for two recipients, and compare sender.send.call_args_list
    # with the expected call(...) values.


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
        print(
            "Add the requested test methods: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalculator)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run_tests())
