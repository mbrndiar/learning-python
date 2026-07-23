"""
Chapter 13, Lesson 1: Tracebacks and pdb

Purpose: read a traceback from the bottom up, recognize the most common
exception types, and know the standard debugger commands for pausing a
program and inspecting its state.

Prerequisites: Chapter 7 (exceptions) and Chapter 12 (you will turn a
diagnosed bug into a regression test). This lesson never launches the
interactive debugger for you; it prints the exact commands to try so the
lesson stays deterministic and non-blocking.

Run it from the repository root:

    python lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py
"""

import sys
import traceback


def average(numbers: list[float]) -> float:
    """Deliberately buggy for numbers=[] to produce a traceback."""
    return sum(numbers) / len(numbers)


# Step 1: capture a real traceback without crashing the whole script. A
# traceback normally goes to stderr; printing this demonstration to stdout
# keeps its frames in a deterministic display order for the lesson.
def demo_traceback() -> None:
    try:
        average([])
    except ZeroDivisionError:
        print("--- Example traceback (caught, not fatal) ---")
        traceback.print_exc(file=sys.stdout)
        print("--- end traceback ---")
        print(
            "\nRead it bottom-up: the last line names the exception type and\n"
            "message. The frames above are the call stack, deepest last. Find\n"
            "the first frame in your own code and inspect the values there."
        )


# Step 2: the handful of exceptions you will meet most often. Each block
# wraps only the operation expected to fail, so the except clause cannot
# accidentally swallow an unrelated bug.
def demo_common_errors() -> None:
    examples: list[tuple[str, Exception]] = []

    try:
        int("not a number")
    except ValueError as error:
        examples.append(("ValueError", error))

    try:
        [1, 2, 3][10]
    except IndexError as error:
        examples.append(("IndexError", error))

    try:
        {"a": 1}["missing"]
    except KeyError as error:
        examples.append(("KeyError", error))

    try:
        None.upper()  # type: ignore[attr-defined]
    except AttributeError as error:
        examples.append(("AttributeError", error))

    print("\nCommon errors and what they mean:")
    for name, error in examples:
        print(f"  {name}: {error}")


# Step 3: how to investigate interactively. Do not leave a breakpoint in
# committed code; use it while diagnosing, then remove it.
def demo_debugger_hint() -> None:
    print(
        "\nInvestigate the buggy average() call under the standard debugger:\n"
        "  python -m pdb lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py\n"
        "At the (Pdb) prompt, try:\n"
        "  break average   # pause when average() is entered\n"
        "  continue        # run until the breakpoint\n"
        "  p numbers       # print an expression\n"
        "  p len(numbers)  # confirm the failed assumption\n"
        "  where           # show the call stack\n"
        "  quit\n"
        "Other useful commands: n (next line), s (step into), c (continue),\n"
        "l (list source). `breakpoint()` pauses execution from inside code."
    )


if __name__ == "__main__":
    demo_traceback()
    demo_common_errors()
    demo_debugger_hint()
