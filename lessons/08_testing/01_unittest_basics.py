"""
Lesson 8.1: Testing with unittest

`unittest` is part of Python's standard library and provides a
framework for writing and running automated tests.
"""

import unittest


def add(a, b):
    """The function under test."""
    return a + b


def divide(a, b):
    """Another function under test, which can raise an error."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class TestMathFunctions(unittest.TestCase):
    """A test case groups related tests together as methods.

    Each method starting with `test_` is discovered and run automatically.
    """

    def setUp(self):
        """Runs before every test method. Useful for shared setup."""
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


if __name__ == "__main__":
    # `unittest.main()` discovers and runs all TestCase methods in this
    # file. `exit=False` lets the script continue instead of exiting the
    # interpreter, which keeps this consistent with the other runnable
    # lessons in this repository.
    unittest.main(verbosity=2, exit=False)
