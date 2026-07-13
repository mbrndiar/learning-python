"""
Lesson 9.2: Debugging and Reading Tracebacks

Bugs are inevitable. Learning to read a traceback and use basic debugging
tools quickly turns confusing errors into solvable puzzles.
"""

import traceback


def divide(a, b):
    return a / b


def average(numbers):
    """Deliberately buggy for numbers=[] to demonstrate a traceback."""
    return sum(numbers) / len(numbers)


def demo_traceback():
    """Show what a traceback looks like and how to read it, without
    crashing the whole script."""
    try:
        divide(1, 0)
    except ZeroDivisionError:
        print("--- Example traceback (caught, not fatal) ---")
        traceback.print_exc()
        print("--- end traceback ---")
        print(
            "\nHow to read it: the last line names the exception type and "
            "message. The lines above show the 'call stack' - each frame "
            "is a function call, read top to bottom in the order they "
            "were entered, with the deepest call (where the error "
            "actually happened) at the bottom."
        )


def demo_common_errors():
    """A few of the most common beginner errors, caught and explained."""
    examples = []

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
        None.upper()
    except AttributeError as error:
        examples.append(("AttributeError", error))

    print("\nCommon errors and what they mean:")
    for name, error in examples:
        print(f"  {name}: {error}")


def demo_debugger_hint():
    """Explain how to pause execution and inspect state interactively."""
    print(
        "\nWhen print statements aren't enough, drop into an interactive "
        "debugger. Add this line where you want to pause:\n"
        "    breakpoint()\n"
        "Then use debugger commands: 'n' (next line), 's' (step into a "
        "call), 'p variable_name' (print a value), 'c' (continue), "
        "'q' (quit)."
    )


if __name__ == "__main__":
    demo_traceback()
    demo_common_errors()
    demo_debugger_hint()
