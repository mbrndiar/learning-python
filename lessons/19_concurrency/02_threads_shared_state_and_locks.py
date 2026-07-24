"""Lesson 19.2: Threads, shared state, and locks.

Purpose:
    Own an in-process thread from construction to join, reason about the shared
    memory that makes threads convenient *and* dangerous, and use a ``Lock`` to
    protect a complete invariant. Every hazard here is shown *deterministically*
    -- a ``threading.Barrier`` forces a specific interleaving, so the lost
    update is reproduced on purpose rather than hoped for.

Prerequisites:
    - Lesson 1's workload model: threads target overlapping *blocking I/O*, not
      CPU-bound Python (Lesson 3 covers that).
    - Exceptions and ``try``/``except`` (Chapter 7): a thread's exception does
      not reach the code that started it, so you must capture it yourself.
    - Mutable mappings and aliasing (Chapter 3): every thread sees the same
      objects, so an unguarded read-modify-write can interleave and lose data.

This lesson is deterministic and offline and makes no timing assertions. To
*prove* that threads overlap, it uses a barrier every worker must reach before
any may proceed: if the workers were secretly serialized, the barrier would
deadlock instead of releasing.
"""

from __future__ import annotations

import threading


def start_all_then_join_all(threads: list[threading.Thread]) -> None:
    """Start every thread, then join every thread.

    The two loops must stay separate. Starting and immediately joining one
    thread before starting the next would run them one at a time -- correct,
    but sequential. Start-all-then-join-all is the shape that actually overlaps.
    """
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def demonstrate_overlap(worker_count: int) -> int:
    """Prove real overlap with a barrier instead of a timer.

    Each worker waits at a ``Barrier`` sized to the whole group. ``wait()``
    only returns once *all* workers have arrived, so a return value proves they
    were alive at the same time. A serialized run could never assemble the full
    party and would raise ``BrokenBarrierError`` on timeout.
    """
    barrier = threading.Barrier(worker_count)
    arrivals: list[int] = []
    lock = threading.Lock()

    def worker(index: int) -> None:
        # A finite timeout is a *deadlock guard*, never a speed claim: if the
        # group can rendezvous the wait returns immediately.
        barrier.wait(timeout=5.0)
        with lock:
            arrivals.append(index)

    threads = [
        threading.Thread(target=worker, args=(index,)) for index in range(worker_count)
    ]
    start_all_then_join_all(threads)
    return len(arrivals)


def demonstrate_exception_isolation() -> tuple[bool, list[BaseException]]:
    """Show that a worker's exception does not propagate to the starter.

    ``join()`` returns normally even when the target raised. If you want the
    failure, the worker must store it and the owner must re-raise it. Returning
    the captured list here models exactly that capture step.
    """
    captured: list[BaseException] = []

    def failing_worker() -> None:
        try:
            raise ValueError("worker failed")
        except ValueError as error:
            # Store, do not print-and-swallow: the owner decides what to do.
            captured.append(error)

    thread = threading.Thread(target=failing_worker)
    thread.start()
    thread.join()
    # The main thread reached here untouched; the error is only visible because
    # the worker deliberately handed it back.
    reached_here = True
    return reached_here, captured


def demonstrate_lost_update() -> int:
    """Reproduce a lost update *deterministically* with a barrier.

    Two workers each want to add 1 to a shared counter, so the correct final
    value is 2. Both read the value, then a ``Barrier`` blocks until both have
    read, then both write ``old + 1``. Because both read 0, both write 1, and
    one increment is silently lost. The result is a guaranteed 1 -- the race is
    forced, not sampled.
    """
    counter = {"value": 0}
    barrier = threading.Barrier(2)

    def unsynchronized_increment() -> None:
        current = counter["value"]  # read
        barrier.wait(timeout=5.0)  # force both reads to happen before any write
        counter["value"] = current + 1  # write a stale value

    threads = [threading.Thread(target=unsynchronized_increment) for _ in range(2)]
    start_all_then_join_all(threads)
    return counter["value"]


def safe_increment_total(worker_count: int, per_worker: int) -> int:
    """Increment a shared counter under a lock and keep the invariant exact.

    The lock makes each read-modify-write *atomic with respect to other
    threads*: the whole ``value = value + 1`` runs without interleaving. With
    ``worker_count`` workers each adding ``per_worker`` times, the total is
    exactly their product. The Global Interpreter Lock does not provide this --
    an unlocked version could still lose updates. The GIL is not a
    synchronization tool; the ``Lock`` is.
    """
    counter = {"value": 0}
    lock = threading.Lock()

    def worker() -> None:
        for _ in range(per_worker):
            with lock:
                counter["value"] = counter["value"] + 1

    threads = [threading.Thread(target=worker) for _ in range(worker_count)]
    start_all_then_join_all(threads)
    return counter["value"]


def locked_transfer_total(transfers: int) -> tuple[int, int, int]:
    """Move money between two accounts under a lock and conserve the total.

    A transfer touches *two* balances; the invariant is the pair, not one
    field. The lock must cover the whole debit-and-credit so no other thread
    observes or interleaves a half-finished transfer. The returned total must
    equal the starting total no matter how the threads interleave.
    """
    balances = {"a": 100, "b": 0}
    lock = threading.Lock()

    def move_one() -> None:
        with lock:
            # Debit and credit are one indivisible step under the lock.
            balances["a"] -= 1
            balances["b"] += 1

    # Only run transfers we can afford, so the example stays valid.
    affordable = min(transfers, 100)
    threads = [threading.Thread(target=move_one) for _ in range(affordable)]
    start_all_then_join_all(threads)
    return balances["a"], balances["b"], balances["a"] + balances["b"]


def main() -> None:
    # Step 1: construct, start-all, join-all, and prove overlap with a barrier.
    print("Step 1: threads overlap (proven by a barrier, not a clock)")
    arrived = demonstrate_overlap(worker_count=4)
    assert arrived == 4
    print(f"  all {arrived} workers rendezvoused at the barrier together")

    # Step 2: shared memory is convenient; worker exceptions are not automatic.
    print("\nStep 2: a worker's exception does not reach the starter")
    reached_here, captured = demonstrate_exception_isolation()
    assert reached_here is True
    assert len(captured) == 1 and isinstance(captured[0], ValueError)
    print("  join() returned normally; the error was only seen once captured")

    # Step 3: the hazard, made deterministic.
    print("\nStep 3: an unguarded read-modify-write loses an update")
    lost = demonstrate_lost_update()
    assert lost == 1  # correct value is 2; the barrier forces the loss
    print(f"  two +1 workers, guarded by nothing -> counter = {lost} (want 2)")

    # Step 4: a lock protects the complete invariant.
    print("\nStep 4: a lock keeps the invariant exact")
    total = safe_increment_total(worker_count=8, per_worker=1000)
    assert total == 8 * 1000
    print(f"  8 x 1000 locked increments -> {total} (exact)")
    account_a, account_b, conserved = locked_transfer_total(transfers=100)
    assert conserved == 100  # money is neither created nor destroyed
    print(f"  100 locked transfers -> a={account_a} b={account_b} total={conserved}")
    print("  the GIL did not do this; the lock did")


if __name__ == "__main__":
    main()
