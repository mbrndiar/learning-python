"""Solutions: Chapter 19 - Concurrent Execution.

Reference implementations for the concurrency exercise. Run this file directly
to execute the same five evaluator groups the starter uses:

    python exercises/19_concurrency/solutions.py

Every check is offline and deterministic. Overlap is proven with barriers and
events -- primitives that deadlock under a wrong implementation -- rather than
with timing, and no check asserts a wall-clock speedup.
"""

from __future__ import annotations

import asyncio
import multiprocessing
import threading
from collections.abc import Awaitable, Callable, Iterator, MutableMapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from types import TracebackType
from typing import Literal, Protocol, TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")

ExecutionModel = Literal["sequential", "threads", "processes", "asyncio"]
WorkloadKind = Literal["blocking-io", "cpu-bound"]


@dataclass(frozen=True)
class Workload:
    """A minimal, explicit description of work to schedule.

    ``operations`` is the number of independent units; ``async_client`` reports
    whether a coroutine-native client exists for a blocking-I/O workload.
    """

    kind: WorkloadKind
    operations: int
    async_client: bool = False


class Lock(Protocol):
    """A context-manager lock, satisfied by ``threading.Lock`` and the fakes."""

    def __enter__(self) -> bool: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
        /,
    ) -> bool | None: ...


# ===========================================================================
# Implementations. Only this region differs between the starter and solution.
# ===========================================================================


def choose_execution_model(workload: Workload) -> ExecutionModel:
    """Map a workload to a deliberate starting model, sequential by default."""
    operations = workload.operations
    if isinstance(operations, bool) or not isinstance(operations, int):
        raise ValueError("operations must be a non-boolean integer")
    if operations < 0:
        raise ValueError("operations must not be negative")
    if workload.kind not in ("blocking-io", "cpu-bound"):
        raise ValueError(f"unknown workload kind: {workload.kind!r}")
    if operations < 2:
        return "sequential"
    if workload.kind == "cpu-bound":
        return "processes"
    if workload.async_client:
        return "asyncio"
    return "threads"


def run_in_threads(func: Callable[[T], R], items: Sequence[T]) -> list[R]:
    """Run ``func`` on every item in its own thread, preserving input order."""
    results: list[R | None] = [None] * len(items)
    errors: list[BaseException | None] = [None] * len(items)

    def worker(index: int, item: T) -> None:
        try:
            results[index] = func(item)
        except Exception as error:  # captured; the owner re-raises in order
            errors[index] = error

    threads = [
        threading.Thread(target=worker, args=(index, item))
        for index, item in enumerate(items)
    ]
    # Start every thread before joining any, so the work actually overlaps.
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    # Re-raise the first failure in input order, so results are never partial.
    for error in errors:
        if error is not None:
            raise error
    return cast("list[R]", results)


def transfer_locked(
    balances: MutableMapping[str, int],
    source: str,
    target: str,
    amount: int,
    lock: Lock,
) -> None:
    """Move ``amount`` from ``source`` to ``target`` under ``lock``."""
    # Argument validation is pure, so it stays outside the lock.
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount must be a non-boolean integer")
    if amount <= 0:
        raise ValueError("amount must be positive")
    # The invariant spans two balances, so the whole check-and-move is one
    # critical section: existence, funds check, debit, and credit together.
    with lock:
        if source not in balances:
            raise KeyError(source)
        if target not in balances:
            raise KeyError(target)
        if balances[source] < amount:
            raise ValueError("insufficient funds")
        balances[source] -= amount
        balances[target] += amount


def map_in_processes(
    func: Callable[[T], R], items: Sequence[T], workers: int = 2
) -> list[R]:
    """Map ``func`` over ``items`` in an owned spawn process pool, in order."""
    if isinstance(workers, bool) or not isinstance(workers, int):
        raise ValueError("workers must be a non-boolean integer")
    if workers < 1:
        raise ValueError("workers must be at least 1")
    if not items:
        return []
    # Request spawn explicitly for identical semantics on 3.11 and 3.14.
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        # map preserves input order; the with-block shuts the pool down.
        return list(executor.map(func, items))


