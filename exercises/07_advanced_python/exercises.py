"""
Exercises: 07 Advanced Python

Implement each item below, then run this file directly to check your
work.
"""

import functools
from typing import Protocol


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


def repeat(times):
    """Return a decorator that joins `times` string results with ' | '."""
    # TODO: implement this decorator factory with functools.wraps
    raise NotImplementedError


class CountUp:
    """An iterator yielding 1 through stop, then raising StopIteration."""

    def __init__(self, stop):
        # TODO: store stop and initialize the next value
        raise NotImplementedError

    def __iter__(self):
        # TODO: return this iterator
        raise NotImplementedError

    def __next__(self):
        # TODO: return the next value or raise StopIteration
        raise NotImplementedError


class MessageSender(Protocol):
    def send(self, recipient: str, message: str) -> None: ...


def send_welcome(sender: MessageSender, recipient: str) -> None:
    """Send a welcome message through an injected protocol."""
    # TODO: call sender.send with a useful message
    raise NotImplementedError


class RecordingSender:
    def __init__(self):
        self.messages = []

    def send(self, recipient, message):
        self.messages.append((recipient, message))


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

    repeated_greet = repeat(3)(greet)
    assert repeated_greet("Ada") == "hello, Ada | hello, Ada | hello, Ada"
    assert repeated_greet.__name__ == "greet"
    print("repeat decorator factory: OK")

    assert list(CountUp(4)) == [1, 2, 3, 4]
    assert list(CountUp(0)) == []
    print("CountUp iterator: OK")

    sender = RecordingSender()
    send_welcome(sender, "Grace")
    assert sender.messages == [("Grace", "Welcome, Grace!")]
    print("Protocol and dependency injection: OK")

    print("\nAll checks passed!")
