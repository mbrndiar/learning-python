"""
Solutions: 06 Object-Oriented Programming
"""

from dataclasses import dataclass
from enum import Enum, auto


class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)


class Animal:
    def speak(self):
        raise NotImplementedError("Subclasses must implement speak()")


class Dog(Animal):
    def speak(self):
        return "Woof!"


class Cat(Animal):
    def speak(self):
        return "Meow!"


class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)


class TaskStatus(Enum):
    PENDING = auto()
    DONE = auto()


@dataclass
class Task:
    title: str
    status: TaskStatus = TaskStatus.PENDING

    def complete(self):
        self.status = TaskStatus.DONE


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
