"""
Exercises: 07 Advanced Python

Implement each item below, then run this file directly to check your
work.
"""

import functools


def uppercase_decorator(func):
    """A decorator that converts the wrapped function's string result
    to uppercase. Remember to use functools.wraps."""
    # TODO: implement this decorator
    raise NotImplementedError


def countdown(n):
    """A generator that yields n, n-1, ..., 1 (inclusive), using `yield`."""
    # TODO: implement this generator function
    raise NotImplementedError


def annotate(name: str, age: int) -> str:
    """Return a string like "Ada is 36 years old", using the type-hinted
    parameters above."""
    # TODO: implement this function
    raise NotImplementedError


def greet(name):
    return f"hello, {name}"


if __name__ == "__main__":
    decorated_greet = uppercase_decorator(greet)
    assert decorated_greet("ada") == "HELLO, ADA"
    assert decorated_greet.__name__ == "greet"  # functools.wraps preserved the name
    print("uppercase_decorator: OK")

    assert list(countdown(3)) == [3, 2, 1]
    print("countdown generator: OK")

    assert annotate("Ada", 36) == "Ada is 36 years old"
    print("annotate: OK")

    print("\nAll checks passed!")
