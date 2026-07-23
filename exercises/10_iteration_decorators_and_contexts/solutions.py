"""
Solutions: Chapter 10 - Iteration, Decorators, and Contexts

Reference solutions for
exercises/10_iteration_decorators_and_contexts/exercises.py.

Run this file directly:

    python exercises/10_iteration_decorators_and_contexts/solutions.py
"""

import functools
from contextlib import contextmanager


class CountUp:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


def countdown(start):
    while start > 0:
        yield start
        start -= 1
    yield "Liftoff!"


def uppercase(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()

    return wrapper


def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]

        return wrapper

    return decorator


@contextmanager
def temporary_value(mapping, key, value):
    had_key = key in mapping
    previous = mapping.get(key)
    mapping[key] = value
    try:
        yield mapping[key]
    finally:
        if had_key:
            mapping[key] = previous
        else:
            del mapping[key]


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
