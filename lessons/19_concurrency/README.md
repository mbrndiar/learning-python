# ⚡ Chapter 19: Concurrent execution

The [Task REST API and clients project](../../projects/tasks/README.md) left you
with a program that does one thing at a time: it validates a task, opens a
connection, waits for the response, and only then starts the next call. That
sequential shape is correct, and for most programs it is also the right shape.
This final chapter asks a narrower question: *when a program spends its time
waiting, or has real CPU work to spread across cores, how do you overlap that
work safely?*

We answer it one model at a time — sequential, threads, processes, and asyncio —
and we never start from "make it concurrent." We start from a bottleneck you can
name, choose the smallest model that addresses it, and pay close attention to
the new hazards each model introduces: shared state, a serialization boundary,
cooperative scheduling, cancellation, and cleanup.

## 🧭 Where this chapter fits

This is the last chapter, and it deliberately comes **after** the Task project.
You already know:

- functions, annotations, and return contracts (Chapter 5);
- exceptions, `try`/`finally`, and the `with` statement (Chapter 7);
- JSON and serialization boundaries (Chapter 8);
- dataclasses, enums, `Literal`, and dependency injection (Chapters 9, 11);
- generators as suspendable calls (Chapter 10); and
- HTTP clients that block while waiting for a response (Chapter 18).

Concurrency reuses all of it. The project gives us a concrete motivation:
fetching several independent task pages is exactly the kind of independent,
wait-dominated work that overlaps well. Everything here is **offline and
deterministic** — no network, no sleeps standing in for timing. Where a lesson
must prove that work truly overlapped, it uses a synchronization primitive (a
`Barrier` or an `Event`) that would deadlock if the work were secretly
serialized, instead of measuring a clock.

## 🎯 Learning objectives

After this chapter you should be able to:

- distinguish **sequential**, **concurrent**, and **parallel** execution, and
  explain why concurrency does not by itself make a program faster;
- classify a workload as **blocking-I/O** or **CPU-bound** and pick a starting
  model, keeping **sequential** as the default;
- construct threads, start-all then join-all, and protect a shared invariant
  with a `Lock`, understanding that the GIL is not a synchronization tool;
- run CPU-bound work in a `ProcessPoolExecutor` across a `spawn` **pickle
  boundary**, with importable workers and a `__main__` guard;
- explain `async def`, the difference between a coroutine *function* and a
  coroutine *object*, `await`, `asyncio.run`, and `create_task` ownership; and
- bound fan-out with a `Semaphore`, cancel a task as a **request** and await it,
  and guarantee cleanup with `try`/`finally`.

## 🧠 1. Mental model: sequential, concurrent, parallel

Three words that are often blurred:

- **Sequential** — one worker does one step at a time, finishing each task
  before starting the next. `A1 A2 A3 B1 B2 B3`.
- **Concurrent** — one worker interleaves progress on several tasks. Their
  lifetimes overlap even though only one step happens at any instant.
  `A1 B1 A2 B2 A3 B3`. Concurrency is a way of *structuring* overlapping
  progress.
- **Parallel** — two or more workers execute *at the same instant* on separate
  cores. Parallelism is the hardware actually doing two things at once.

Lesson 1 makes this concrete by driving two generators by hand: the same steps,
scheduled two ways. The multiset of steps is identical; only the interleaving
differs, and nothing runs in parallel — a single loop on a single core.

Concurrency *enables* parallelism but does not require it: asyncio is concurrent
on one thread with no parallelism at all, while a process pool is genuinely
parallel.

## ⚖️ 2. Concurrency is not speed

The most important sentence in this chapter: **concurrency does not guarantee a
speedup.** Overlap only helps when there is something to overlap — many
independent waits, or CPU work that can be split across cores. Adding workers
also adds scheduling, coordination, cancellation, and debugging cost, plus, for
processes, startup and serialization cost that can dwarf a small task.

