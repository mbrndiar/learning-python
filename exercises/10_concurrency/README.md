# Exercises: Module 10 - Concurrency

Practice problems for [`lessons/10_concurrency/`](../../lessons/10_concurrency/README.md):
threading, multiprocessing and asyncio.

## Tasks in `exercises.py`

- `run_in_threads(func, items)` - run `func(item)` for every item
  concurrently using `threading.Thread`, collecting results in order.
- `fetch_all(values)` - run the given `fetch` coroutine concurrently for
  every value using `asyncio.gather`, collecting results in order.

## How to work through it

1. Read [`lessons/10_concurrency/`](../../lessons/10_concurrency/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/10_concurrency/exercises.py
   ```

   It prints `OK` for each check once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.

This is the final exercise module - once you're done, try building the
[Task Manager capstone project](../../project/README.md).
