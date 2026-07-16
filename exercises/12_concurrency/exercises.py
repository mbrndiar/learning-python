"""
Exercises: 12 Concurrency

Implement each function below, then run this file directly to check
your work.
"""

import asyncio


def run_in_threads(func, items):
    """Run func(item) for every item in `items` concurrently using
    threading.Thread, and return a list of results in the same order
    as `items`.

    Hint: store results and exceptions in pre-sized lists. After joining,
    re-raise the first worker exception instead of silently returning None.
    """
    # TODO: implement this function
    raise NotImplementedError


async def fetch(value, delay=0.05):
    """A coroutine that sleeps for `delay` seconds then returns `value`."""
    await asyncio.sleep(delay)
    return value


async def fetch_all(values):
    """Run `fetch` concurrently for every value in `values` using
    asyncio.gather, and return the list of results in order."""
    # TODO: implement this function
    raise NotImplementedError


async def fetch_all_limited(values, limit):
    """Fetch every value while allowing at most `limit` active operations."""
    # TODO: implement this function with asyncio.Semaphore
    raise NotImplementedError


async def fetch_with_timeout(value, delay, timeout):
    """Await fetch(value, delay) but raise TimeoutError after `timeout`."""
    # TODO: implement this function with asyncio.wait_for
    raise NotImplementedError


if __name__ == "__main__":
    results = run_in_threads(lambda x: x * x, [1, 2, 3, 4])
    assert results == [1, 4, 9, 16]
    try:
        run_in_threads(lambda _: 1 / 0, [1])
        raise AssertionError("expected ZeroDivisionError")
    except ZeroDivisionError:
        pass
    print("run_in_threads: OK")

    gathered = asyncio.run(fetch_all([1, 2, 3]))
    assert gathered == [1, 2, 3]
    print("fetch_all: OK")

    limited = asyncio.run(fetch_all_limited([1, 2, 3], limit=2))
    assert limited == [1, 2, 3]
    try:
        asyncio.run(fetch_all_limited([1], limit=0))
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    print("fetch_all_limited: OK")

    try:
        asyncio.run(fetch_with_timeout("late", delay=0.1, timeout=0.01))
        raise AssertionError("expected TimeoutError")
    except TimeoutError:
        pass
    print("fetch_with_timeout: OK")

    print("\nAll checks passed!")
