"""Lesson 19.4: Asyncio coroutines, tasks, and scheduling.

Purpose:
    Introduce ``async``/``await`` from first principles. You will separate a
    *coroutine function* from the *coroutine object* it returns, see that
    calling one schedules nothing, drive a coroutine with ``asyncio.run``, and
    then make coroutines overlap with ``asyncio.create_task``. Scheduling is
    shown deterministically with ``asyncio.Event`` -- no sleeps that pretend to
    measure time -- and ``asyncio.gather`` is explained with its exact ordering
    and failure rules.

Prerequisites:
    - Lesson 1's model: asyncio suits many *blocking-I/O* operations when a
      coroutine-native client exists; it is a single thread cooperatively
      scheduling awaits, not extra cores.
    - Generators and the idea of a suspendable call (Chapter 10). A coroutine
      is a function the event loop can pause at each ``await``.
    - Exceptions (Chapter 7): a failure inside one coroutine surfaces where it
      is awaited, so ownership decides who observes it.

This lesson is deterministic and offline. ``asyncio.sleep(0)`` is used only as
a *cooperative yield* -- a documented way to let other tasks run a step -- never
as a timed delay, and nothing here asserts a speedup.
"""

from __future__ import annotations

import asyncio
import inspect


async def add(left: int, right: int) -> int:
    """A trivial coroutine function. Calling it returns a coroutine object."""
    return left + right


async def value_after_yields(value: str, yields: int) -> str:
    """Return ``value`` after cooperatively yielding ``yields`` times.

    Each ``await asyncio.sleep(0)`` hands control back to the loop for one step,
    so a coroutine with more yields *completes later* in scheduling order. This
    lets us separate completion order from result order without any real delay.
    """
    for _ in range(yields):
        await asyncio.sleep(0)
    return value


def describe_coroutine_object() -> tuple[bool, bool]:
    """Show that ``add`` is a coroutine *function* and ``add(...)`` an object.

    Crucially, building the object runs none of the body. We close the object
    to release it cleanly instead of leaving an un-awaited coroutine behind.
    """
    is_function = inspect.iscoroutinefunction(add)
    pending = add(1, 2)  # nothing has executed yet
    is_object = inspect.iscoroutine(pending)
    pending.close()  # avoid a "coroutine was never awaited" warning
    return is_function, is_object


async def ping_pong() -> list[str]:
    """Prove two tasks overlap cooperatively using events, not timing.

    ``ping`` records, signals ``ping_ready``, and suspends on ``pong_ready``.
    ``pong`` cannot proceed until ``ping_ready`` is set, then records and
    releases ``ping``. The only order the events permit is start, pong, end --
    a deterministic proof that both tasks were live and handed control back and
    forth. Serialized execution could not satisfy the mutual waits.
    """
    log: list[str] = []
    ping_ready = asyncio.Event()
    pong_ready = asyncio.Event()

    async def ping() -> None:
        log.append("ping-start")
        ping_ready.set()
        await pong_ready.wait()
        log.append("ping-end")

    async def pong() -> None:
        await ping_ready.wait()
        log.append("pong")
        pong_ready.set()

    # Keep strong references. The loop holds only weak references to tasks, so
    # an unreferenced task can be garbage-collected before it finishes.
    ping_task = asyncio.create_task(ping())
    pong_task = asyncio.create_task(pong())
    await asyncio.gather(ping_task, pong_task)
    return log


async def gather_preserves_input_order() -> list[str]:
    """Return gather's results, which follow input order, not completion order.

    "first" yields three times and "second" only once, so "second" finishes
    first. ``gather`` still returns ["first", "second"] because results align
    with the *input* sequence.
    """
    return list(
        await asyncio.gather(
            value_after_yields("first", yields=3),
            value_after_yields("second", yields=1),
        )
    )


async def gather_failure_boundary() -> tuple[str, bool, bool]:
    """Show that a failing awaitable does not cancel its gather siblings.

    With the default ``return_exceptions=False``, the first exception is
    propagated to the awaiter immediately, but the other awaitables are *not*
    cancelled and keep running. We own the sibling as a task so we can confirm
    it was neither cancelled nor abandoned.
    """
    log: list[str] = []

    async def sibling() -> str:
        await value_after_yields("", yields=2)
        log.append("sibling-done")
        return "sibling"

    async def failing() -> str:
        raise ValueError("boom")

    sibling_task = asyncio.create_task(sibling())
    failing_task = asyncio.create_task(failing())

    raised = ""
    try:
        await asyncio.gather(failing_task, sibling_task)
    except ValueError as error:
        raised = str(error)

    was_cancelled = sibling_task.cancelled()
    # The sibling kept running; awaiting it now completes it normally.
    await sibling_task
    return raised, was_cancelled, ("sibling-done" in log)


async def gather_collects_exceptions() -> list[str]:
    """With ``return_exceptions=True``, failures are aggregated in order."""

    async def failing() -> str:
        raise ValueError("boom")

    results = await asyncio.gather(
        value_after_yields("ok", yields=1),
        failing(),
        return_exceptions=True,
    )
    # Normalize to labels so the ordered shape is easy to assert.
    return [item if isinstance(item, str) else type(item).__name__ for item in results]


async def main() -> None:
    # Step 1: coroutine function vs coroutine object; run one with asyncio.run.
    print("Step 1: async def, the coroutine object, and awaiting")
    is_function, is_object = describe_coroutine_object()
    assert is_function and is_object
    print("  add is a coroutine function; add(1, 2) is an un-run coroutine object")
    total = await add(1, 2)  # await runs it inline, as part of this task
    assert total == 3
    print(f"  awaiting it produced {total}")

    # Step 2 and 3: create_task schedules concurrently; events prove overlap.
    print("\nStep 2-3: create_task overlaps work; events schedule it")
    order = await ping_pong()
    assert order == ["ping-start", "pong", "ping-end"]
    print(f"  cooperative order: {order}")

    # Step 4: gather ordering and its failure boundary.
    print("\nStep 4: gather ordering and failure boundary")
    ordered = await gather_preserves_input_order()
    assert ordered == ["first", "second"]  # input order despite finish order
    print(f"  results follow input order: {ordered}")

    raised, was_cancelled, sibling_ran = await gather_failure_boundary()
    assert raised == "boom"
    assert was_cancelled is False  # a sibling is not cancelled by gather
    assert sibling_ran is True
    print("  a gather failure propagated but did not cancel its sibling")

    collected = await gather_collects_exceptions()
    assert collected == ["ok", "ValueError"]  # aggregated, still in order
    print(f"  return_exceptions=True aggregates in order: {collected}")


if __name__ == "__main__":
    # asyncio.run builds an event loop, drives main() to completion, and closes
    # the loop. It is the single entry point from synchronous code.
    asyncio.run(main())