async def async_map(func: Callable[[T], Awaitable[R]], items: Sequence[T]) -> list[R]:
    """Schedule ``func`` for every item concurrently, preserving input order."""
    if not items:
        return []
    # gather schedules each coroutine as a task and returns results in input
    # order; the first exception propagates to the caller.
    return list(await asyncio.gather(*(func(item) for item in items)))


async def async_map_limited(
    func: Callable[[T], Awaitable[R]], items: Sequence[T], limit: int
) -> list[R]:
    """Schedule ``func`` for every item with at most ``limit`` running at once."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("limit must be a non-boolean integer")
    if limit < 1:
        raise ValueError("limit must be positive")
    if not items:
        return []
    semaphore = asyncio.Semaphore(limit)

    async def bounded(item: T) -> R:
        # The semaphore admits at most `limit` holders; the rest wait here.
        async with semaphore:
            return await func(item)

    return list(await asyncio.gather(*(bounded(item) for item in items)))


async def cancel_and_wait(task: asyncio.Task[T]) -> T | None:
    """Request cancellation of ``task`` and await its completion.

    Returns the result if the task already finished successfully, ``None`` if it
    was cancelled, and propagates the exception if it already failed.
    """
    task.cancel()
    try:
        return await task
    except asyncio.CancelledError:
        # Awaiting propagates an owner's cancellation into its child. Check the
        # owner first so that cancellation cannot be mistaken for the request
        # this function sent to `task`.
        owner = asyncio.current_task()
        if owner is not None and owner.cancelling():
            raise
        if task.cancelled():
            return None
        raise


# ===========================================================================
# Shared evaluator, fakes, and top-level process workers (byte-identical
# between the starter and the solution).
# ===========================================================================


def _square(value: int) -> int:
    """Top-level, picklable process worker used by the evaluator."""
    return value * value


def _raise_on_three(value: int) -> int:
    """Top-level worker that fails for a specific input, to prove propagation."""
    if value == 3:
        raise ValueError("no threes allowed")
    return value


def _append_marker(values: list[int]) -> int:
    """Mutate the received list; the caller's copy must stay unchanged."""
    values.append(-1)
    return len(values)


async def _double(value: int) -> int:
    """Top-level async worker used where the body is irrelevant."""
    return value * 2


class TrackingLock:
    """A context-manager lock that records whether it is currently held.

    It performs no real mutual exclusion; the evaluator uses it single-threaded
    to prove every balance access happened inside the lock's scope.
    """

    def __init__(self) -> None:
        self.held = False
        self.enter_count = 0

    def __enter__(self) -> bool:
        self.held = True
        self.enter_count += 1
        return True

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
        /,
    ) -> None:
        self.held = False
        return None


