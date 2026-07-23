# 🔁 Exercises: Chapter 10 - Iteration, Decorators, and Contexts

**Prerequisites:** completed
[`lessons/10_iteration_decorators_and_contexts/`](../../lessons/10_iteration_decorators_and_contexts/README.md).

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/10_iteration_decorators_and_contexts/exercises.py

# Compile-check without running:
python -m py_compile exercises/10_iteration_decorators_and_contexts/exercises.py

# Check the reference solution:
python exercises/10_iteration_decorators_and_contexts/solutions.py
```

## Tasks

1. **`CountUp`** - implement the iterator protocol (`__iter__`/
   `__next__`) directly, raising `StopIteration` once the range is
   exhausted.
2. **`countdown(start)`** - a generator function using `yield`, ending
   with `"Liftoff!"`.
3. **`uppercase(func)`** - a decorator that upper-cases the wrapped
   function's string result, using `functools.wraps`.
4. **`repeat(times)`** - a decorator factory whose decorated function
   returns a list of `times` repeated results, also using
   `functools.wraps`.
5. **`temporary_value(mapping, key, value)`** - a generator-based
   context manager (`@contextlib.contextmanager`) that restores a
   dict's previous state afterward, on both success and failure.

## Constraints

- Each starter initially raises `NotImplementedError`, so the checks stop
  at the first incomplete task with a focused traceback.
- Both decorators must use `functools.wraps` -- the checks assert
  `__name__` is preserved, not just that the return value is correct.
- `temporary_value` must use `try`/`finally` around a single `yield`, not
  a class-based context manager.

## Edge cases exercised

- `CountUp(2, 2)` (an empty range) is checked to raise `StopIteration` on
  the very first `next()` call.
- `temporary_value` is checked on three scenarios: a key that existed
  before (restored to its old value on success), the same key when the
  `with` block raises (still restored, and the exception still
  propagates), and a key that did *not* exist before (removed entirely
  afterward, not left with a placeholder).
- `repeat`'s decorated function is checked for both its return value
  (a list of repeated results) and its preserved `__name__`.
