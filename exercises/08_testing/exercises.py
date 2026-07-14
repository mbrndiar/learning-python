"""
Exercises: 08 Testing

Write unittest tests for the small `Calculator` class below. This
exercise is about writing tests yourself, not just implementing
functions.
"""

import sys
import unittest


class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    # TODO: write test_add, asserting Calculator().add(2, 3) == 5

    # TODO: write test_subtract, asserting Calculator().subtract(5, 3) == 2

    # TODO: write test_divide_by_zero_raises, asserting that
    # calling divide(1, 0) raises ValueError (use self.assertRaises)


def run_tests():
    required = {"test_add", "test_subtract", "test_divide_by_zero_raises"}
    available = set(unittest.defaultTestLoader.getTestCaseNames(TestCalculator))
    missing = sorted(required - available)
    if missing:
        print(
            "Add the three requested test methods: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalculator)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run_tests())
