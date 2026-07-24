# 🧪 Chapter 12: Automated Testing

**Semantic ID:** `module.automated-testing` · **Prerequisites:**
`module.typing-protocols-and-di`

## 📍 Where this fits

Chapters 1-11 built behavior: functions with contracts, classes with
invariants, and collaborators injected through a `Protocol`. This chapter
adds the discipline that keeps that behavior correct as it changes. It is
the first of three tooling chapters (testing here, debugging and CLIs in
Chapter 13, environments and packaging in Chapter 14) and everything after
it — SQL repositories, HTTP servers and clients, the Task project, and
both capstones — is validated by tests written the way this chapter
teaches.

## 🎯 Learning objectives

After this chapter, you should be able to:

- explain what an automated test checks (observable behavior at a
  boundary) and why testing private implementation makes refactoring
  fragile;
- structure any test as arrange-act-assert and keep it deterministic;
- write `unittest.TestCase` classes, use the `setUp`/`tearDown` lifecycle
  for fresh per-test state, and choose precise assertions including
  `assertRaises` and `assertAlmostEqual`;
- report several related examples independently with `subTest`;
- write pytest tests as plain functions with plain `assert`, expect
  exceptions with `pytest.raises`, multiply a case with
  `@pytest.mark.parametrize`, and isolate resources with fixtures such as
  `tmp_path`;
- distinguish a fake, a stub, and a mock; constrain a mock with
  `Mock(spec=...)`; and patch a dependency where the code under test looks
  it up.

## 🧠 Motivation and mental model

A test is ordinary code that arranges a fully determined input, calls one
behavior, and asserts on the observable result. Its value is entirely
about trust: a suite you trust lets you change code confidently, and a
suite you do not trust is worse than none because it produces false
confidence. Trust comes from two habits. First, assert on behavior a
caller can observe (return values, raised exceptions, messages sent to a
collaborator) rather than on private implementation, so that a harmless
refactor does not turn the suite red. Second, remove every source of
nondeterminism — clocks, randomness, network, filesystem, iteration order
— so a passing test stays passing for the right reason.

`unittest` and pytest are two frameworks for the same idea. `unittest`
ships with Python and expresses tests as classes with explicit assertion
methods; pytest is a third-party tool that expresses tests as plain
functions with plain `assert` and adds parameterization and fixtures.
Both run the same arrange-act-assert structure.

## 1️⃣ The testing mental model and determinism

A test is ordinary code: it arranges a fully determined input, performs
one action, and asserts on the observable result. Written by hand, with
no framework at all, that arrange-act-assert (AAA) shape is obvious --
frameworks in the next three concepts remove boilerplate but never change
this structure. A boundary or failure path deserves its own case, not just
the happy path, and every source of nondeterminism (the clock, randomness,
the network, dict/set iteration order) must be removed or normalized, or a
passing test can fail tomorrow with no code change.

```python
def average(values: Sequence[float]) -> float:
    """Return the arithmetic mean, raising ValueError for empty input."""
    if not values:
        raise ValueError("average() needs at least one value")
    return sum(values) / len(values)


def check_average_rejects_empty() -> None:
    try:
        average([])
    except ValueError:
        return  # the promised behavior happened
    raise AssertionError("average([]) should have raised ValueError")
```

```text
Running arrange-act-assert checks by hand (no framework yet):
  PASSED: check_average_of_two_values
  PASSED: check_average_rejects_empty
  PASSED: check_distinct_sorted_is_deterministic
```

`check_average_rejects_empty` is itself hand-written test code -- no
framework runs it here, so a failed assertion inside it is just an
ordinary `AssertionError` propagating out of `main()`, exactly like any
other bug. None of the three checks assert that `average()` uses `sum()`
and `len()` internally; that stays free to change.

Run the complete companion (a runnable script, not a pytest file):

```bash
python lessons/12_testing/01_testing_mental_model.py
```

See [`01_testing_mental_model.py`](01_testing_mental_model.py) for the
full sequence, including `distinct_sorted`, which sorts a set before
asserting so the result no longer depends on the set's arbitrary
iteration order.

> **Try one change:** change `average`'s empty-input branch from
> `raise ValueError(...)` to `return 0.0`. Predict what
> `check_average_rejects_empty` does next: it no longer sees a
> `ValueError`, so it falls through to
> `raise AssertionError("average([]) should have raised ValueError")`.
> This one check is not just covering an edge case -- it is the single
> place `average`'s actual contract ("raises `ValueError` when there is
> nothing to average") is pinned down; remove the raise and the test
> itself reports that the contract broke.

## 2️⃣ The unittest lifecycle and assertions