That is why every lesson proves *correctness* — real overlap, preserved
ordering, complete cleanup — and never asserts a wall-clock win. When you build
something real, **measure** the specific workload before and after; the sections
below give you the reasoning, not a benchmark.

## 🧭 3. Choosing a model: name the workload first

Two questions decide the starting model:

1. **How many independent operations are there?** Fewer than two → stay
   **sequential**; there is nothing to overlap.
2. **Is the work waiting or computing?** *Blocking I/O* (network, disk) overlaps
   well with threads or asyncio; *CPU-bound* Python needs processes to use more
   than one core.

| Workload | Good starting point |
| --- | --- |
| Fewer than two independent operations | **sequential** |
| Blocking I/O, only synchronous clients | **threads** |
| Blocking I/O, coroutine-native client | **asyncio** |
| CPU-bound pure Python, several units | **processes** |

Lesson 1 encodes exactly this as `choose_execution_model(workload)`. Treat its
answer as a *starting hypothesis* to measure, not a verdict.

## 🧵 4. Threads, shared state, and locks (Lesson 2)

A thread runs inside the current process and **shares its memory**. That makes
communication trivial and data races possible.

- **Lifecycle.** Build `threading.Thread(target=..., args=...)`, then
  **start all, then join all**. Starting and immediately joining each thread in
  turn would serialize them. Lesson 2 proves real overlap with a
  `threading.Barrier`: every worker must arrive before any is released, so a
  returned result means they were alive together (the finite timeout is only a
  deadlock guard, never a speed claim).
- **Exceptions do not propagate.** A worker that raises does **not** deliver
  that exception to the code that started it; `join()` returns normally. If you
  want the failure, the worker must capture it and the owner must re-raise it.
- **The hazard, deterministically.** Two threads each add 1 to a shared counter.
  Both read `0`, a `Barrier` forces both reads before either write, then both
  write `1` — one increment is lost. The result is a guaranteed `1` instead of
  `2`: the race is *forced*, not sampled.
- **A lock protects a complete invariant.** `threading.Lock` makes a whole
  read-modify-write atomic with respect to other threads. A money transfer
  touches *two* balances, so the lock must cover the entire debit-and-credit;
  the total is then conserved no matter how threads interleave.

### The GIL, accurately

In today's default CPython builds, a **Global Interpreter Lock (GIL)** lets only
one thread execute Python bytecode at a time. So threads overlap **waiting**
(blocking I/O) but do not run CPU-bound Python in parallel — which is why CPU
work goes to processes, not threads.

Two corrections to a common myth:

- **The GIL is not a synchronization tool.** Thread execution can switch between
  the read and write steps of a larger operation, and extension code may release
  the GIL explicitly, so an unguarded invariant can still interleave and lose
  data. You still need a `Lock`.
- **Free-threaded builds exist.** Optional *free-threaded* CPython builds (first
  shipped in 3.13, still not the default in 3.14) run threads without a GIL.
  They remove the parallelism limit and, if anything, *increase* the need to
  protect shared mutable state. Either way, the correct tool for a shared
  invariant is a lock — never the GIL.

## 🧱 5. Processes, serialization, and pools (Lesson 3)

A process has its **own interpreter and its own memory**, so CPU-bound Python
can run truly in parallel across processes. The cost is a boundary.

- **The pickle boundary.** A worker callable, its arguments, and its results are
  **pickled** to cross into another interpreter. The callable must therefore be
  importable by name: a **top-level function**, not a lambda or a function
  defined inside another function. Plain data (numbers, lists, dicts) crosses
  fine. Lesson 3 checks this directly with a pickle round-trip.
- **Separate memory.** Because arguments are copied across the boundary, a
  worker that mutates its argument cannot touch the caller's object. Lesson 3
  sends a list to a worker that appends to it and shows the caller's list
  unchanged.
