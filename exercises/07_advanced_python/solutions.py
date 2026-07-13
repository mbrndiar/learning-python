"""
Solutions: 07 Advanced Python
"""

import functools


def uppercase_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()

    return wrapper


def countdown(n):
    while n > 0:
        yield n
        n -= 1


def annotate(name: str, age: int) -> str:
    return f"{name} is {age} years old"


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
