# 🧪 Exercises: Module 8 - Testing

Practice problems for [`lessons/08_testing/`](../../lessons/08_testing/README.md):
testing with `unittest`.

## 🧩 Tasks in `exercises.py`

Unlike the other modules, this exercise is about writing tests
yourself, not implementing functions. A small `Calculator` class is
given; add test methods to `TestCalculator`:

- `test_add` - assert `Calculator().add(2, 3) == 5`.
- `test_subtract` - assert `Calculator().subtract(5, 3) == 2`.
- `test_divide_by_zero_raises` - assert that `divide(1, 0)` raises
  `ValueError` (use `self.assertRaises`).

## ▶️ How to work through it

1. Read [`lessons/08_testing/`](../../lessons/08_testing/README.md) first.
2. Open `exercises.py` and implement each test method marked `# TODO`.
3. Run it:

   ```bash
   python exercises/08_testing/exercises.py
   ```

   `unittest` reports which tests passed or failed.
   If the methods are still missing, the exercise exits with an instruction
   instead of reporting the misleading result `Ran 0 tests ... OK`.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
