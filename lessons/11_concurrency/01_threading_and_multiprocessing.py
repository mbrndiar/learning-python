"""
Lesson 11.1: Threading and Multiprocessing

Python offers two standard-library ways to run work concurrently:
- `threading` - multiple threads in one process, best for I/O-bound work
  (network requests, file access). Traditional GIL-enabled CPython builds
  generally do not execute CPU-bound Python bytecode in parallel across
  threads; free-threaded builds have different execution characteristics.
- `multiprocessing` - multiple separate processes, best for CPU-bound
  work, since workers use separate Python interpreters and memory.
"""

import multiprocessing
import threading
import time


def io_bound_task(name, delay):
    """Simulate I/O-bound work (e.g. waiting on a network response)."""
    # sleep blocks this thread but releases execution so other threads can make
    # progress, which models waiting for external I/O.
    time.sleep(delay)
    print(f"  Task {name} finished after {delay}s")


def cpu_bound_task(n):
    """Simulate CPU-bound work: sum of squares up to n."""
    return sum(i * i for i in range(n))


def run_with_threads():
    print("Running I/O-bound tasks with threads:")
    start = time.perf_counter()
    threads = [
        threading.Thread(target=io_bound_task, args=(f"T{i}", 0.2)) for i in range(3)
    ]
    # start() schedules every thread before join() waits for completion. Joining
    # immediately after each start would accidentally serialize the work.
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"  Total time: {time.perf_counter() - start:.2f}s (ran concurrently)")


def run_with_processes():
    print("\nRunning CPU-bound tasks with a process pool:")
    start = time.perf_counter()
    # Pool sends arguments to separate worker processes. That enables parallel
    # CPU work but requires serializable data and adds process startup/IPC cost.
    with multiprocessing.Pool(processes=2) as pool:
        results = pool.map(cpu_bound_task, [200_000, 200_000])
    print(f"  Results: {results}")
    print(f"  Total time: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    run_with_threads()
    # multiprocessing.Pool requires the module-level guard below on some
    # platforms (notably Windows), which is why this call sits inside
    # `if __name__ == "__main__":`.
    run_with_processes()
