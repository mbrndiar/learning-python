"""
Chapter 7, Lesson 1: Exception Flow

Purpose: trace how an exception propagates up the call stack until
something catches it; narrow `except` clauses; the `else` and `finally`
clauses of `try`; re-raising with a bare `raise`; and exception chaining
with `raise ... from ...`.

Prerequisites: Chapters 1-6 (values through modules/packages). This is the
first lesson in the whole course to use `try`/`except` as its own subject.

Read this file top to bottom, predict each output, then run it:

    python lessons/07_exceptions_files_and_paths/01_exception_flow.py
"""

import traceback


# Step 1: raising an exception immediately stops normal execution and
# starts unwinding the call stack, one frame at a time, until a matching
# `except` is found (or the program ends, printing an unhandled
# traceback). Each function below adds one more frame to that stack.
def inner():
    raise ValueError("something inner went wrong")


def middle():
    inner()  # no try here -- ValueError simply keeps propagating outward


def outer():
    try:
        middle()
    except ValueError as error:
        print("Caught in outer():", error)
        # error.__traceback__ records every frame the exception passed
        # through on its way up -- middle() and inner() both appear here,
        # even though outer() is the only place with a try/except.
        frames = traceback.extract_tb(error.__traceback__)
        print("Frames the exception passed through:", [frame.name for frame in frames])


outer()


# Step 2: a narrow `except` names the specific exception type(s) it can
# recover from. A bare `except:` (or `except Exception:`) also swallows
# unrelated bugs -- a typo causing NameError, for instance -- which then
# fail silently instead of surfacing as a real defect.
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        # This handler recovers from exactly the failure it names. Any
        # other exception (a TypeError from a non-numeric argument, say)
        # still propagates normally, which is the correct behavior here.
        return None


print("\nsafe_divide(10, 2):", safe_divide(10, 2))
print("safe_divide(10, 0):", safe_divide(10, 0))

# Multiple except clauses (or one tuple of types) handle distinct failures
# distinctly, instead of collapsing them into one generic branch.
for numerator, denominator in [(10, 2), (10, 0), ("10", 2)]:
    try:
        result = numerator / denominator
    except ZeroDivisionError:
        print(f"  {numerator}/{denominator}: division by zero")
    except TypeError:
        print(f"  {numerator}/{denominator}: incompatible types")
    else:
        # Step 3: `else` runs only when the try block completed without
        # raising. Code that should run on success, but that you do NOT
        # want the except clauses to also catch errors from, belongs here
        # rather than at the end of the try block.
        print(f"  {numerator}/{denominator} = {result}")
    finally:
        # Step 4: `finally` runs unconditionally -- after the try block, or
        # after whichever except/else clause ran -- whether or not an
        # exception occurred. It is for cleanup that must always happen.
        print(f"  (checked {numerator}/{denominator})")


# Step 5: `raise` with no argument, used inside an except block, re-raises
# the exception currently being handled -- unchanged, with its original
# traceback intact. This is useful for logging or partial cleanup before
# letting the original failure continue propagating.
def load_config_value(raw):
    try:
        return int(raw)
    except ValueError:
        print(f"\n  logging: could not parse config value {raw!r}")
        raise  # re-raise the same ValueError; do not swallow it here


try:
    load_config_value("not-a-number")
except ValueError as error:
    print("  caller still sees the original error:", error)


# Step 6: exception chaining. `raise NewError(...) from original` attaches
# the original exception as `__cause__`, so both are visible: readers see
# the *translated* error your code raised on purpose, and the *original*
# low-level error that triggered it.
def parse_amount(text):
    try:
        return int(text)
    except ValueError as error:
        raise ValueError(f"amount must be a whole number: {text!r}") from error


try:
    parse_amount("many")
except ValueError as error:
    print("\nTranslated error:", error)
    print("  original cause:", type(error.__cause__).__name__, "-", error.__cause__)

# --- One-variable experiment -------------------------------------------
# Change `raise ValueError(...) from error` to plain `raise ValueError(...)`
# (no `from`) and predict what `error.__cause__` becomes. Python still
# records the earlier exception as `__context__` automatically whenever a
# new exception is raised inside an except block -- `from` only promotes
# that implicit context to an explicit, documented `__cause__`.
