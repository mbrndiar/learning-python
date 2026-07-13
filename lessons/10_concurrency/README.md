# Module 10: Concurrency

Two complementary approaches to doing more than one thing at a time in
Python.

## Concepts covered

- **`01_threading_and_multiprocessing.py`** - `threading` for running
  multiple threads in one process, best for I/O-bound work (network
  requests, file access) because of the Global Interpreter Lock (GIL);
  and `multiprocessing` for running separate processes, best for
  CPU-bound work since each process has its own interpreter and GIL.
- **`02_asyncio_basics.py`** - `asyncio`, single-threaded cooperative
  concurrency using `async`/`await` and `asyncio.gather`, ideal for many
  I/O-bound tasks running at once without the overhead of threads or
  processes.

## Running

```bash
python lessons/10_concurrency/01_threading_and_multiprocessing.py
python lessons/10_concurrency/02_asyncio_basics.py
```

Once you've read through both files, practice what you learned in
[`exercises/10_concurrency/`](../../exercises/10_concurrency/README.md).

This is the final module - once you're done, try building the
[Task Manager capstone project](../../project/README.md).
