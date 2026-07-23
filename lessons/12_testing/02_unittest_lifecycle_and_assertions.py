"""
Chapter 12, Lesson 2: The unittest Lifecycle and Assertions

Purpose: write test cases with the standard-library `unittest` framework;
understand the per-test lifecycle (`setUp`/`tearDown`, and `setUpClass`
for expensive shared state); choose precise assertions; test expected
exceptions; and report several related examples independently with
`subTest`.

Prerequisites: Lesson 1 (arrange-act-assert and determinism) and Chapter
9 classes. `unittest` ships with Python, so nothing needs installing.

Run this file directly; `unittest.main()` discovers and runs the cases:

    python lessons/12_testing/02_unittest_lifecycle_and_assertions.py
"""

import unittest


# Step 1: the code under test.
class Cart:
    """A tiny shopping cart used to demonstrate the unittest lifecycle."""

    def __init__(self) -> None:
        self.prices: list[float] = []

    def add(self, price: float) -> None:
        if price < 0:
            raise ValueError("price must not be negative")
        self.prices.append(price)

    def total(self) -> float:
        return sum(self.prices)


# Step 2: a test case is a class subclassing unittest.TestCase. Every
# method named test_* is discovered and run. unittest builds a *fresh*
# TestCase instance per method and then calls setUp(), so mutable fixture
# state created in setUp() cannot leak from one test into another.
class TestCart(unittest.TestCase):
    def setUp(self) -> None:
        # Runs before each test_* method. Each test gets its own Cart.
        self.cart = Cart()

    def tearDown(self) -> None:
        # Runs after each test, even if it failed. Use it to release
        # resources; here there is nothing to clean up, so it only
        # documents the lifecycle hook.
        self.cart.prices.clear()

    # Step 3: prefer specific assertions. assertEqual reports both values
    # on failure, which is far more useful than assertTrue(a == b).
    def test_total_of_two_items(self) -> None:
        self.cart.add(10.0)
        self.cart.add(5.0)
        self.assertEqual(self.cart.total(), 15.0)

    def test_empty_cart_total_is_zero(self) -> None:
        self.assertEqual(self.cart.total(), 0.0)

    # Step 4: floating-point results are compared with assertAlmostEqual,
    # never assertEqual, because binary floats rarely land on an exact
    # decimal value.
    def test_total_uses_almost_equal_for_floats(self) -> None:
        self.cart.add(0.1)
        self.cart.add(0.2)
        self.assertAlmostEqual(self.cart.total(), 0.3)

    # Step 5: test an expected exception with assertRaises as a context
    # manager. Capturing the exception lets you also assert on its message
    # so a different ValueError cannot silently satisfy the test.
    def test_negative_price_is_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.cart.add(-1.0)
        self.assertIn("negative", str(caught.exception))

    # Step 6: subTest reports several related examples independently. A
    # plain for-loop would stop at the first failing row and hide the
    # rest; subTest labels each row and keeps going.
    def test_running_totals_with_subtests(self) -> None:
        examples = (
            ([1.0], 1.0),
            ([1.0, 2.0], 3.0),
            ([1.0, 2.0, 3.0], 6.0),
        )
        for prices, expected in examples:
            with self.subTest(prices=prices):
                cart = Cart()
                for price in prices:
                    cart.add(price)
                self.assertEqual(cart.total(), expected)


if __name__ == "__main__":
    # verbosity=2 prints one line per test. unittest.main() exits nonzero
    # when any test fails, so CI and shells see a red suite as a failure
    # rather than mistaking it for a successful script.
    unittest.main(verbosity=2)