`unittest.TestCase` methods named `test_*` are discovered automatically,
and unittest builds a **fresh instance per test method**, calling
`setUp()` before it and `tearDown()` after -- even on failure. Because
`self.cart` is rebuilt from scratch in `setUp()` on that new instance, one
test's mutations can never leak into the next; this is what makes tests
safe to run in any order. Prefer specific assertions (`assertEqual`,
`assertIn`) over a bare `assertTrue(a == b)`, since they report both
values on failure, and always compare floats with `assertAlmostEqual`
rather than `assertEqual`.

```python
class TestCart(unittest.TestCase):
    def setUp(self) -> None:
        # Runs before each test_* method. Each test gets its own Cart.
        self.cart = Cart()

    def test_total_uses_almost_equal_for_floats(self) -> None:
        self.cart.add(0.1)
        self.cart.add(0.2)
        self.assertAlmostEqual(self.cart.total(), 0.3)

    def test_negative_price_is_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            self.cart.add(-1.0)
        self.assertIn("negative", str(caught.exception))
```

```text
test_empty_cart_total_is_zero (__main__.TestCart.test_empty_cart_total_is_zero) ... ok
test_negative_price_is_rejected (__main__.TestCart.test_negative_price_is_rejected) ... ok
test_running_totals_with_subtests (__main__.TestCart.test_running_totals_with_subtests) ... ok
test_total_of_two_items (__main__.TestCart.test_total_of_two_items) ... ok
test_total_uses_almost_equal_for_floats (__main__.TestCart.test_total_uses_almost_equal_for_floats) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```

`verbosity=2` prints one line per test method; `unittest.main()` exits
nonzero on any failure, so a shell or CI sees a red suite as a failure
instead of mistaking it for a normal exit.

Run the complete companion (a runnable script whose own `unittest.main()`
call performs discovery):

```bash
python lessons/12_testing/02_unittest_lifecycle_and_assertions.py
```

See
[`02_unittest_lifecycle_and_assertions.py`](02_unittest_lifecycle_and_assertions.py)
for the full sequence, including `test_running_totals_with_subtests`,
where `subTest` reports each row of a loop independently instead of
stopping at the first failure.

> **Try one change:** change `Cart.total` to `return sum(self.prices) +
> 1`. Predict which tests fail: `test_total_of_two_items`,
> `test_empty_cart_total_is_zero`, and
> `test_total_uses_almost_equal_for_floats` each report a specific
> expected-vs-actual mismatch, while `test_negative_price_is_rejected`
> (which never checks the total) keeps passing -- each assertion tests
> exactly one behavior.

## 3️⃣ Pytest assertions, parameterization, and fixtures

pytest collects any function named `test_*` -- no base class required --
and rewrites a plain `assert` to show both operands on failure.
`@pytest.mark.parametrize` runs one test body once per row and reports
each row as a *separate* result, unlike a `for` loop, which would stop at
the first failing row and hide the rest. A `@pytest.fixture` function
supplies input to any test naming it as a parameter; `tmp_path` is a
built-in fixture giving each test its own empty directory, so
filesystem-touching tests stay isolated and deterministic.

```python
@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(2, 3, 5), (-1, -1, -2), (0, 5, 5)],
)
def test_add_examples(a: int, b: int, expected: int) -> None:
    assert add(a, b) == expected


def test_write_report_uses_isolated_directory(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"
    write_report(report, [3, 5])
    assert report.read_text(encoding="utf-8") == "3\n5\n"
```

```text
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_add_returns_sum PASSED
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_divide_by_zero_raises PASSED
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_add_examples[2-3-5] PASSED
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_add_examples[-1--1--2] PASSED
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_add_examples[0-5-5] PASSED
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_fixture_supplies_values PASSED
lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py::test_write_report_uses_isolated_directory PASSED

============================== 7 passed in 0.02s ===============================
```

`parametrize` expanded `test_add_examples` into three separately named
cases (`[2-3-5]`, `[-1--1--2]`, `[0-5-5]`) instead of one.

This file must be **run by pytest, not directly with `python`**. It does
have an `if __name__ == "__main__":` guard, but that guard only hands the
file to `pytest.main([__file__, "-v"])` -- the collector and reporter are
always pytest's, never a hand-rolled runner. Use the exact command:

```bash
python -m pytest lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py -v
```

See
[`03_pytest_assertions_parameterization_and_fixtures.py`](03_pytest_assertions_parameterization_and_fixtures.py)
for the full sequence, including `test_divide_by_zero_raises`, which uses
`pytest.raises(ValueError, match="zero")`.

> **Try one change:** edit the `parametrize` row `(2, 3, 5)` to a wrong
> expected value, e.g. `(2, 3, 6)`, and rerun the exact command above.
> Predict the result: only `test_add_examples[2-3-6]` reports FAILED, with
> the rewritten `assert` showing both operands; the other cases stay
> green -- a `for` loop over the same rows inside one test body would
> instead stop entirely at the first failing row.

## 4️⃣ Test doubles and mocking

