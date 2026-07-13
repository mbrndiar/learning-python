# Exercises: Module 5 - Modules and Files

Practice problems for [`lessons/05_modules_and_files/`](../../lessons/05_modules_and_files/README.md):
modules, file I/O, exceptions, custom exceptions and context managers.

## Tasks in `exercises.py`

- `write_lines(path, lines)` / `read_lines(path)` - write a list of
  strings to a file and read them back, using `open()` and the `with`
  statement.
- `safe_divide(a, b)` - divide two numbers, handling `ZeroDivisionError`
  with `try`/`except`.
- `withdraw(balance, amount)` - raise a custom exception when a
  withdrawal exceeds the available balance.

## How to work through it

1. Read [`lessons/05_modules_and_files/`](../../lessons/05_modules_and_files/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/05_modules_and_files/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
