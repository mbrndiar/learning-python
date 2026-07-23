"""
Chapter 9, Lesson 5: ABCs, Dataclasses, Enums, and Domain Errors

Purpose: use `abc.ABC`/`@abstractmethod` to enforce that subclasses
implement required methods; use `@dataclass` (and `field(default_factory=
...)`) to reduce boilerplate for data-holding classes; use `enum.Enum` for
a closed set of named constants; and define a custom exception now that
inheritance (Lesson 2) has been taught, so it can subclass `Exception`
deliberately rather than as unexplained syntax.

Prerequisites: Lessons 1-4 (classes through the Python data model).

Read this file top to bottom, predict each output, then run it:

    python lessons/09_object_oriented_programming/05_abcs_dataclasses_enums_and_domain_errors.py
"""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from enum import Enum, auto


# Step 1: an abstract base class defines a required interface. Shape
# itself can never be instantiated -- only a subclass that implements
# every @abstractmethod can be.
class Shape(ABC):
    """An abstract base class: cannot be instantiated directly."""

    @abstractmethod
    def area(self):
        """Subclasses must implement this method."""
        raise NotImplementedError

    @abstractmethod
    def perimeter(self):
        """Subclasses must implement this method."""
        raise NotImplementedError

    def describe(self):
        """A concrete method, available to every subclass for free."""
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    """A concrete shape implementing the Shape interface."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    """A square specializes Rectangle by fixing width equal to height."""

    def __init__(self, side):
        super().__init__(side, side)


try:
    Shape()  # cannot instantiate an abstract class
except TypeError as error:
    print("Cannot instantiate Shape directly:", error)

for shape in (Rectangle(4, 5), Square(3)):
    print(shape.describe())


# Step 2: dataclasses generate __init__, __repr__, and __eq__ from
# annotated fields, removing boilerplate for data-holding classes.
class TaskStatus(Enum):
    """A closed set of named states -- deliberately not arbitrary strings."""

    PENDING = auto()
    DONE = auto()


@dataclass
class Task:
    """A small record combining a plain field with an enum-typed field."""

    title: str
    status: TaskStatus = TaskStatus.PENDING
    # field(default_factory=list) creates a fresh list for every Task.
    # Dataclasses reject a bare `tags: list = []` at class-definition time
    # with ValueError. default_factory both satisfies that guard and creates
    # a different list for every instance.
    tags: list = field(default_factory=list)

    def complete(self):
        """Move this task to the DONE status."""
        self.status = TaskStatus.DONE


task = Task("Write the lesson", tags=["writing"])
print("\nBefore:", task)
task.complete()
print("After:", task)
print(
    "Equal to an equivalent completed Task?",
    task == Task("Write the lesson", TaskStatus.DONE, ["writing"]),
)

# asdict() recursively converts a dataclass instance (and nested dataclasses)
# into a new dict. It preserves other rich values as-is: status remains a
# TaskStatus enum, so convert it to status.name or status.value before passing
# this record to Chapter 8's json.dumps().
print("asdict(task):", asdict(task))

for status in TaskStatus:
    print(status.name, "=", status.value)


# Step 3: a custom exception. Now that inheritance has been taught
# (Lesson 2), `class InsufficientFundsError(Exception):` is no longer
# unexplained syntax -- it is the same subclassing mechanism already
# used for Dog(Animal), applied to the exception hierarchy instead.
class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""

    def __init__(self, balance, amount):
        # Structured attributes let a handler inspect the failure
        # without parsing the human-readable message string.
        self.balance = balance
        self.amount = amount
        super().__init__(f"cannot withdraw {amount}: balance is only {balance}")


class BankAccount:
    """BankAccount from Lesson 3, extended with a domain-specific error."""

    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount


account = BankAccount("Grace", 100)
try:
    account.withdraw(500)
except InsufficientFundsError as error:
    print("\nCaught a domain-specific error:", error)
    print(
        "  structured detail -- balance:", error.balance, "| requested:", error.amount
    )

# --- One-variable experiment -------------------------------------------
# Change Task's tags default to a bare `tags: list = []` (remove
# field(default_factory=list)) and predict when the failure occurs. Python
# raises ValueError while @dataclass processes the class, before any Task can
# be created. Read the message, then restore default_factory.
