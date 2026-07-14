"""
Lesson 11.2: asyncio Basics

`asyncio` provides cooperative concurrency using async/await. A coroutine
voluntarily yields at an await, allowing other tasks to run. Blocking code
inside a coroutine blocks the event-loop thread, so real programs must use
async-aware I/O libraries or explicitly offload blocking work.
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

    # Each await suspends main until that operation finishes, so these calls
    # do not overlap even though fetch_data itself is asynchronous.
    print("Sequential (awaiting one at a time):")
    await fetch_data("A", 0.2)
    await fetch_data("B", 0.2)
    print(f"  Sequential total: {time.perf_counter() - start:.2f}s\n")

    # gather schedules both coroutine objects and waits for all their results.
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
