"""
Lesson 8.1: Testing with unittest

`unittest` is part of Python's standard library and provides a
framework for writing and running automated tests.
"""

import unittest
from unittest.mock import Mock, call


def add(a, b):
    """The function under test."""
    return a + b


def divide(a, b):
    """Another function under test, which can raise an error."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def notify_all(sender, recipients, message):
    """Send one message through an injected collaborator."""
    for recipient in recipients:
        sender.send(recipient, message)


class TestMathFunctions(unittest.TestCase):
    """A test case groups related tests together as methods.

    Each method starting with `test_` is discovered and run automatically.
    """

    def setUp(self):
        """Runs before every test method. Useful for shared setup."""
        # unittest creates a fresh TestCase instance per method, then calls
        # setUp(). Mutable fixture state therefore does not leak between tests.
        self.sample_numbers = (2, 3)

    def test_add_positive_numbers(self):
        a, b = self.sample_numbers
        self.assertEqual(add(a, b), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

    def test_divide_normal_case(self):
        self.assertAlmostEqual(divide(10, 4), 2.5)

    def test_divide_by_zero_raises(self):
        # assertRaises checks that the expected exception is raised.
        with self.assertRaises(ValueError):
            divide(10, 0)

    def test_true_and_false_assertions(self):
        self.assertTrue(add(1, 1) == 2)
        self.assertFalse(add(1, 1) == 3)

    def test_add_examples_with_subtests(self):
        examples = ((2, 3, 5), (-1, -1, -2), (0, 4, 4))
        for a, b, expected in examples:
            # subTest keeps one failed example from hiding the remaining cases
            # and labels the failure with the supplied parameters.
            with self.subTest(a=a, b=b):
                self.assertEqual(add(a, b), expected)

    def test_notify_all_uses_sender_boundary(self):
        # Replace only the external collaborator. notify_all's real loop and
        # message forwarding still execute, so the test checks useful behavior
        # without performing network or console I/O.
        sender = Mock()

        notify_all(sender, ["Ada", "Grace"], "Review the tests")

        self.assertEqual(
            sender.send.call_args_list,
            [
                call("Ada", "Review the tests"),
                call("Grace", "Review the tests"),
            ],
        )


if __name__ == "__main__":
    # The default exit behavior gives shells and CI a nonzero status when a test
    # fails, so automation cannot mistake a red suite for a successful lesson.
    unittest.main(verbosity=2)
