# 🌱 Exercises: Module 1 - Basics

Practice problems for [`lessons/01_basics/`](../../lessons/01_basics/README.md):
variables, conversions, numeric types, operators, text, and binary data.

## 🧩 Tasks in `exercises.py`

- `celsius_to_fahrenheit(celsius)` - convert a temperature using
  arithmetic operators.
- `is_palindrome(text)` - check if a string reads the same forwards and
  backwards, using string methods and slicing.
- `count_vowels(text)` - count vowels in a string by iterating over its
  characters.

## 🔢 Companion numeric and binary exercises

The existing beginner starter remains focused on its original three tasks.
After lessons 1.5 and 1.6, continue with
[`numeric_and_binary_types/exercises.py`](numeric_and_binary_types/exercises.py):

- explicit `int`, `float`, `str`, and `bool` conversions;
- a UTF-8 encode/decode round trip;
- mutation through `bytearray` while preserving the original `bytes`;
- exact decimal multiplication from text;
- exact rational addition with `Fraction`.

Run the companion starter and compare it with its separate solution:

```bash
python exercises/01_basics/numeric_and_binary_types/exercises.py
python exercises/01_basics/numeric_and_binary_types/solutions.py
```

## ▶️ How to work through it

1. Read [`lessons/01_basics/`](../../lessons/01_basics/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/01_basics/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
