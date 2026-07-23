"""
Exercises: Chapter 9 - Objects and Data Models

Implement each class below, then run this file directly to check your
work.

    python exercises/09_object_oriented_programming/exercises.py

Each starter raises NotImplementedError until you implement it.
"""

import dataclasses
from dataclasses import dataclass
from enum import Enum, auto


class Rectangle:
    """A rectangle with a width and height."""

    def __init__(self, width, height):
        # TODO: store width and height on the instance
        raise NotImplementedError

    def area(self):
        """Return width * height."""
        # TODO: implement this method
        raise NotImplementedError

    def perimeter(self):
        """Return 2 * (width + height)."""
        # TODO: implement this method
        raise NotImplementedError


class Square(Rectangle):
    """A square is a rectangle where width == height.

    Reuse Rectangle's __init__ via super() by passing the same side for
    both width and height.
    """

    def __init__(self, side):
        # TODO: call the parent constructor appropriately
        raise NotImplementedError


class Animal:
    """Base class for a coherent "is a" hierarchy -- do not add unrelated
    subclasses that would not truthfully be an Animal."""

    def speak(self):
        raise NotImplementedError("Subclasses must implement speak()")


class Dog(Animal):
    def speak(self):
        # TODO: return "Woof!"
        raise NotImplementedError


class Cat(Animal):
    def speak(self):
        # TODO: return "Meow!"
        raise NotImplementedError


class BankAccount:
    """Expose a read-only balance property, validate deposits, and raise a
    domain-specific error on an over-large withdrawal."""

    def __init__(self, balance=0):
        # TODO: store balance as a non-public instance attribute
        raise NotImplementedError

    @property
    def balance(self):
        # TODO: return the current balance
        raise NotImplementedError

    def deposit(self, amount):
        """Add a positive amount or raise ValueError."""
        # TODO: implement this method
        raise NotImplementedError

    def withdraw(self, amount):
        """Subtract a positive amount not exceeding the balance.

        Raise ValueError for a non-positive amount. Raise
        InsufficientFundsError (defined below) when amount exceeds the
        current balance -- construct it as
        InsufficientFundsError(balance, amount).
        """
        # TODO: implement this method
        raise NotImplementedError


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance.

    Store `balance` and `amount` as attributes (in that order) and pass a
    descriptive message to the parent Exception via super().__init__(...).
    """

    def __init__(self, balance, amount):
        # TODO: store balance and amount, then call super().__init__(...)
        raise NotImplementedError


class Vector:
    """A two-dimensional value supporting equality and vector addition."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        # TODO: compare Vector values and return NotImplemented otherwise
        raise NotImplementedError

    def __add__(self, other):
        # TODO: add Vector values and return NotImplemented otherwise
        raise NotImplementedError


class TaskStatus(Enum):
    PENDING = auto()
    DONE = auto()


@dataclass
class Task:
    title: str
    status: TaskStatus = TaskStatus.PENDING
    notes: list[str] = dataclasses.field(default_factory=list)

    def complete(self):
        # TODO: update status to TaskStatus.DONE
        raise NotImplementedError

    def add_note(self, note):
        # TODO: append note to this task's independent notes list
        raise NotImplementedError

    def as_record(self):
        # TODO: return a recursively independent dict with dataclasses.asdict
        raise NotImplementedError


rectangle = Rectangle(4, 5)
assert rectangle.area() == 20
assert rectangle.perimeter() == 18
print("Rectangle: OK")

square = Square(4)
assert square.area() == 16
assert square.perimeter() == 16
print("Square: OK")

animals = [Dog(), Cat()]
sounds = [animal.speak() for animal in animals]
assert sounds == ["Woof!", "Meow!"]
print("Polymorphism (Dog/Cat): OK")

account = BankAccount(10)
account.deposit(5)
assert account.balance == 15
try:
    account.deposit(0)
    raise AssertionError("expected ValueError")
except ValueError:
    pass
print("BankAccount property/deposit: OK")

try:
    account.withdraw(1000)
    raise AssertionError("expected InsufficientFundsError")
except InsufficientFundsError as error:
    assert error.balance == 15
    assert error.amount == 1000
print("InsufficientFundsError: OK")

assert Vector(1, 2) + Vector(3, 4) == Vector(4, 6)
assert Vector.__add__(Vector(1, 2), 3) is NotImplemented
print("Vector protocols: OK")

task = Task("Practice dataclasses")
other_task = Task("Read about enums")
assert task.status is TaskStatus.PENDING
task.add_note("Use field(default_factory=list)")
assert task.notes == ["Use field(default_factory=list)"]
assert other_task.notes == [], "Each Task must own a different notes list"

record = task.as_record()
assert record == {
    "title": "Practice dataclasses",
    "status": TaskStatus.PENDING,
    "notes": ["Use field(default_factory=list)"],
}
recorded_notes = record["notes"]
assert isinstance(recorded_notes, list)
recorded_notes.append("change the exported copy")
assert task.notes == ["Use field(default_factory=list)"]

task.complete()
assert task.status is TaskStatus.DONE
assert task == Task(
    "Practice dataclasses",
    TaskStatus.DONE,
    ["Use field(default_factory=list)"],
)
print("Dataclass and enum: OK")

print("\nAll checks passed!")
