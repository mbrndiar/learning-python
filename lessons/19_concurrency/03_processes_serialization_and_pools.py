"""Lesson 19.3: Processes, serialization, and pools.

Purpose:
    Run CPU-bound Python across separate interpreters, and pay the price that
    buys: separate memory and a serialization boundary. You will see why worker
    callables and their arguments must be *picklable and importable*, own a
    process pool explicitly through a context manager, and read back results in
    input order. The pool is created with an explicit ``spawn`` context so the
    behavior is identical on Python 3.11 and 3.14.

Prerequisites:
    - Lesson 1's model: processes are the answer for *CPU-bound* work, because
      Lesson 2's threads cannot run Python bytecode in parallel.
    - The ``with`` statement and resource ownership (Chapter 7): a pool owns OS
      processes and must be shut down.
    - Pickling is the same serialization idea as JSON boundaries (Chapter 8),
      applied to Python objects crossing between interpreters.

Key portability facts this lesson encodes:
    - As of Python 3.14, ``fork`` is no longer the default start method on any
      platform. This lesson always requests ``spawn`` explicitly, so a fresh
      interpreter starts each worker on every supported version.
    - A ``spawn`` worker re-imports this module, so all pool creation lives
      under ``if __name__ == "__main__"``. Otherwise each worker would try to
      build its own pool and recurse.

The lesson is deterministic and offline and asserts no speedups. Parallel CPU
work *can* be faster on multiple cores, but startup and serialization cost can
erase that for small inputs, so we verify ordering and isolation instead.
"""

from __future__ import annotations

import multiprocessing
import pickle
from concurrent.futures import ProcessPoolExecutor


def square(value: int) -> int:
    """A top-level, importable worker: exactly what a process pool can run.

    Because it is defined at module scope, a spawned interpreter can import it
    by name to reconstruct the call. A lambda or a function defined inside
    another function cannot be reached this way (see Step 1).
    """
    return value * value


def append_marker(values: list[int]) -> int:
    """Mutate the received list and report its new length.

    The argument arrives as an independent copy rebuilt from pickled bytes, so
    mutating it here cannot touch the caller's list. This is how "separate
    memory" shows up in practice.
    """
    values.append(-1)
    return len(values)


def is_picklable(obj: object) -> bool:
    """Return whether ``obj`` survives a pickle round-trip.

    Process arguments, results, and the worker callable itself all cross this
    boundary. Anything that fails here cannot be sent to a worker.
    """
    try:
        pickle.loads(pickle.dumps(obj))
    except (pickle.PicklingError, AttributeError, TypeError):
        return False
    return True


def map_in_spawn_pool(numbers: list[int], workers: int) -> list[int]:
    """Square each number in an explicitly owned spawn pool, order preserved.

    ``executor.map`` yields results in the order of the *inputs*, not the order
    in which workers happen to finish. The ``with`` block shuts the pool down
    (joining its worker processes) even if the body raises.
    """
    # Request spawn explicitly for identical semantics on 3.11 and 3.14.
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        # list() drains the lazy map while the pool is still open.
        return list(executor.map(square, numbers))


def run_isolated_mutation(original: list[int], workers: int) -> tuple[int, list[int]]:
    """Send a list to a worker that mutates it; return the worker result and
    the caller's untouched original.

    The returned original proves the mutation stayed in the child interpreter.
    """
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        worker_length = executor.submit(append_marker, original).result()
    return worker_length, original


def main() -> None:
    # Step 1: the serialization boundary decides what a worker can be.
    print("Step 1: workers and arguments cross a pickle boundary")
    assert is_picklable(square) is True  # top-level function: importable
    assert is_picklable([1, 2, 3]) is True  # plain data: fine
    assert is_picklable(lambda value: value) is False  # lambda: not importable
    print("  top-level function and plain data are picklable; a lambda is not")

    # Step 2: own a spawn pool and read results in input order.
    print("\nStep 2: an explicitly owned spawn pool, ordered results")
    numbers = [0, 1, 2, 3, 4, 5]
    squared = map_in_spawn_pool(numbers, workers=2)
    assert squared == [0, 1, 4, 9, 16, 25]  # positional, not completion, order
    print(f"  squares in input order: {squared}")

    # Step 3: separate memory -- the worker mutated a copy, not our list.
    print("\nStep 3: process memory is separate")
    original = [10, 20, 30]
    worker_length, returned_original = run_isolated_mutation(original, workers=2)
    assert worker_length == 4  # the child appended to its own copy
    assert returned_original == [10, 20, 30]  # ours is untouched
    print(f"  worker saw length {worker_length}; our list is still {original}")

    # Step 4: ownership and the absence of a timing claim.
    print("\nStep 4: ownership and honesty about speed")
    print("  the 'with' block shut the pool down and joined its workers")
    print("  all pool creation stayed under __main__, so spawn did not recurse")
    print("  we verified ordering and isolation, not a wall-clock speedup")


if __name__ == "__main__":
    main()
