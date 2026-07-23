# 🔤 Exercises: Chapter 2 - Text and Numbers

Practice problems for
[`lessons/02_text_and_numbers/`](../../lessons/02_text_and_numbers/README.md).
Like Chapter 1's exercises, this file uses only top-level statements -- no
`def` yet -- plus the operators, string methods, encoding, and numeric types
from this chapter's lessons.

## 🧩 Tasks in `exercises.py`

- **Task 1 - Celsius to Fahrenheit:** convert two given temperatures using
  `F = C * 9/5 + 32`.
- **Task 2 - palindrome check:** decide whether two given words read the
  same forwards and backwards, case-insensitively, using slicing.
- **Task 3 - UTF-8 round trip:** encode a given accented string as UTF-8 and
  decode it back.
- **Task 4 - exact decimal total:** multiply an exact `Decimal` unit price
  by a quantity, built directly from text.
- **Task 5 - exact fraction addition:** parse and add two rational strings
  with `Fraction`.
- **Task 6 - formatted receipt line:** combine alignment and fixed-precision
  format specifiers in one f-string.

## ▶️ How to work through it

1. Read
   [`lessons/02_text_and_numbers/README.md`](../../lessons/02_text_and_numbers/README.md)
   first.
2. Open `exercises.py` and replace every initial value marked `# TODO`.
3. Run it:

   ```bash
   python exercises/02_text_and_numbers/exercises.py
   ```

4. The first failing `assert` names the incomplete task. Fix it, rerun, and
   repeat until you see `All checks passed!`.
5. Compare with `solutions.py` if you get stuck.

## 🔍 Inputs, outputs, and constraints

- Task 1 inputs are already valid numbers; no conversion failure to guard.
- Task 2 and Task 3 use different words/text than the lesson examples, so
  copying the lesson's exact code will not satisfy the assertions unless you
  adapt it to these inputs.
- Task 4 must construct `Decimal` from the given text directly (not via
  `float`), or the exact-total assertion can fail due to binary floating
  point approximation.
- Task 6 checks both the exact formatted string and its total length (20
  characters), so both the left alignment width (12) and the right
  alignment/precision width (8, with 2 decimals) must be correct.