class GuardedBalances(MutableMapping[str, int]):
    """A balances mapping that rejects any access made outside the lock.

    Both reads and writes require ``lock.held``, so a missing lock scope, or a
    lock covering only the writes, fails deterministically without relying on an
    observed thread race.
    """

    def __init__(self, lock: TrackingLock, data: dict[str, int]) -> None:
        self._lock = lock
        self._data = data

    def __getitem__(self, key: str) -> int:
        if not self._lock.held:
            raise AssertionError("balance read outside the lock")
        return self._data[key]

    def __setitem__(self, key: str, value: int) -> None:
        if not self._lock.held:
            raise AssertionError("balance written outside the lock")
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def evaluate_model_selection() -> None:
    assert choose_execution_model(Workload("cpu-bound", 1)) == "sequential"
    assert choose_execution_model(Workload("blocking-io", 1)) == "sequential"
    assert choose_execution_model(Workload("cpu-bound", 8)) == "processes"
    assert choose_execution_model(Workload("blocking-io", 10)) == "threads"
    assert (
        choose_execution_model(Workload("blocking-io", 10, async_client=True))
        == "asyncio"
    )

    # Validation: reject a boolean or negative operation count.
    for invalid in (Workload("cpu-bound", True), Workload("cpu-bound", -1)):
        try:
            choose_execution_model(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{invalid!r} must be rejected")

    # Validation: reject an unknown workload kind.
    try:
        choose_execution_model(Workload(cast("WorkloadKind", "bogus"), 3))
    except ValueError:
        pass
    else:
        raise AssertionError("unknown workload kind must be rejected")


def evaluate_threaded_fan_out() -> None:
    # Order preserved and empty input handled.
    assert run_in_threads(_square, [1, 2, 3, 4]) == [1, 4, 9, 16]
    assert run_in_threads(_square, []) == []

    # Real overlap: every worker must reach the barrier before any is released.
    worker_count = 4
    barrier = threading.Barrier(worker_count)

    def arrive(index: int) -> int:
        # A serialized runner leaves one worker waiting alone -> BrokenBarrier.
        barrier.wait(timeout=5.0)
        return index

    assert run_in_threads(arrive, list(range(worker_count))) == [0, 1, 2, 3]

    # Worker exceptions surface to the caller in input order.
    def fail(value: int) -> int:
        raise ValueError(f"bad {value}")

    try:
        run_in_threads(fail, [10, 11, 12])
    except ValueError as error:
        assert str(error) == "bad 10"  # the first input's error, deterministically
    else:
        raise AssertionError("worker exceptions must propagate")


def evaluate_locked_transfer() -> None:
    lock = threading.Lock()

    # Amount validation rejects booleans and non-positive values; no mutation.
    plain = {"a": 100, "b": 0}
    for bad_amount in (True, 0, -5):
        try:
            transfer_locked(plain, "a", "b", bad_amount, lock)
        except ValueError:
            pass
        else:
            raise AssertionError(f"amount {bad_amount!r} must be rejected")
    assert plain == {"a": 100, "b": 0}

    # Missing accounts raise KeyError; still no mutation.
    for source, target in (("x", "b"), ("a", "y")):
        try:
            transfer_locked(plain, source, target, 10, lock)
        except KeyError:
            pass
        else:
            raise AssertionError("a missing account must raise KeyError")
    assert plain == {"a": 100, "b": 0}

    # Insufficient funds raise before any partial update.
    try:
        transfer_locked(plain, "a", "b", 1000, lock)
    except ValueError:
        pass
    else:
        raise AssertionError("insufficient funds must be rejected")
    assert plain == {"a": 100, "b": 0}

    # Lock-scope enforcement: every balance access must be inside the lock.
    tracking = TrackingLock()
    backing = {"a": 100, "b": 0}
    transfer_locked(GuardedBalances(tracking, backing), "a", "b", 30, tracking)
    assert tracking.enter_count >= 1
    assert backing == {"a": 70, "b": 30}
    assert backing["a"] + backing["b"] == 100  # invariant conserved

    # Real threads under one lock keep the total exact regardless of order.
    shared = {"a": 500, "b": 0}
    real_lock = threading.Lock()

    def move_one() -> None:
        transfer_locked(shared, "a", "b", 1, real_lock)

    movers = [threading.Thread(target=move_one) for _ in range(100)]
    for mover in movers:
        mover.start()
    for mover in movers:
        mover.join()
    assert shared["a"] + shared["b"] == 500  # conserved
    assert shared == {"a": 400, "b": 100}


def evaluate_process_pool() -> None:
    # Ordered results and empty input.
    assert map_in_processes(_square, [0, 1, 2, 3, 4]) == [0, 1, 4, 9, 16]
    assert map_in_processes(_square, []) == []

    # workers validation: reject booleans and non-positive counts.
    for bad_workers in (True, 0, -1):
        try:
            map_in_processes(_square, [1, 2], workers=bad_workers)
        except ValueError:
            pass
        else:
            raise AssertionError(f"workers={bad_workers!r} must be rejected")

    # Worker failures propagate to the caller.
    try:
        map_in_processes(_raise_on_three, [1, 2, 3])
    except ValueError:
        pass
    else:
        raise AssertionError("worker failures must propagate")

    # Process input is copied across the boundary: the caller's list is intact.
    payload = [1, 2, 3]
    assert map_in_processes(_append_marker, [payload]) == [4]
    assert payload == [1, 2, 3]


async def _check_async_map() -> None:
    # Empty input.
    assert await async_map(_double, []) == []

    # Overlap proven by events: no worker finishes until all have started.
    total = 4
    started = 0
    all_started = asyncio.Event()

    async def probe(value: int) -> int:
        nonlocal started
        started += 1
        if started == total:
            all_started.set()
        try:
            await asyncio.wait_for(all_started.wait(), timeout=5.0)
        except TimeoutError:
            raise AssertionError(
                "async_map must schedule all operations concurrently"
            ) from None
        return value * 10

    assert await async_map(probe, [1, 2, 3, 4]) == [10, 20, 30, 40]

    # Failures propagate.
    async def fail(value: int) -> int:
        raise ValueError(f"bad {value}")

    try:
        await async_map(fail, [1, 2, 3])
    except ValueError:
        pass
    else:
        raise AssertionError("async_map must propagate failures")


async def _check_async_map_limited() -> None:
    # Empty input and limit validation.
    assert await async_map_limited(_double, [], limit=2) == []
    for bad_limit in (True, 0, -1):
        try:
            await async_map_limited(_double, [1], limit=bad_limit)
        except ValueError:
            pass
        else:
            raise AssertionError(f"limit={bad_limit!r} must be rejected")

    # Bounded but concurrent: the peak active count equals the limit, no more.
    limit = 2
    total = 5
    active = 0
    peak = 0
    reached_limit = asyncio.Event()
    release = asyncio.Event()

    async def probe(value: int) -> int:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        if active >= limit:
            reached_limit.set()
        await release.wait()
        active -= 1
        return value

    task = asyncio.create_task(async_map_limited(probe, list(range(total)), limit))
    try:
        await asyncio.wait_for(reached_limit.wait(), timeout=5.0)
    except TimeoutError:
        raise AssertionError(
            "async_map_limited must run up to `limit` tasks concurrently"
        ) from None
    release.set()
    assert await task == list(range(total))  # order preserved
    assert peak == limit  # overlapped up to the limit, never beyond it

    # Failures propagate.
    async def fail(value: int) -> int:
        raise ValueError("bad")

    try:
        await async_map_limited(fail, [1, 2, 3], limit=2)
    except ValueError:
        pass
    else:
        raise AssertionError("async_map_limited must propagate failures")


async def _check_cancel_and_wait() -> None:
    # Cancelling a running task: cleanup completes before return, result is None.
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def long_running() -> int:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()
        return 0  # unreachable at runtime; satisfies the return type

    running = asyncio.create_task(long_running())
    await started.wait()
    assert await cancel_and_wait(running) is None
    assert cleaned.is_set()  # the finally ran before cancel_and_wait returned
    assert running.cancelled()

    # An already-completed success is returned, not swallowed.
    async def quick() -> int:
        return 42

    done = asyncio.create_task(quick())
    while not done.done():
        await asyncio.sleep(0)
    assert await cancel_and_wait(done) == 42

    # An already-failed task propagates its exception.
    async def boom() -> int:
        raise ValueError("already failed")

    failed = asyncio.create_task(boom())
    while not failed.done():
        await asyncio.sleep(0)
    try:
        await cancel_and_wait(failed)
    except ValueError:
        pass
    else:
        raise AssertionError("cancel_and_wait must propagate a prior failure")

    # Cancelling the owner while it awaits child cleanup must propagate to the
    # owner rather than being mistaken for the child's requested cancellation.
    victim_started = asyncio.Event()
    first_cancellation_seen = asyncio.Event()

    async def slow_cancellation() -> None:
        victim_started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            first_cancellation_seen.set()
            await asyncio.Event().wait()
            raise

    victim = asyncio.create_task(slow_cancellation())
    await victim_started.wait()
    owner = asyncio.create_task(cancel_and_wait(victim))
    await first_cancellation_seen.wait()
    owner.cancel()
    try:
        await owner
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("cancelling the owner must propagate CancelledError")
    assert owner.cancelled()
    assert victim.cancelled()


def evaluate_async() -> None:
    asyncio.run(_check_async_map())
    asyncio.run(_check_async_map_limited())
    asyncio.run(_check_cancel_and_wait())


def run_evaluation(label: str, evaluation: Callable[[], None]) -> None:
    try:
        evaluation()
    except NotImplementedError as error:
        raise AssertionError(f"{label}: implement the remaining TODO") from error
    print(f"{label}: OK")


if __name__ == "__main__":
    run_evaluation("model selection", evaluate_model_selection)
    run_evaluation("threaded fan-out", evaluate_threaded_fan_out)
    run_evaluation("locked transfer invariant", evaluate_locked_transfer)
    run_evaluation("process pool", evaluate_process_pool)
    run_evaluation("async scheduling, bounding, and cancellation", evaluate_async)
    print("\nAll checks passed!")