A **fake** is a small working implementation with state you can inspect
afterward; a **stub** returns a fixed answer and records nothing; a
**mock** records every call so a test can assert on *how* a collaborator
was used. `Mock(spec=RealClass)` constrains a mock to the real interface
-- accessing a method the real class does not have raises
`AttributeError` instead of silently succeeding. `unittest.mock.patch`
replaces a name exactly **where it is looked up**, as a context manager
that always restores the original afterward, even if the block raises.

```python
def demonstrate_mock_with_spec() -> None:
    gateway = Mock(spec=EmailGateway)
    gateway.send.return_value = "receipt-42"

    receipt = notify_signup(gateway, "lin@example.com")

    gateway.send.assert_called_once_with(
        to="lin@example.com", subject="Welcome", body="Thanks for signing up."
    )
    assert gateway.send.call_args_list == [
        call(to="lin@example.com", subject="Welcome", body="Thanks for signing up.")
    ]


def demonstrate_patch_where_looked_up() -> None:
    with patch(
        f"{__name__}.read_setting", return_value="Release Notes"
    ) as fake_setting:
        assert build_banner() == "== Release Notes =="
        fake_setting.assert_called_once_with("title")
```

```text
fake recorded one message; stub returned its canned receipt
Mock(spec=...) rejected a method the real class does not have
patched read_setting only within the with-block, then restored it
```

`gateway.send.call_args_list` verifies the exact keyword arguments
`notify_signup` passed at the boundary; outside the `with` block,
`read_setting` is restored automatically, so later code (and later tests)
see the real function again.

Run the complete companion:

```bash
python lessons/12_testing/04_test_doubles_and_mocking.py
```

See
[`04_test_doubles_and_mocking.py`](04_test_doubles_and_mocking.py) for the
full sequence, including `demonstrate_fake_and_stub`, which contrasts a
`FakeEmailGateway`'s recorded state with a `StubEmailGateway`'s canned
receipt.

> **Try one change:** change the `patch` target in
> `demonstrate_patch_where_looked_up` from `f"{__name__}.read_setting"` to
> a wrong location, e.g. `"builtins.read_setting"`. Predict the result:
> `patch` itself raises `AttributeError` before the test body even runs,
> because no `read_setting` attribute exists there -- confirming the rule
> that you patch where a name is *looked up* (`build_banner`'s own
> module), never where it merely happens to be *defined*.

## 🔁 Transition ahead

Chapter 13 uses these tests as the safety net while you learn to diagnose
failures with tracebacks and `pdb` and to build `argparse` command-line
boundaries. From here on, every new behavior in the course is accompanied
by a test, and the Task project and capstones are graded by pytest and
unittest suites that follow exactly the structure introduced here.

## ⚠️ Common mistakes

- Asserting only that code ran (`assertTrue(result)`) instead of checking
  the actual value.
- Comparing floating-point results with `assertEqual` instead of
  `assertAlmostEqual`.
- Letting tests share mutable state or depend on execution order.
- Catching an exception by hand and letting the test pass when nothing was
  raised, instead of using `assertRaises`/`pytest.raises`.
- Depending on the clock, randomness, the network, or dictionary/set
  iteration order, which makes a test flaky.
- Patching where a name is *defined* rather than where the code under test
  *looks it up*.
- Using an unconstrained `Mock` so a misspelled method silently succeeds;
  prefer `Mock(spec=...)`.

## 🧾 Summary

- A trustworthy test asserts on observable behavior, follows
  arrange-act-assert, and is fully deterministic.
- `unittest` expresses tests as `TestCase` classes with a per-test
  lifecycle and precise assertion methods, including `assertRaises` and
  `subTest`.
- pytest expresses tests as functions with plain `assert`, plus
  `pytest.raises`, `@pytest.mark.parametrize`, and fixtures such as
  `tmp_path`.
- Fakes, stubs, and mocks are different tools; `Mock(spec=...)` constrains
  a mock to a real interface, and `patch` replaces a name where it is
  looked up.

## ❓ Review questions (closed notes)

1. What should a test assert on, and what should it avoid asserting on, so
   that refactoring stays safe?
2. Why must a test be deterministic, and what are three common sources of
   nondeterminism?
3. What runs before and after each `unittest` test method, and why is a
   fresh instance created per test?
4. When do you use `assertAlmostEqual` instead of `assertEqual`, and why?
5. How does `@pytest.mark.parametrize` differ from a `for` loop inside one
   test?
6. What is the difference between a fake, a stub, and a mock?
7. What does `Mock(spec=SomeClass)` add, and where must you point `patch`?

## 📚 Authoritative references

- [`unittest` — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [`unittest.mock` — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [pytest documentation](https://docs.pytest.org/en/stable/)
- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/12_testing/`](../../exercises/12_testing/README.md).
