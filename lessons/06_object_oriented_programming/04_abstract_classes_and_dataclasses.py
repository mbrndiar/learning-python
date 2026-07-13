"""
Lesson 6.4: Abstract Base Classes, Dataclasses and Enums

This lesson wraps up OOP with three more tools:
- `abc.ABC` / `@abstractmethod` to properly enforce an interface
- `@dataclass` to reduce boilerplate for simple data-holding classes
- `enum.Enum` to represent a fixed set of named constants
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto


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
        """Concrete method available to every subclass for free."""
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    """A concrete shape that implements the Shape interface."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    """Composition through inheritance: a Square is a special Rectangle."""

    def __init__(self, side):
        super().__init__(side, side)


@dataclass
class Point:
    """A dataclass automatically generates __init__, __repr__ and __eq__."""

    x: float
    y: float

    def distance_to(self, other):
        """Regular methods work exactly the same on dataclasses."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Polygon:
    """Demonstrate a mutable default using `field(default_factory=...)`."""

    name: str
    points: list = field(default_factory=list)


class Color(Enum):
    """An enum defines a fixed, named set of related constants."""

    RED = auto()
    GREEN = auto()
    BLUE = auto()


if __name__ == "__main__":
    shapes = [Rectangle(4, 5), Square(3)]
    for shape in shapes:
        print(shape.describe())

    try:
        Shape()  # cannot instantiate an abstract class
    except TypeError as error:
        print("Caught an error:", error)

    p1 = Point(0, 0)
    p2 = Point(3, 4)
    print("p1:", p1)
    print("Distance:", p1.distance_to(p2))
    print("Equal to itself?", p1 == Point(0, 0))

    polygon = Polygon("Triangle")
    polygon.points.append(Point(0, 0))
    polygon.points.append(Point(1, 0))
    polygon.points.append(Point(0, 1))
    print("Polygon:", polygon)

    for color in Color:
        print(color.name, "=", color.value)

    print("Chosen color:", Color.GREEN)
    print("Is it blue?", Color.GREEN is Color.BLUE)
