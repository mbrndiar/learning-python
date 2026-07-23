# 🧪 Exercises: Chapter 12 - Automated Testing

Practice problems for
[`lessons/12_testing/`](../../lessons/12_testing/README.md). Unlike most
chapters, this exercise is about writing *tests* yourself in both
frameworks, not implementing production functions.

Install the development dependencies first (pytest is required) by
following [`docs/SETUP.md`](../../docs/SETUP.md).

## 🧩 Tasks in `exercises.py`

A small `Calculator` class and a `notify_all` collaborator function are
supplied. Add:

**unittest methods on `TestCalculator`:**

- `test_add` — assert `Calculator().add(2, 3) == 5`.
- `test_subtract` — assert `Calculator().subtract(5, 3) == 2`.
- `test_divide_by_zero_raises` — assert `divide(1, 0)` raises `ValueError`
  (use `self.assertRaises`).
- `test_add_examples_with_subtests` — check several additions with
  `self.subTest(...)` so each example is reported independently.
- `test_notify_all_uses_sender_boundary` — inject a `Mock(spec=...)` sender
  and assert on `sender.send.call_args_list`.

**pytest functions:**

- `test_add_parametrized` — decorated with `@pytest.mark.parametrize` over
  at least three `(a, b, expected)` rows.
- a `calculator` fixture plus `test_subtract_with_fixture(calculator)`.
- `test_divide_by_zero_pytest` — using `pytest.raises(ValueError,
  match="zero")`.

## ▶️ How to work through it

1. Read [`lessons/12_testing/`](../../lessons/12_testing/README.md) first.
2. Open `exercises.py` and add each test marked `# TODO`. You will need to
   `import pytest` for the pytest tasks.
3. Run the evaluator from the repository root:

   ```bash
   python exercises/12_testing/exercises.py
   ```

   It first reports any missing tests, then runs your unittest and pytest
   tests,    and finally replaces each `Calculator` method in memory with a deliberately
   faulty version to confirm your assertions would catch a real bug. It
   prints `All checks passed!` only when every test is present, passing,
   and mutation-sensitive.
4. To watch your pytest tests directly:

   ```bash
   python -m pytest exercises/12_testing/exercises.py -v
   ```

5. Compare with `solutions.py` if you get stuck.

## ⚠️ Why the evaluator injects faults

A test that never fails proves nothing. The evaluator temporarily replaces
one `Calculator` method with a wrong implementation and expects the matching
test to turn red. If a "test" passes even against the broken code, it is not
really testing behavior — tighten its assertion. It also checks that the
parameterized test declares at least three rows, the fixture is a real
`@pytest.fixture`, and the collaborator mock is constrained by
`MessageSender`.
