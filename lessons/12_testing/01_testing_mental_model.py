"""
Chapter 12, Lesson 1: The Testing Mental Model

Purpose: describe what an automated test actually checks (observable
behavior at a boundary, not private implementation), structure a test as
arrange-act-assert, and explain why a test must be deterministic to be
trustworthy.

Prerequisites: Chapters 1-11. This lesson only uses functions, classes,
and exceptions you already know; the testing frameworks themselves arrive
in Lessons 2-4.

This lesson runs as an ordinary script so you can read its reasoning:

    python lessons/12_testing/01_testing_mental_model.py
"""

from collections.abc import Sequence


# Step 1: the code under test. `average` has one observable behavior worth
# pinning down (it returns the mean) and one failure path worth pinning
# down (an empty sequence has no mean). A test targets *these*, not the
# fact that the body happens to call sum() and len().
def average(values: Sequence[float]) -> float:
    """Return the arithmetic mean, raising ValueError for empty input."""
    if not values:
        raise ValueError("average() needs at least one value")
    return sum(values) / len(values)


# Step 2: a test is just code that arranges an input, acts by calling the
# behavior, and asserts on the observable result. Written out by hand, the
# arrange-act-assert (AAA) shape is obvious. Frameworks in later lessons
# remove the boilerplate but keep this exact structure.
def check_average_of_two_values() -> None:
    values = [10.0, 20.0]  # arrange: a small, fully determined input
    result = average(values)  # act: call the behavior once
    assert result == 15.0, f"expected 15.0, got {result}"  # assert


# Step 3: boundaries and failure paths deserve their own cases. Testing
# only the happy path leaves the most bug-prone code (edge conditions)
# unchecked. Here the observable behavior is "raises ValueError", so the
# assertion is about the exception, not a return value.
def check_average_rejects_empty() -> None:
    try:
        average([])
    except ValueError:
        return  # the promised behavior happened
    raise AssertionError("average([]) should have raised ValueError")


# Step 4: determinism. A test that depends on the wall clock, a random
# number, a network response, or dictionary iteration order can pass today
# and fail tomorrow without any code change, which destroys trust. Pin
# every input. Below, sorting makes the observable result independent of
# the set's iteration order.
def distinct_sorted(values: Sequence[str]) -> list[str]:
    """Return unique values in a deterministic, presentation-ready order."""
    return sorted(set(values))


def check_distinct_sorted_is_deterministic() -> None:
    # The same input must always produce the same output for the assertion
    # below to be meaningful on every run and every machine.
    assert distinct_sorted(["b", "a", "b", "c", "a"]) == ["a", "b", "c"]


def main() -> None:
    print("Running arrange-act-assert checks by hand (no framework yet):")
    checks = (
        check_average_of_two_values,
        check_average_rejects_empty,
        check_distinct_sorted_is_deterministic,
    )
    for check in checks:
        check()
        print(f"  PASSED: {check.__name__}")

    print(
        "\nWhat each check pinned down:\n"
        "  - a representative normal case (the mean of two values);\n"
        "  - a boundary/failure path (empty input raises ValueError);\n"
        "  - a deterministic result independent of set iteration order.\n"
        "None of them asserted that average() uses sum() or len(); that is\n"
        "an implementation detail you should be free to change."
    )


if __name__ == "__main__":
    main()
