# ⚡ Exercises: Module 12 - Concurrency

Practice problems for [`lessons/12_concurrency/`](../../lessons/12_concurrency/README.md):
threading, multiprocessing and asyncio.

## 🧩 Tasks in `exercises.py`

- `run_in_threads(func, items)` - run `func(item)` for every item
  concurrently using `threading.Thread`, collecting results in order.
- `fetch_all(values)` - run the given `fetch` coroutine concurrently for
  every value using `asyncio.gather`, collecting results in order.
- `fetch_all_limited(values, limit)` - bound fan-out with a semaphore.
- `fetch_with_timeout(...)` - apply a finite timeout and observe cancellation.

The thread exercise must also propagate worker exceptions to the caller.

## ▶️ How to work through it

1. Read [`lessons/12_concurrency/`](../../lessons/12_concurrency/README.md) first.
2. Open `exercises.py` and implement each function marked `# TODO`.
3. Run it:

   ```bash
   python exercises/12_concurrency/exercises.py
   ```

   It prints `OK` for each check once everything is implemented
   correctly.
4. Compare with `solutions.py` if you get stuck or want a second opinion.

This is the final optional exercise module. These exercises prepare you to
evaluate process contention in the comparative capstone and bounded threads in
the idiomatic capstone:

[Two required capstones](../../capstones/README.md).
