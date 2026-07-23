"""
Chapter 10, Lesson 4: Decorator Factories and @contextmanager

Purpose: write a decorator *factory* -- a function that returns a
decorator, letting the decorator itself accept arguments -- and write a
generator-based context manager with `contextlib.contextmanager`,
completing the `with`-statement mental model Chapter 7 built with
class-based `__enter__`/`__exit__`.

Prerequisites: Lesson 3 (decorators and wrappers), and Chapter 7's
`with`/`__enter__`/`__exit__` guarantee.

Read this file top to bottom, predict each output, then run it:

    python lessons/10_iteration_decorators_and_contexts/04_decorator_factories_and_contextmanager.py
"""

import functools
from contextlib import contextmanager


def repeat(times):
    """A decorator factory: a function that returns a decorator.

    Calling repeat(3) runs immediately and returns `decorator`; Python
    then applies `decorator` to the function being defined. Only
    `wrapper` runs on each later call to the decorated function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]

        return wrapper

    return decorator


@repeat(times=3)
def greet_once(name):
    """Return a single greeting for `name`."""
    return f"Hi, {name}"


# Step 1: greet_once("Ada") now returns a list of 3 identical results --
# the decorator factory's argument (times=3) shaped what `decorator`
# built, before `greet_once` was ever called.
print("greet_once('Ada'):", greet_once("Ada"))


# Step 2: a generator-based context manager. The code before `yield`
# runs as __enter__ would; the single yielded value is what `as` binds;
# the code after `yield` -- inside `finally` -- runs as __exit__ would,
# on both a normal exit and an exception, exactly like Chapter 7's
# ManagedFile.__exit__.
@contextmanager
def temporary_value(mapping, key, value):
    """Temporarily set `mapping[key] = value`, restoring it afterward.

    Restores the previous value if `key` existed, or removes `key`
    entirely if it did not -- either way, on success or on failure.
    """
    had_key = key in mapping
    previous = mapping.get(key)
    mapping[key] = value
    try:
        yield mapping[key]
    finally:
        # This restoration runs whether the with block finished
        # normally or raised -- `finally` inside a @contextmanager
        # generator is what provides that guarantee.
        if had_key:
            mapping[key] = previous
        else:
            del mapping[key]


settings = {"mode": "production"}

# Step 3: cleanup after a successful block.
with temporary_value(settings, "mode", "debug") as active_mode:
    print("\nInside the with block, mode is:", active_mode)
    print("settings dict during the block:", settings)
print("After the with block, mode is restored:", settings)

# Step 4: cleanup after a failing block. The restoration still happens,
# and the exception still propagates afterward -- neither guarantee is
# sacrificed for the other.
try:
    with temporary_value(settings, "mode", "debug"):
        raise RuntimeError("simulated failure while mode is temporarily changed")
except RuntimeError as error:
    print("\nCaught the propagated error:", error)
print("settings restored even after failure:", settings)

# Step 5: a key that did not exist before is removed afterward, not left
# behind with some placeholder value.
with temporary_value(settings, "feature_flag", True):
    print("\nDuring the block:", settings)
print("Key removed afterward:", "feature_flag" in settings)

# --- One-variable experiment -------------------------------------------
# Change the `finally:` block's restoration logic to omit the
# `if had_key:` check (always doing `mapping[key] = previous`) and
# predict what settings looks like after the Step 5 block, where
# "feature_flag" had no previous value at all.
