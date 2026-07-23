"""
Exercises: Chapter 10 - Iteration, Decorators, and Contexts

Implement each function/class below, then run this file directly to
check your work.

    python exercises/10_iteration_decorators_and_contexts/exercises.py

Each starter raises NotImplementedError until you implement it.
"""

import functools
from contextlib import contextmanager


class CountUp:
    """A custom iterator counting from `start` up to (not including) `stop`."""

    def __init__(self, start, stop):
        self.current = start
        self.stop = stop

    def __iter__(self):
        # TODO: return the right object to make CountUp its own iterator
        raise NotImplementedError

    def __next__(self):
        # TODO: return the next value, or raise StopIteration when done
        raise NotImplementedError


def countdown(start):
    """A generator function yielding `start, start-1, ..., 1` then "Liftoff!"."""
    # TODO: implement using yield (no return value needed)
    raise NotImplementedError


def uppercase(func):
    """A decorator that upper-cases the wrapped function's string result.

    Use functools.wraps so the wrapped function keeps its original
    __name__ and __doc__.
    """
    # TODO: implement this decorator
    raise NotImplementedError


def repeat(times):
    """A decorator factory: repeat(times) returns a decorator.

    The decorated function, when called, returns a list containing its
    result repeated `times` times. Use functools.wraps on the inner
    wrapper.
    """
    # TODO: implement this decorator factory
    raise NotImplementedError


@contextmanager
def temporary_value(mapping, key, value):
    """Temporarily set mapping[key] = value, restoring it afterward.

    Restore the previous value if `key` existed before, or remove `key`
    entirely if it did not -- in both cases, whether the with block
    succeeded or raised.
    """
    # TODO: implement using try/finally around a single yield
    raise NotImplementedError


counted = list(CountUp(1, 4))
assert counted == [1, 2, 3]
try:
    next(iter(CountUp(2, 2)))
    raise AssertionError("expected StopIteration for an empty range")
except StopIteration:
    pass
print("CountUp: OK")

assert list(countdown(3)) == [3, 2, 1, "Liftoff!"]
print("countdown: OK")


@uppercase
def greet(name):
    """Return a greeting."""
    return f"hi, {name}"


assert greet("Ada") == "HI, ADA"
assert greet.__name__ == "greet", "Task: use functools.wraps to preserve __name__"
print("uppercase decorator: OK")


@repeat(times=3)
def make_value():
    return "x"


assert make_value() == ["x", "x", "x"]
assert make_value.__name__ == "make_value", "Task: use functools.wraps in repeat too"
print("repeat decorator factory: OK")

settings = {"mode": "production"}
with temporary_value(settings, "mode", "debug") as active:
    assert active == "debug"
    assert settings == {"mode": "debug"}
assert settings == {"mode": "production"}, "Task: restore the previous value on success"

try:
    with temporary_value(settings, "mode", "debug"):
        raise RuntimeError("simulated failure")
except RuntimeError:
    pass
assert settings == {"mode": "production"}, (
    "Task: restore the previous value even on failure"
)

with temporary_value(settings, "new_key", 1):
    assert settings == {"mode": "production", "new_key": 1}
assert "new_key" not in settings, "Task: remove a key that did not exist before"
print("temporary_value: OK")

print("\nAll checks passed!")
