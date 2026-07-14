# ⚡ Module 11: Concurrency

Two complementary approaches to doing more than one thing at a time in
Python.

## 🎯 Learning objectives

After this module, you should be able to distinguish concurrency from
parallelism, identify I/O- and CPU-bound workloads, select threads, processes,
or asyncio, and recognize shared-state hazards.

## 🔀 Concurrency, parallelism, and workload

Concurrency means multiple tasks make progress during overlapping periods;
parallelism means work literally executes at the same instant. First determine
whether a program waits mostly for external I/O or spends time computing.
Concurrency adds scheduling, coordination, cancellation, and debugging costs,
so sequential code is the best default when it is fast enough.

For example, a program that waits for ten independent HTTP responses may benefit
from overlap. A program that adds ten small numbers will probably become slower
after adding workers. Start from the wait or bottleneck you can name, not from a
desire to make the code "concurrent."

## 🧵 Threads and processes

Threads share a process's memory, making communication convenient and data
races possible. A lock protects an invariant involving shared mutable state;
thread-safe queues are often clearer than sharing collections directly. In
traditional GIL-enabled CPython builds, the Global Interpreter Lock generally
prevents multiple threads from executing Python bytecode in parallel, but
threads still overlap blocking I/O. Free-threaded CPython builds change that
execution constraint, not the need to protect shared mutable state. Never treat
the GIL as a synchronization strategy.

Processes have separate memory and interpreters, allowing CPU-bound Python work
to run in parallel across cores. Data sent between processes must be
serialized, startup is more expensive, and worker entry points need a
`__main__` guard—especially on platforms that start fresh interpreter
processes.

## 🌊 Asyncio

`asyncio` runs coroutines cooperatively on an event loop. A coroutine yields
control at `await`, so one coroutine that performs blocking work can freeze all
others. Use asynchronous libraries for network and file-like operations, or
offload unavoidable blocking calls:

```python
results = await asyncio.gather(fetch("a"), fetch("b"))
```

Creating a coroutine object does not schedule it. `await` executes it as part
of the current task; `asyncio.create_task()` schedules it independently.
Tasks should have clear ownership, error handling, cancellation, and cleanup.
Limit fan-out with queues or semaphores rather than creating unbounded work.

An owned task is one whose result or failure somebody will observe. If the
caller no longer needs it, cancel it and still await it so cleanup can finish.
Do not create background tasks and forget them: their exceptions can otherwise
surface far from the code that started the operation.

## 🧭 Choosing a model

| Situation | Good starting point |
| --- | --- |
| Few quick operations | sequential code |
| Blocking I/O with synchronous libraries | threads |
| CPU-heavy pure Python | processes |
| Many concurrent operations with async libraries | `asyncio` |

Measure before and after. Workload size, library behavior, serialization, and
deployment constraints can change the answer.

## 📚 Concepts covered

- **`01_threading_and_multiprocessing.py`** - `threading` for running
  multiple threads in one process, often useful for blocking I/O; and
  `multiprocessing` for isolated worker processes that can run CPU-bound Python
  across cores. Traditional GIL-enabled and free-threaded CPython builds have
  different thread execution characteristics.
- **`02_asyncio_basics.py`** - `asyncio`, single-threaded cooperative
  concurrency using `async`/`await` and `asyncio.gather`, ideal for many
  I/O-bound tasks running at once without the overhead of threads or
  processes.

## ▶️ Running

```bash
python lessons/11_concurrency/01_threading_and_multiprocessing.py
python lessons/11_concurrency/02_asyncio_basics.py
```

Once you've read through both files, practice what you learned in
[`exercises/11_concurrency/`](../../exercises/11_concurrency/README.md).

This is the final module - once you're done, try building the
[Task Manager capstone project](../../project/README.md).

## ⚠️ Common mistakes

- Assuming concurrency automatically makes small programs faster.
- Updating shared state without synchronization.
- Passing unpicklable objects to process workers.
- Calling blocking functions directly inside coroutines.
- Creating tasks and never awaiting their completion or observing failures.

## ❓ Review questions

1. How do concurrency and parallelism differ?
2. Why can threads help I/O-bound work despite the GIL?
3. What costs accompany process-based parallelism?
4. What happens if a coroutine performs blocking work?
5. Why should a concurrency decision be measured rather than assumed?
