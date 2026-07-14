"""
Solutions: 11 Concurrency
"""

import asyncio
import threading


def run_in_threads(func, items):
    results = [None] * len(items)
    errors = [None] * len(items)

    def worker(index, item):
        try:
            results[index] = func(item)
        except Exception as error:
            errors[index] = error

    threads = [
        threading.Thread(target=worker, args=(i, item)) for i, item in enumerate(items)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for error in errors:
        if error is not None:
            raise error
    return results


async def fetch(value, delay=0.05):
    await asyncio.sleep(delay)
    return value


async def fetch_all(values):
    return await asyncio.gather(*(fetch(value) for value in values))


async def fetch_all_limited(values, limit):
    if limit < 1:
        raise ValueError("limit must be positive")
    semaphore = asyncio.Semaphore(limit)

    async def limited_fetch(value):
        async with semaphore:
            return await fetch(value)

    return await asyncio.gather(*(limited_fetch(value) for value in values))


async def fetch_with_timeout(value, delay, timeout):
    return await asyncio.wait_for(fetch(value, delay), timeout=timeout)


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
