"""
Solutions: 10 Concurrency
"""

import asyncio
import threading


def run_in_threads(func, items):
    results = [None] * len(items)

    def worker(index, item):
        results[index] = func(item)

    threads = [
        threading.Thread(target=worker, args=(i, item))
        for i, item in enumerate(items)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return results


async def fetch(value, delay=0.05):
    await asyncio.sleep(delay)
    return value


async def fetch_all(values):
    return await asyncio.gather(*(fetch(value) for value in values))


if __name__ == "__main__":
    results = run_in_threads(lambda x: x * x, [1, 2, 3, 4])
    assert results == [1, 4, 9, 16]
    print("run_in_threads: OK")

    gathered = asyncio.run(fetch_all([1, 2, 3]))
    assert gathered == [1, 2, 3]
    print("fetch_all: OK")

    print("\nAll checks passed!")
