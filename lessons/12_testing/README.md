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

## 🧩 Progressive syntax and mechanism

1. **Arrange-act-assert.** Every test, in any framework, arranges input,
   performs one action, and asserts on the observable result.
2. **`unittest.TestCase`.** Methods named `test_*` are discovered
   automatically; a fresh instance is built per method.
3. **Lifecycle hooks.** `setUp()` runs before each test and `tearDown()`
   after each (even on failure); `setUpClass()` exists only for expensive
   state that is safe to share.
4. **Precise assertions.** `assertEqual`, `assertIn`, `assertIsNone`, and
   `assertAlmostEqual` report better failures than a bare `assertTrue`;
   compare floats with `assertAlmostEqual`.
5. **Expected exceptions.** `with self.assertRaises(ValueError) as caught:`
   verifies the failure path and lets you assert on the message.
6. **`subTest`.** Reports each example in a loop independently so one
   failure does not hide the rest.
7. **pytest functions and `assert`.** Any `test_*` function is collected;
   pytest rewrites `assert` to show both operands on failure.
8. **`pytest.raises`.** The pytest equivalent of `assertRaises`, with a
   `match=` regular expression for the message.
9. **`@pytest.mark.parametrize`.** Runs one test body once per row and
   reports each row separately.
10. **Fixtures.** A function decorated with `@pytest.fixture` supplies
    input to any test that names it as a parameter; `tmp_path` is a
    built-in fixture giving each test an isolated directory.
11. **Test doubles.** A *fake* is a working lightweight implementation, a
    *stub* returns canned answers, and a *mock* records interactions for
    verification. `Mock(spec=RealClass)` rejects attributes the real class
    lacks. `unittest.mock.patch("module.name")` replaces a name where it
    is looked up and restores it afterward.

## 📖 Read-predict-run-modify workflow

Read each file top to bottom, predict its output, then run it. Note that
Lesson 3 is designed to be run *by pytest*:

```bash
python lessons/12_testing/01_testing_mental_model.py
python lessons/12_testing/02_unittest_lifecycle_and_assertions.py
python -m pytest lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py -v
python lessons/12_testing/04_test_doubles_and_mocking.py
```

### Expected output highlights

- `01_testing_mental_model.py`: three by-hand arrange-act-assert checks
  pass, including a boundary case (`average([])` raises `ValueError`) and
  a deterministic case (a sorted set of strings).
- `02_unittest_lifecycle_and_assertions.py`: `Ran 5 tests ... OK`, with
  the `subTest` case ready to label each running-total row independently if
  one fails.
- `03_...fixtures.py`: pytest reports `7 passed`, expanding the
  parameterized `test_add_examples` into three separately named cases.
- `04_test_doubles_and_mocking.py`: the fake records one message, the stub
  returns its canned receipt, `Mock(spec=...)` rejects a method the real
  class does not have, and the patched setting is restored after the
  `with` block.

Then modify something and predict the new result: break `Cart.total` to
return `sum(self.prices) + 1` and watch exactly which unittest assertions
fail; change a `parametrize` row so it is wrong and confirm only that case
turns red.

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