- **`spawn` and `__main__`.** As of **Python 3.14, `fork` is no longer the
  default start method on any platform.** Lesson 3 requests
  `multiprocessing.get_context("spawn")` explicitly, so a fresh interpreter
  starts each worker identically on 3.11 and 3.14. A spawned worker **re-imports
  your module**, so all pool creation must live under
  `if __name__ == "__main__"`; otherwise each worker would try to build its own
  pool and recurse.
- **Own the pool; read results in order.** A `ProcessPoolExecutor` from
  `concurrent.futures`, used as a context manager, shuts its workers down on
  exit. `executor.map` returns results in **input order**, even though workers
  finish in an arbitrary order.

```python
context = multiprocessing.get_context("spawn")
with ProcessPoolExecutor(max_workers=2, mp_context=context) as executor:
    squares = list(executor.map(square, numbers))  # input order, not finish order
```

## 🌊 6. Asyncio: coroutines, tasks, scheduling (Lesson 4)

`asyncio` runs many operations concurrently on **one thread** by cooperatively
scheduling coroutines around their `await` points.

- **Coroutine function vs coroutine object.** `async def f(): ...` defines a
  coroutine *function*. Calling `f()` returns a coroutine *object* and **runs
  none of the body** — nothing is scheduled yet. You either `await` it or wrap
  it in a task; an un-awaited coroutine is a bug (and a warning).
- **Running it.** `asyncio.run(main())` builds an event loop, drives `main()` to
  completion, and closes the loop. It is the single entry point from synchronous
  code.
- **`await` runs inline.** Awaiting a coroutine runs it as part of the *current*
  task. Two sequential `await`s do **not** overlap.
- **`create_task` schedules concurrently — and needs an owner.** `asyncio.create_task(coro)`
  schedules the coroutine to run soon and returns a `Task`. The event loop keeps
  only a **weak reference** to tasks, so *you must keep a strong reference*
  (a variable or a set) or the task may be garbage-collected mid-flight. Lesson 4
  proves cooperative overlap with an `Event` "ping-pong": two tasks hand control
  back and forth, an order that only concurrent, live tasks can produce.
- **`gather` ordering and its failure boundary.** `asyncio.gather(*aws)` returns
  results in the **order of the inputs**, not the order they finished. With the
  default `return_exceptions=False`, the **first exception propagates
  immediately to the caller, but the other awaitables are *not* cancelled and
  keep running**. With `return_exceptions=True`, exceptions are collected in the
  result list in input order. (This "siblings keep running" behavior is the key
  contrast with `TaskGroup` below.)

## 🎚️ 7. Bounded work, cancellation, and cleanup (Lesson 5)

Real systems do not fan out without limit, and they must stop work cleanly.

- **Bound fan-out with a `Semaphore`.** `asyncio.Semaphore(limit)` admits at most
  `limit` holders at once. Lesson 5 proves the bound deterministically with two
  events: workers signal when `limit` are simultaneously inside, and the owner
  confirms exactly `limit` overlapped and the peak never exceeded it.
- **Cancellation is a request.** `task.cancel()` asks the loop to raise
  `asyncio.CancelledError` inside the task at its next `await`. It is not an
  immediate kill. The owner should then **`await` the task** so the cancellation
  and its cleanup actually complete and the outcome is observed.
- **`CancelledError` is a `BaseException`.** It subclasses `BaseException`
  directly, *not* `Exception`, so a blanket `except Exception` will not catch it
  — by design. Never swallow it in a broad catch.
- **Cleanup belongs in `finally`.** Whatever must run on the way out — releasing
  a resource, recording state — goes in `try`/`finally`, so it runs on the
  cancellation path too.
- **Bridge a blocking call with `to_thread`.** A synchronous blocking call inside
  a coroutine freezes the *whole* loop. `asyncio.to_thread(func, *args)` runs it
  on a worker thread and awaits the result, keeping the loop responsive.
