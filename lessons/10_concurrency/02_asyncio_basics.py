"""
Lesson 10.2: asyncio Basics

`asyncio` provides single-threaded, cooperative concurrency using
`async`/`await`. It's ideal for many I/O-bound tasks (network calls,
file access) running at once without the overhead of threads or
processes.
"""

import asyncio
import time


async def fetch_data(name, delay):
    """Simulate an I/O-bound operation, e.g. an HTTP request."""
    print(f"  Starting {name}...")
    await asyncio.sleep(delay)  # non-blocking "wait" - other tasks can run
    print(f"  Finished {name} after {delay}s")
    return f"{name} result"


async def main():
    start = time.perf_counter()

    # Running tasks sequentially (slow: awaits block one after another)
    print("Sequential (awaiting one at a time):")
    await fetch_data("A", 0.2)
    await fetch_data("B", 0.2)
    print(f"  Sequential total: {time.perf_counter() - start:.2f}s\n")

    # Running tasks concurrently with asyncio.gather
    start = time.perf_counter()
    print("Concurrent (asyncio.gather):")
    results = await asyncio.gather(
        fetch_data("C", 0.2),
        fetch_data("D", 0.2),
    )
    print(f"  Results: {results}")
    print(f"  Concurrent total: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    # asyncio.run() creates an event loop, runs the coroutine to
    # completion, then closes the loop.
    asyncio.run(main())
