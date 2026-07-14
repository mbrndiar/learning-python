"""
Lesson 6.1: Classes and Objects

Classes define new types that bundle state (attributes) and behavior (methods).
Calling a class creates an instance and passes it to __init__ as `self`.
"""

import math


class Dog:
    """A simple class representing a dog."""

    # Class attributes are found through every instance. Mutable per-dog state
    # should instead be initialized on `self` inside __init__.
    species = "Canis familiaris"

    def __init__(self, name, age):
        """Initialize a new Dog instance with a name and age."""
        self.name = name  # instance attribute
        self.age = age  # instance attribute

    def bark(self):
        """Return a string describing the dog barking."""
        return f"{self.name} says Woof!"

    def describe(self):
        """Return a human-readable description of the dog."""
        return f"{self.name} is {self.age} year(s) old."

    def __str__(self):
        """Define how the object is shown when printed."""
        return f"Dog({self.name}, {self.age})"


class Circle:
    """Demonstrate properties, a common way to compute derived values."""

    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        """Compute an attribute-like value without storing duplicate state."""
        return math.pi * self.radius**2

    @staticmethod
    def unit_circle():
        """Construct a circle without needing an existing instance."""
        return Circle(1)


if __name__ == "__main__":
    dog1 = Dog("Rex", 3)
    dog2 = Dog("Fido", 5)

    print(dog1.bark())
    print(dog2.describe())
    print("Species:", dog1.species)
    print("Printed object:", dog1)

    circle = Circle(2)
    print("Circle area:", circle.area)

    unit = Circle.unit_circle()
    print("Unit circle area:", unit.area)