- **`TaskGroup` is the structured default.** `async with asyncio.TaskGroup() as
  tg:` creates tasks and awaits them all on exit, and — unlike `gather` — **cancels
  the remaining siblings when one task fails**. Prefer it for related tasks. This
  chapter still teaches explicit `cancel()`-and-`await`, because owning a single
  task's cancellation is a skill the exercise exercises directly.

## 🧪 Read, predict, run, modify

Work one lesson at a time. Predict first, then run, then make the change and
predict again.

### Lesson 1 — concurrency, parallelism, and workloads

Predict the two step orderings for tasks `A` and `B`, and which model
`choose_execution_model` returns for CPU-bound work with one operation. Run:

```bash
python lessons/19_concurrency/01_concurrency_parallelism_and_workloads.py
```

Expected (abridged):

```text
  sequential order: A1 A2 A3 B1 B2 B3
  concurrent order: A1 B1 A2 B2 A3 B3
```

Then change a workload's `operations` to `1` and predict why the model becomes
`sequential`.

### Lesson 2 — threads, shared state, and locks

Predict the lost-update result, and whether a worker's `ValueError` reaches
`main`. Run:

```bash
python lessons/19_concurrency/02_threads_shared_state_and_locks.py
```

Expected (abridged):

```text
  two +1 workers, guarded by nothing -> counter = 1 (want 2)
  8 x 1000 locked increments -> 8000 (exact)
```

Then remove the `with lock:` in `safe_increment_total` and predict why the total
may no longer be exact (and why the GIL does not save you).

### Lesson 3 — processes, serialization, and pools

Predict whether a lambda is picklable, and the order of `executor.map` results.
Run:

```bash
python lessons/19_concurrency/03_processes_serialization_and_pools.py
```

Expected (abridged):

```text
  squares in input order: [0, 1, 4, 9, 16, 25]
  worker saw length 4; our list is still [10, 20, 30]
```

Then move `map_in_spawn_pool`'s pool creation *outside* the `__main__` guard and
predict why a `spawn` worker would recurse.

### Lesson 4 — asyncio coroutines, tasks, and scheduling

Predict the ping-pong order and the result order of a `gather` where the second
input finishes first. Run:

```bash
python lessons/19_concurrency/04_asyncio_coroutines_tasks_and_scheduling.py
```

Expected (abridged):

```text
  cooperative order: ['ping-start', 'pong', 'ping-end']
  results follow input order: ['first', 'second']
```

Then, in `gather_failure_boundary`, predict whether the sibling is cancelled
when the other awaitable raises (compare with a `TaskGroup`).

### Lesson 5 — bounded work, cancellation, and cleanup

Predict the peak concurrency for `limit=2, total=5`, and whether cleanup runs
when a task is cancelled. Run:

```bash
python lessons/19_concurrency/05_bounded_work_cancellation_and_cleanup.py
```

Expected (abridged):

```text
  limit=2 over 5 tasks -> 2 active at once, peak 2
  CancelledError is a BaseException; cleanup ran before return
```

Then change `except* ValueError` to catch a different type and predict why the
`TaskGroup` failure would no longer be handled.

## 🔬 Controlled experiments

Small, reversible changes that turn a claim into an observation:

- **Serialize the threads.** In Lesson 2, join each thread right after starting
  it. The barrier demo will now raise `BrokenBarrierError` on timeout — proof
  that the barrier was detecting genuine overlap.
- **Break the invariant deliberately.** Compare `safe_increment_total` with the
  barrier-coordinated `demonstrate_lost_update`. The barrier forces both reads
  before either write, proving the lost update without relying on whether an
  ordinary run happens to expose the race.
- **Break picklability.** Pass a `lambda` to `executor.map` in Lesson 3 and
  watch the pool fail to send it — the boundary is real.
- **Forget the owner.** In Lesson 4, create a task without keeping a reference
  and never await it; reason about why the loop is free to drop it.
- **Skip the await after cancel.** In Lesson 5, call `task.cancel()` but do not
  `await` the task; the `finally` cleanup may not have completed when you move
  on. Awaiting is what makes cancellation observable and complete.

