# 📦 Exercises: Module 5 - Modules and Files

Practice problems for [`lessons/05_modules_and_files/`](../../lessons/05_modules_and_files/README.md):
modules and packages, paths and directories, file I/O, date/time, JSON,
exceptions, custom exceptions, and context managers.

## 🧩 Tasks in `exercises.py`

- `write_lines(path, lines)` / `read_lines(path)` - write a list of
  strings to a file and read them back, using `open()` and the `with`
  statement.
- `write_bytes(path, data)` / `read_bytes(path)` - preserve exact byte content
  with binary `wb`/`rb` modes and no text encoding.
- `safe_divide(a, b)` - divide two numbers, handling `ZeroDivisionError`
  with `try`/`except`.
- `withdraw(balance, amount)` - reject non-positive withdrawals and raise a
  custom exception when a withdrawal exceeds the available balance.
- `save_json(path, data)` / `load_json(path)` - persist structured data.
- `temporary_value(mapping, key, value)` - implement deterministic cleanup
  with `@contextmanager`.
- `describe_greeting(name)` - practice absolute imports by importing `hello`
  from `example_package.greetings` and returning the result.
- `directory_inventory(root)` - recursively classify descendants and return
  deterministic relative paths plus file sizes.
- `parse_timestamp_to_utc(text)` - parse an aware ISO 8601 value, reject a
  naive timestamp, and normalize the represented instant to UTC.

## ▶️ How to work through it

1. Read [`lessons/05_modules_and_files/`](../../lessons/05_modules_and_files/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/05_modules_and_files/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
