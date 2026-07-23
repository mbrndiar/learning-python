"""
Chapter 10, Lesson 3: Decorators and Wrappers

Purpose: write a decorator -- a function that wraps another function to
add behavior without changing its source -- and use `functools.wraps` so
the wrapped function still reports its original name and docstring.

Prerequisites: Lesson 2 (generators and lazy evaluation), and functions as
first-class values from earlier chapters (a function can be passed as an
argument and returned from another function).

Read this file top to bottom, predict each output, then run it:

    python lessons/10_iteration_decorators_and_contexts/03_decorators_and_wrappers.py
"""

import functools


def uppercase(func):
    """A decorator: transform the return value of `func` to upper case."""

    # `wrapper` adds one call layer around `func`. functools.wraps copies
    # func's __name__/__doc__ onto wrapper and sets wrapper.__wrapped__,
    # so introspection tools can still reach the original function.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()

    return wrapper


@uppercase
def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"


# Step 1: `@uppercase` above ran when Python executed the `def greet`
# statement -- it is exactly equivalent to `greet = uppercase(greet)`,
# executed once, before this line runs.
print(greet("Ada"))
print("greet.__name__ (preserved by functools.wraps):", greet.__name__)
print("greet.__doc__ (preserved too):", greet.__doc__)


def count_calls(func):
    """A decorator that counts how many times the wrapped function ran."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # `wrapper.calls` lives on the wrapper function object itself --
        # a decorator's wrapper can hold state between calls this way,
        # since each decorated function gets its own wrapper closure.
        wrapper.calls += 1
        return func(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


@count_calls
def add(a, b):
    """Add two numbers."""
    return a + b


# Step 2: state attached to the wrapper persists across calls to the
# decorated function, without any global variable.
print("\nadd(2, 3):", add(2, 3))
print("add(4, 5):", add(4, 5))
print("add.calls:", add.calls)

# --- One-variable experiment -------------------------------------------
# Remove the `@functools.wraps(func)` line from uppercase and predict
# what `greet.__name__` prints afterward. Without it, `wrapper` itself
# (not `greet`) is the function object being introspected, so its name
# and docstring would be `wrapper`'s, not the original `greet`'s.
