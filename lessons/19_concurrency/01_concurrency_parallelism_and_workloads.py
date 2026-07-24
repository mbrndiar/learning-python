"""Lesson 19.1: Concurrency, parallelism, and workloads.

Purpose:
    Build the mental model this whole chapter rests on before touching any
    thread, process, or event loop. You will distinguish *sequential*,
    *concurrent*, and *parallel* execution, tell a *blocking-I/O* workload
    apart from a *CPU-bound* one, and turn that distinction into a small,
    explicit decision contract. The chapter's rule is deliberate: sequential
    code is the default, and adding workers is a response to a bottleneck you
    can name -- never a reflex.

Prerequisites:
    - Functions, annotations, and return contracts (Chapter 5).
    - Dataclasses, enums, and ``Literal`` values (Chapters 9 and 11).
    - Generators and the iterator protocol (Chapter 10); the interleaving demo
      below drives generators by hand as a stand-in for a scheduler.
    - The stable Task project, which motivates fanning out independent HTTP
      calls without changing the domain contract.

This lesson is deterministic and offline. It makes no timing measurements and
asserts no speedups: concurrency changes *how work is scheduled*, not whether
it is inherently faster.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

# The four models this chapter teaches. "sequential" is a first-class answer,
# not the absence of an answer: most programs should stay here.
ExecutionModel = Literal["sequential", "threads", "processes", "asyncio"]

# A workload is either dominated by *waiting* on something external
# (blocking-io) or by *computing* in Python (cpu-bound). This single axis
# drives most of the decision.
WorkloadKind = Literal["blocking-io", "cpu-bound"]


@dataclass(frozen=True)
class Workload:
    """A minimal, explicit description of work to be scheduled.

    Attributes:
        name: A label used only for presentation.
        kind: Whether the work mostly waits (``blocking-io``) or mostly
            computes (``cpu-bound``).
        operations: The number of *independent* units of work. One unit has
            nothing to overlap with, so it stays sequential regardless of kind.
        async_library_available: Whether a coroutine-native client exists for
            this work. Overlapping blocking I/O needs either threads or an
            async library; you cannot get overlap from ``asyncio`` alone if the
            only client you have blocks the event loop.
    """

    name: str
    kind: WorkloadKind
    operations: int
    async_library_available: bool = False


def choose_execution_model(workload: Workload) -> ExecutionModel:
    """Map a workload to a deliberate starting model.

    The contract, in priority order:

    1. Fewer than two independent operations -> ``sequential``. There is nothing
       to overlap, so coordination overhead would only add risk.
    2. CPU-bound work -> ``processes``. Separate interpreters run Python
       bytecode on separate cores; threads cannot (see Lesson 2).
    3. Blocking I/O with a coroutine-native client -> ``asyncio``. One thread
       schedules many awaiting operations cheaply.
    4. Blocking I/O with only synchronous clients -> ``threads``. Each blocking
       call waits on its own thread while the others make progress.

    This is a *starting point*, not a guarantee. The final section explains why
    the answer must still be measured against the real workload.
    """
    if workload.operations < 2:
        return "sequential"
    if workload.kind == "cpu-bound":
        return "processes"
    if workload.async_library_available:
        return "asyncio"
    return "threads"


def make_task_steps(label: str, step_count: int) -> Iterator[str]:
    """Yield the successive step labels of one imaginary task.

    Driving this generator by hand models a task that can be *paused* between
    steps. A real thread or coroutine is paused by the runtime; here we do it
    explicitly so the interleaving is fully deterministic and visible.
    """
    for step in range(1, step_count + 1):
        yield f"{label}{step}"


def run_sequentially(labels: list[str], step_count: int) -> list[str]:
    """Drain each task to completion before starting the next one."""
    trace: list[str] = []
    for label in labels:
        # Each task runs start-to-finish with no interruption: A1 A2 A3 ...
        trace.extend(make_task_steps(label, step_count))
    return trace


def run_concurrently(labels: list[str], step_count: int) -> list[str]:
    """Advance every task one step at a time in a fixed round-robin.

    This is *concurrency*: the tasks' progress overlaps and interleaves, even
    though exactly one step happens at any instant. Nothing here runs in
    parallel -- a single loop, on a single core, produces A1 B1 A2 B2 ...
    Concurrency is a structure for overlapping progress; parallelism is the
    hardware actually doing two things at the same instant.
    """
    generators = [make_task_steps(label, step_count) for label in labels]
    trace: list[str] = []
    active = list(generators)
    while active:
        still_running: list[Iterator[str]] = []
        for generator in active:
            step = next(generator, None)
            if step is not None:
                trace.append(step)
                still_running.append(generator)
        # A finished generator is dropped, so the round-robin naturally shrinks.
        active = still_running
    return trace


def format_decision_table(workloads: list[Workload]) -> str:
    """Render the decision contract over concrete example workloads."""
    header = f"{'workload':<28}{'kind':<14}{'ops':>4}  {'async?':<7}-> model"
    lines = [header, "-" * len(header)]
    for workload in workloads:
        model = choose_execution_model(workload)
        async_flag = "yes" if workload.async_library_available else "no"
        lines.append(
            f"{workload.name:<28}{workload.kind:<14}"
            f"{workload.operations:>4}  {async_flag:<7}-> {model}"
        )
    return "\n".join(lines)


def main() -> None:
    # Step 1: sequential vs concurrent vs parallel.
    # Same two tasks, two schedules. Sequential finishes A before touching B;
    # concurrent interleaves their steps. Same *work*, different *ordering*.
    print("Step 1: one workload, two schedules")
    sequential_trace = run_sequentially(["A", "B"], step_count=3)
    concurrent_trace = run_concurrently(["A", "B"], step_count=3)
    print(f"  sequential order: {' '.join(sequential_trace)}")
    print(f"  concurrent order: {' '.join(concurrent_trace)}")
    # The multiset of steps is identical; only their interleaving differs.
    assert sorted(sequential_trace) == sorted(concurrent_trace)
    assert sequential_trace != concurrent_trace
    print("  same steps, different interleaving (still one core, one at a time)")

    # Step 2: name the workload, then choose a model.
    print("\nStep 2: choosing a model from the workload")
    workloads = [
        Workload("add ten small numbers", "cpu-bound", operations=1),
        Workload("hash many files", "cpu-bound", operations=8),
        Workload("fetch pages (sync client)", "blocking-io", operations=10),
        Workload(
            "fetch pages (async client)",
            "blocking-io",
            operations=10,
            async_library_available=True,
        ),
    ]
    print(format_decision_table(workloads))
    assert choose_execution_model(workloads[0]) == "sequential"
    assert choose_execution_model(workloads[1]) == "processes"
    assert choose_execution_model(workloads[2]) == "threads"
    assert choose_execution_model(workloads[3]) == "asyncio"

    # Step 3: why sequential is the default, and why concurrency is not speed.
    print("\nStep 3: measurement caveats")
    # A single operation has no sibling to overlap with, so every model that
    # adds coordination is pure overhead here.
    single = Workload("one request", "blocking-io", operations=1)
    assert choose_execution_model(single) == "sequential"
    print("  one operation -> sequential (nothing to overlap)")
    print("  concurrency adds scheduling, coordination, and cancellation cost;")
    print("  it can be slower for small or CPU-cheap work. This chapter proves")
    print("  *correctness* (overlap, ordering, cleanup), never a wall-clock win.")


if __name__ == "__main__":
    main()
