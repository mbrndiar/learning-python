"""
Solutions: 08 Testing
"""

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

    def test_add(self):
        self.assertEqual(self.calculator.add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(self.calculator.subtract(5, 3), 2)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            self.calculator.divide(1, 0)


def run_tests():
    required = {"test_add", "test_subtract", "test_divide_by_zero_raises"}
    available = set(unittest.defaultTestLoader.getTestCaseNames(TestCalculator))
    missing = sorted(required - available)
    if missing:
        raise RuntimeError(f"Missing expected tests: {', '.join(missing)}")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalculator)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run_tests())
