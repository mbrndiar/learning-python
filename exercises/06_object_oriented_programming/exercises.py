"""
Exercises: 06 Object-Oriented Programming

Implement the classes below, then run this file directly to check
your work.
"""

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

    Reuse Rectangle's __init__ via super() by passing the same side
    for both width and height.
    """

    def __init__(self, side):
        # TODO: call the parent constructor appropriately
        raise NotImplementedError


class Animal:
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
    """Expose a read-only balance property and validate deposits."""

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


class Vector:
    """A two-dimensional value supporting vector addition."""

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

    def complete(self):
        # TODO: update status to TaskStatus.DONE
        raise NotImplementedError


if __name__ == "__main__":
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
    print("BankAccount property: OK")

    assert Vector(1, 2) + Vector(3, 4) == Vector(4, 6)
    assert Vector.__add__(Vector(1, 2), 3) is NotImplemented
    print("Vector protocols: OK")

    task = Task("Practice dataclasses")
    assert task.status is TaskStatus.PENDING
    task.complete()
    assert task.status is TaskStatus.DONE
    assert task == Task("Practice dataclasses", TaskStatus.DONE)
    print("Dataclass and enum: OK")

    print("\nAll checks passed!")
