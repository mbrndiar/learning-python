# 🧪 Exercises: Chapter 19 — Concurrent execution

Own concurrent work across every model this chapter teaches — a model decision,
threads with a shared invariant, a process pool, and asyncio scheduling,
bounding, and cancellation — behind seven small, typed functions. No network, no
sleeps standing in for timing.

## 🧩 What you will implement

The seven functions are graded in five progressive groups:

1. **Model selection** — `choose_execution_model(workload)` returns
   `"sequential"`, `"threads"`, `"processes"`, or `"asyncio"` for a small
   `Workload` taxonomy, and validates its input.
2. **Threaded fan-out** — `run_in_threads(func, items)` runs one thread per item,
   preserves input order, handles empty input, and re-raises the first worker
   exception. Real overlap is proven with a `threading.Barrier`.
3. **Locked transfer invariant** — `transfer_locked(balances, source, target,
   amount, lock)` moves money under the supplied lock so the multi-balance total
   is conserved, with no partial update.
4. **Process pool** — `map_in_processes(func, items, workers=2)` maps over an
   owned `spawn` process pool, preserving order and propagating failures.
5. **Async scheduling, bounding, and cancellation** — `async_map(func, items)`,
   `async_map_limited(func, items, limit)`, and `cancel_and_wait(task)`.

The evaluator injects barriers, events, a tracking lock, a guarded mapping, and
top-level picklable workers. It never measures a clock or asserts a speedup.

## 📥 Inputs and 📤 outputs

- `Workload(kind, operations, async_client=False)` where `kind` is
  `"blocking-io"` or `"cpu-bound"`; `choose_execution_model` returns one of the
  four model strings.
- `run_in_threads` and `map_in_processes` are generic over `func: (T) -> R` and a
  sequence of `T`, and return `list[R]` in input order.
- `async_map` and `async_map_limited` are generic over `func: (T) -> Awaitable[R]`
  and return `list[R]` in input order.
- `cancel_and_wait(task)` returns the task's result if it already succeeded,
  `None` if it was cancelled, and re-raises a prior failure.
- `transfer_locked` mutates the `balances` mapping in place and returns `None`.

## 📋 Contract and constraints

- **Sequential default.** `choose_execution_model` returns `"sequential"` for
  fewer than two operations; `"processes"` for CPU-bound; `"asyncio"` for
  blocking-I/O with an async client; otherwise `"threads"`. It rejects a boolean
  or negative `operations` and an unknown `kind`.
- **Start-all then join-all.** `run_in_threads` must start every thread before
  joining any, so the work overlaps; a barrier check fails a serialized version.
- **Exceptions propagate in order.** If workers raise, `run_in_threads` re-raises
  the first exception in input order; results are never partial.
- **One critical section.** `transfer_locked` validates `amount` (rejecting
  `bool` and non-positive values) outside the lock, then, *inside* the lock,
  checks that both accounts exist and funds suffice before debiting and
  crediting. Missing accounts raise `KeyError`; insufficient funds raise
  `ValueError`; the total is conserved and never partially updated. The evaluator
  rejects a missing or too-narrow lock scope deterministically.
- **Owned spawn pool.** `map_in_processes` validates `workers` (rejecting `bool`
  and non-positive counts), handles empty input, and owns a
  `ProcessPoolExecutor` built with `multiprocessing.get_context("spawn")`.
  Results follow input order; worker failures propagate; process input is copied,
  so the caller's objects are untouched.
- **Schedule all, preserve order.** `async_map` schedules every operation
  concurrently and returns results in input order, propagating the first failure.
- **Bounded fan-out.** `async_map_limited` rejects a `bool` or non-positive
  `limit`, then runs at most `limit` operations at once with an
  `asyncio.Semaphore`, preserving order and exceptions. The evaluator uses events
  to reject both serialization and unbounded fan-out.
- **Cancel as a request.** `cancel_and_wait` requests cancellation and awaits the
  task, swallowing only that task's `CancelledError`, allowing an
  already-completed success, propagating an already-completed failure, and never
  swallowing cancellation of the owner that is awaiting it. The evaluator
  observes a `finally` cleanup event and proves cleanup finished before the call
  returned.

## 🧨 Edge cases the checks exercise

- Boolean and negative `operations`, and an unknown workload `kind`, are rejected.
- An empty item list returns `[]` for the threaded, process, and async maps.
- A barrier proves the threads genuinely overlapped; a serialized version fails.
- Missing accounts, insufficient funds, and invalid amounts leave balances intact.
- Balance access outside the lock fails via a guarded mapping and tracking lock.
- 100 real threaded transfers under one lock keep the total exactly conserved.
- A worker mutation affects only its copied process input, not the caller's object.
- Events prove `async_map` schedules everything and `async_map_limited` stays at
  exactly its limit — neither serialized nor unbounded.
- Cancelling a running task runs its `finally` before `cancel_and_wait` returns;
  a completed task's success is returned, a prior failure is re-raised, and
  cancellation of the owner still propagates.

## ▶️ Run the exercise

Read [`lessons/19_concurrency/`](../../lessons/19_concurrency/README.md) first,
then, from the repository root:

```bash
python exercises/19_concurrency/exercises.py
```

The untouched starter fails first in the **model selection** group. Implement the
`TODO` blocks until all five groups print `OK` and the file ends with
`All checks passed!`.

The reference solution stays locked until you have attempted the exercise.

This is the final exercise module, following the required
[Task REST API and clients project](../../projects/tasks/README.md). It prepares
you to reason about process contention in the comparative capstone and bounded
threads in the idiomatic capstone: complete it before the
[two required capstones](../../capstones/README.md).
