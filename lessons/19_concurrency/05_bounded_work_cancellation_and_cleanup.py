"""Lesson 19.5: Bounded work, cancellation, and cleanup.

Purpose:
    Turn "run everything at once" into owned, bounded, cancellable work. You
    will cap fan-out with ``asyncio.Semaphore``, treat cancellation as a
    *request* that must be awaited, guarantee cleanup with ``try``/``finally``,
    and bridge an unavoidable blocking call with ``asyncio.to_thread``. Finally
    you will meet ``asyncio.TaskGroup`` as the structured-concurrency default,
    while still practising explicit cancellation.

Prerequisites:
    - Lesson 4: ``async``/``await``, the event loop, ``create_task`` ownership,
      strong task references, and ``gather`` ordering and failure rules.
    - Exceptions and ``finally`` (Chapter 7). Cleanup that must always run
      belongs in ``finally`` -- including when a task is cancelled.

Facts this lesson encodes precisely:
    - ``asyncio.CancelledError`` directly subclasses ``BaseException`` (not
      ``Exception``), so a blanket ``except Exception`` will not catch it and a
      broad catch must not swallow it.
    - Cancellation is cooperative: ``task.cancel()`` requests a
      ``CancelledError`` at the next ``await``; the owner should then ``await``
      the task so cleanup completes and the outcome is observed.
    - A synchronous blocking call inside a coroutine blocks the whole loop;
      ``asyncio.to_thread`` moves it to a worker thread.

The lesson is deterministic and offline. Overlap and cleanup are proven with
events, and no step asserts a wall-clock speedup.
"""

from __future__ import annotations

import asyncio


async def bounded_fan_out(limit: int, total: int) -> tuple[int, int]:
    """Run ``total`` tasks but keep at most ``limit`` inside the critical region.

    Determinism comes from two events. Every task that acquires the semaphore
    increments ``active``; when ``active`` first reaches ``limit`` it sets
    ``full``. The owner waits for ``full``, reads ``active`` (exactly ``limit``,
    because the semaphore blocks the rest), then sets ``release`` to drain them.
    The returned ``(observed, peak)`` proves real overlap up to the limit and
    that the limit was never exceeded -- without timing anything.
    """
    semaphore = asyncio.Semaphore(limit)
    active = 0
    peak = 0
    full = asyncio.Event()
    release = asyncio.Event()

    async def worker() -> None:
        nonlocal active, peak
        async with semaphore:
            active += 1
            peak = max(peak, active)
            if active >= limit:
                full.set()
            await release.wait()
            active -= 1

    # Own every task with a strong reference until it is awaited.
    tasks = [asyncio.create_task(worker()) for _ in range(total)]
    await full.wait()
    observed_active = active  # exactly `limit` tasks are inside right now
    release.set()
    await asyncio.gather(*tasks)
    return observed_active, peak


async def cancellation_with_cleanup() -> tuple[bool, bool]:
    """Cancel an owned task and prove its ``finally`` cleanup ran before return.

    ``started`` guarantees the task is actually running before we cancel it.
    The task parks on an event that is never set, so only cancellation can end
    it. We request cancellation, then ``await`` the task: the ``finally`` sets
    ``cleaned`` and the owner observes the ``CancelledError``.
    """
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def long_running() -> None:
        started.set()
        try:
            await asyncio.Event().wait()  # never resolves; ends only via cancel
        finally:
            # Cleanup must run on the cancellation path too.
            cleaned.set()

    task = asyncio.create_task(long_running())
    await started.wait()
    task.cancel()  # a request, delivered at the task's next await

    cancelled_observed = False
    try:
        await task  # let the cancellation and its cleanup complete
    except asyncio.CancelledError:
        cancelled_observed = True
    return cancelled_observed, cleaned.is_set()


def blocking_square(value: int) -> int:
    """A synchronous function. Awaiting real work like this inline would block
    the event loop; ``to_thread`` is the bounded bridge for it."""
    return value * value


async def offload_blocking(value: int) -> int:
    """Run a blocking call on a worker thread and await its result.

    ``to_thread`` keeps the event loop responsive: the loop schedules other
    tasks while the worker thread runs ``blocking_square``.
    """
    return await asyncio.to_thread(blocking_square, value)


async def structured_group(values: list[int]) -> list[int]:
    """Run sibling tasks under a ``TaskGroup``, awaited automatically on exit.

    ``TaskGroup`` is the structured-concurrency default: creating tasks in the
    ``async with`` block and letting the block's exit await them keeps ownership
    and error handling in one place.
    """
    results: list[int] = []

    async def collect(value: int) -> None:
        results.append(await offload_blocking(value))

    async with asyncio.TaskGroup() as group:
        for value in values:
            group.create_task(collect(value))
    return sorted(results)


async def taskgroup_cancels_siblings() -> bool:
    """Contrast with ``gather``: a ``TaskGroup`` failure *cancels* siblings.

    The sibling runs until the failing task raises; the group then cancels the
    sibling, whose ``finally`` sets ``cleaned``. In Lesson 4 a ``gather``
    sibling kept running instead -- that is the structural difference.
    """
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def sibling() -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()

    async def failing() -> None:
        await started.wait()  # ensure the sibling is live before failing
        raise ValueError("boom")

    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(sibling())
            group.create_task(failing())
    except* ValueError:
        # TaskGroup reports failures as an ExceptionGroup, matched with except*.
        pass
    return cleaned.is_set()


async def main() -> None:
    # Step 1: a semaphore bounds fan-out; events prove the bound deterministically.
    print("Step 1: bounded fan-out with a semaphore")
    observed, peak = await bounded_fan_out(limit=2, total=5)
    assert observed == 2  # exactly `limit` overlapped -- real concurrency
    assert peak == 2  # and never more than `limit`
    print(f"  limit=2 over 5 tasks -> {observed} active at once, peak {peak}")

    # Step 2: cancellation is a request; cleanup belongs in finally.
    print("\nStep 2: cancel as a request, cleanup in finally")
    assert issubclass(asyncio.CancelledError, BaseException)
    assert not issubclass(asyncio.CancelledError, Exception)
    cancelled_observed, cleaned = await cancellation_with_cleanup()
    assert cancelled_observed and cleaned
    print("  CancelledError is a BaseException; cleanup ran before return")

    # Step 3: bridge a blocking call with to_thread.
    print("\nStep 3: bridge a blocking call with to_thread")
    bridged = await offload_blocking(9)
    assert bridged == 81
    print(f"  to_thread ran a blocking call off the loop -> {bridged}")

    # Step 4: TaskGroup as the structured default; it cancels siblings on failure.
    print("\nStep 4: TaskGroup structured concurrency")
    grouped = await structured_group([1, 2, 3, 4])
    assert grouped == [1, 4, 9, 16]
    print(f"  TaskGroup awaited all siblings -> {grouped}")
    siblings_cleaned = await taskgroup_cancels_siblings()
    assert siblings_cleaned is True
    print("  a TaskGroup failure cancelled its sibling (cleanup still ran)")
    print("  the exercise still asks you to cancel-and-await one task explicitly")


if __name__ == "__main__":
    asyncio.run(main())
