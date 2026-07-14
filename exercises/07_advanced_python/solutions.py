"""
Solutions: 07 Advanced Python
"""

import functools
from typing import Protocol


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


def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return " | ".join(func(*args, **kwargs) for _ in range(times))

        return wrapper

    return decorator


class CountUp:
    def __init__(self, stop):
        self.stop = stop
        self.next_value = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_value > self.stop:
            raise StopIteration
        value = self.next_value
        self.next_value += 1
        return value


class MessageSender(Protocol):
    def send(self, recipient: str, message: str) -> None: ...


def send_welcome(sender: MessageSender, recipient: str) -> None:
    sender.send(recipient, f"Welcome, {recipient}!")


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
