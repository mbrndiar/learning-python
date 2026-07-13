"""
Lesson 7.1: Decorators

A decorator is a function that wraps another function (or class) to add
extra behavior without modifying its source code. Decorators are a
direct application of closures and higher-order functions.
"""

import functools
import time


def uppercase_result(func):
    """A simple decorator: transform the return value of `func`."""

    @functools.wraps(func)  # preserves func's name/docstring for introspection
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()

    return wrapper


def repeat(times):
    """A decorator factory: a function that returns a decorator.

    This pattern lets a decorator accept its own arguments (here, `times`).
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results

        return wrapper

    return decorator


def timer(func):
    """A practical decorator: measure and print how long `func` takes to run."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  {func.__name__} took {elapsed:.6f} seconds")
        return result

    return wrapper


@uppercase_result
def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"


@repeat(times=3)
def roll_die():
    """Simulate rolling a die once."""
    import random

    return random.randint(1, 6)


@timer
def sum_up_to(n):
    """Sum all integers from 1 to n."""
    return sum(range(1, n + 1))


if __name__ == "__main__":
    # `@uppercase_result` above `greet` is equivalent to:
    #   greet = uppercase_result(greet)
    print(greet("Ada"))
    print("greet.__name__ (preserved by functools.wraps):", greet.__name__)

    print("\nroll_die() called 3 times:", roll_die())

    print("\nTiming a function call:")
    total = sum_up_to(1_000_000)
    print("  result:", total)
