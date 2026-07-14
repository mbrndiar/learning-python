# Exercises: Module 7 - Advanced Python

Practice problems for [`lessons/07_advanced_python/`](../../lessons/07_advanced_python/README.md):
decorators, generators/iterators and type hints.

## Tasks in `exercises.py`

- `uppercase_decorator(func)` - write a decorator that upper-cases the
  string returned by the wrapped function.
- `countdown(n)` - write a generator function that `yield`s numbers from
  `n` down to 1.
- `annotate(name: str, age: int) -> str` - add type hints to a function
  signature.
- `repeat(times)` - build a configurable decorator factory.
- `CountUp` - implement the iterator protocol directly.
- `send_welcome(sender, recipient)` - depend on an injected `Protocol`.

## How to work through it

1. Read [`lessons/07_advanced_python/`](../../lessons/07_advanced_python/README.md) first.
2. Open `exercises.py` and implement each piece marked `# TODO`.
3. Run it:

   ```bash
   python exercises/07_advanced_python/exercises.py
   ```

   It prints `All checks passed!` once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.
