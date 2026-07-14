# 🧪 Module 8: Testing

Why automated tests matter, and how to write them with Python's built-in
testing framework.

## 🎯 Learning objectives

After this module, you should be able to define test cases, arrange independent
fixtures, choose precise assertions, test expected failures, and explain what
makes a test suite trustworthy.

## 🔍 Why and what to test

A test executes behavior and compares the observed result with an expectation.
Good tests are deterministic, isolated, readable, and fast enough to run
frequently. Test public behavior rather than private implementation so harmless
refactoring does not break the suite.

Use the arrange–act–assert structure:

```python
class TestCart(unittest.TestCase):
    def test_total_of_two_items(self):
        cart = Cart([10, 5])  # arrange
        total = cart.total()  # act
        self.assertEqual(total, 15)  # assert
```

Cover representative normal cases, boundaries, empty input, and meaningful
failure paths. Coverage can reveal unexecuted code but cannot prove that
assertions are correct or requirements are complete.

A useful narrative for each defect is: first write the smallest example that
demonstrates the unwanted behavior, watch it fail for the expected reason, make
the production change, and keep the example as a regression test. A test that
never failed may still be valid, but seeing the failure guards against testing
the wrong path.

## 🔄 `unittest` lifecycle and assertions

Test methods start with `test_`. `setUp()` runs before each test and
`tearDown()` afterward; each test should receive fresh mutable state. Use
`setUpClass()` only for expensive state that can safely be shared.

Prefer specific assertions such as `assertEqual`, `assertIsNone`,
`assertIn`, `assertAlmostEqual`, and `assertRaises`. To inspect an exception:

```python
with self.assertRaises(ValueError) as context:
    parse_age("-1")
self.assertIn("positive", str(context.exception))
```

Use `subTest()` to report several related examples independently. Mocks replace
collaborators at boundaries such as clocks or network clients; patch the name
where the code under test looks it up, and avoid mocking the behavior actually
being tested.

For example, a notification function should be tested with a mock sender rather
than a real network service. Assert the message sent through that boundary while
leaving the function's own branching and formatting real.

## 📚 Concepts covered

- **`01_unittest_basics.py`** - `unittest`, part of the standard library,
  for writing test cases as classes (`unittest.TestCase`), using
  assertion methods (`assertEqual`, `assertRaises`, etc.), and running
  tests from the command line.

## ▶️ Running

```bash
python lessons/08_testing/01_unittest_basics.py
```

Once you've read through the file, practice what you learned in
[`exercises/08_testing/`](../../exercises/08_testing/README.md).

See also module 9's [`04_pytest_basics.py`](../09_tooling_and_debugging/04_pytest_basics.py)
for examples using the
[pytest](https://docs.pytest.org/en/stable/) testing framework.

## ⚠️ Common mistakes

- Making tests depend on execution order or shared mutable state.
- Asserting only that code ran without checking the result.
- Comparing floats with exact equality.
- Catching an exception manually and letting the test pass if none is raised.
- Mocking so much that the test no longer exercises meaningful behavior.

## ❓ Review questions

1. What do arrange, act, and assert mean?
2. Why should tests be isolated from one another?
3. When is `assertAlmostEqual` preferable to `assertEqual`?
4. What does code coverage fail to tell you?
5. Which collaborator boundaries are good candidates for mocks?