## ⚠️ Common mistakes

- Reaching for concurrency to make small or CPU-cheap work "faster."
- Starting and joining threads one at a time, accidentally serializing them.
- Assuming a worker thread's exception will surface in the caller.
- Updating shared mutable state without a lock — trusting the GIL instead.
- Passing a lambda or a locally defined function to a process pool.
- Creating a pool outside `if __name__ == "__main__"` and recursing on `spawn`.
- Believing `fork` is still the default in 3.14 (it is not).
- Calling a coroutine function and forgetting to `await` or schedule it.
- Losing a task by not keeping a strong reference to it.
- Expecting `gather` to cancel siblings on failure (it does not; `TaskGroup`
  does).
- Catching `CancelledError` in a broad `except Exception` (it is a
  `BaseException`), or swallowing it without re-raising after cleanup.
- Cancelling a task but never awaiting it, so cleanup may not finish.
- Calling a blocking function directly inside a coroutine and freezing the loop.

## 🧾 Summary

- Sequential is the default; concurrency overlaps *progress* and does not
  guarantee speed.
- Name the workload first: blocking-I/O → threads or asyncio; CPU-bound →
  processes; fewer than two operations → sequential.
- Threads share memory: start-all/join-all, capture worker exceptions, and
  protect complete invariants with a `Lock`. The GIL is not synchronization, and
  free-threaded builds only raise the stakes.
- Processes have separate memory and a pickle boundary: importable workers,
  explicit `spawn`, a `__main__` guard, an owned pool, and input-ordered results.
- Asyncio schedules coroutines on one thread: calling a coroutine schedules
  nothing, `create_task` needs a strong-referenced owner, and `gather` preserves
  input order while leaving failing siblings running.
- Bound fan-out with a `Semaphore`; cancellation is an awaited request;
  `CancelledError` is a `BaseException`; cleanup goes in `finally`; `to_thread`
  bridges a blocking call; `TaskGroup` is the structured default.

## ❓ Review questions (closed notes)

1. In one sentence each, distinguish sequential, concurrent, and parallel
   execution. Which one does asyncio provide, and which do processes provide?
2. Why does concurrency not guarantee a speedup, and what would you measure to
   find out?
3. Why must threads be started all-then-joined-all rather than one at a time,
   and what does a `Barrier` prove that a timer cannot?
4. The GIL prevents parallel Python bytecode in default builds — so why do you
   still need a `Lock` for a shared counter?
5. What exactly crosses the process pickle boundary, and why can a lambda not be
   a process worker?
6. Why must process-pool creation sit under `if __name__ == "__main__"`, and
   what changed about the default start method in Python 3.14?
7. What is the difference between a coroutine function and a coroutine object,
   and what happens if you call one without awaiting it?
8. When one awaitable passed to `gather` raises, what happens to the others —
   and how does a `TaskGroup` differ?
9. Why is `task.cancel()` a request rather than a kill, and why should the owner
   `await` the task afterward?
10. Why can a blanket `except Exception` fail to catch a cancellation, and where
    should cleanup live?

## 📚 Authoritative references

- [`threading`](https://docs.python.org/3.14/library/threading.html)
- [`multiprocessing`](https://docs.python.org/3.14/library/multiprocessing.html)
- [`concurrent.futures.ProcessPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#processpoolexecutor)
- [`asyncio` tasks and coroutines](https://docs.python.org/3.14/library/asyncio-task.html)
- [`asyncio` synchronization primitives](https://docs.python.org/3.14/library/asyncio-sync.html)
- [`asyncio` runners](https://docs.python.org/3.14/library/asyncio-runner.html)

Next, complete the
[Chapter 19 exercise](../../exercises/19_concurrency/README.md). This is the
final module, following the required
[Task REST API and clients project](../../projects/tasks/README.md). Once you are
done, build [both equally required capstones](../../capstones/README.md).
