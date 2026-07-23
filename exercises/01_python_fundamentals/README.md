# 🌱 Exercises: Chapter 1 - Python Fundamentals

Practice problems for
[`lessons/01_python_fundamentals/`](../../lessons/01_python_fundamentals/README.md).
These tasks use only what Chapter 1 teaches: names, core scalar types,
explicit conversions, truthiness, and `assert`. There is no `def`, no
collection literal beyond the incidental values already shown, no import,
and no exception handling in this file -- Chapter 1 has not taught those
yet.

## 🧩 Tasks in `exercises.py`

- **Task 1 - classify values by type:** check four values with
  `isinstance(value, expected_type)` and check the missing value with
  `value is None`.
- **Task 2 - explicit conversions:** convert given text and a given integer
  to `int`, `float`, `str`, and `bool` using the constructor-as-converter
  pattern from the lesson.
- **Task 3 - predict truthiness:** predict `bool(...)` for five values
  (an empty string, the string `"0"`, the integer `0`, `-1`, and `None`)
  before checking your prediction against the real result.

## ▶️ How to work through it

1. Read
   [`lessons/01_python_fundamentals/README.md`](../../lessons/01_python_fundamentals/README.md)
   first.
2. Open `exercises.py`. Each task is a block of top-level statements with
   initial values marked `# TODO`.
3. Replace each marked initial value with the requested expression or value, then
   run the file:

   ```bash
   python exercises/01_python_fundamentals/exercises.py
   ```

4. The first failing `assert` names the incomplete task. Fix it, rerun, and
   repeat. Once every task is complete, the script prints `All checks passed!`.
5. Compare with `solutions.py` if you get stuck or want a second opinion.

## 🔍 Inputs, outputs, and constraints

- Task 1 and Task 3 have no invalid input to guard against; they only check
  that your classification/prediction matches Python's actual behavior.
- Task 2 assumes `quantity_text` and `unit_price_text` are valid numeric
  text, matching what Chapter 1 covers (conversion failures are only
  *described*, not handled, until later in the course).
- Every check in this file is a plain `assert`, exactly as taught in the
  lesson -- there is no hidden test runner.
