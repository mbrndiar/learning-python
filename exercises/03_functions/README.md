# 🧩 Exercises: Module 3 - Functions

Practice problems for [`lessons/03_functions/`](../../lessons/03_functions/README.md):
function call contracts, binding, lambdas, closures, and recursion.

## 🛠️ Tasks in `exercises.py`

- `make_multiplier(factor)` - return a closure that multiplies its input
  by `factor`.
- `sum_all(*args)` - sum an arbitrary number of positional arguments.
- `describe(**kwargs)` - build a string from arbitrary keyword arguments.
- `format_label(name, /, *, category)` - satisfy a positional-only and
  keyword-only call contract.
- `record_topic(topics, topic)` - mutate the caller's list and rely on the
  implicit `None` return.
- `factorial(n)` - compute a factorial recursively.

## ▶️ How to work through it

1. Read [`lessons/03_functions/`](../../lessons/03_functions/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/03_functions/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
