"""
Exercises: 10 Concurrency

Implement each function below, then run this file directly to check
your work.
"""

import asyncio


def run_in_threads(func, items):
    """Run func(item) for every item in `items` concurrently using
    threading.Thread, and return a list of results in the same order
    as `items`.

    Hint: store results in a pre-sized list and have each thread write
    to its own index.
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


if __name__ == "__main__":
    results = run_in_threads(lambda x: x * x, [1, 2, 3, 4])
    assert results == [1, 4, 9, 16]
    print("run_in_threads: OK")

    gathered = asyncio.run(fetch_all([1, 2, 3]))
    assert gathered == [1, 2, 3]
    print("fetch_all: OK")

    print("\nAll checks passed!")
