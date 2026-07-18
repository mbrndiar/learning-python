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
        # Assigning through self stores state on this particular instance;
        # dog1 and dog2 therefore receive independent names and ages.
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
    """Demonstrate properties and class-related method types."""

    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        """Compute an attribute-like value without storing duplicate state."""
        # Deriving area from radius avoids stale duplicated state when radius
        # changes after construction.
        return math.pi * self.radius**2

    @classmethod
    def unit_circle(cls):
        """Return a radius-one instance of the class used for the call."""
        # Using cls instead of Circle means an inherited call constructs the
        # subclass, making this an inheritance-respecting alternative constructor.
        return cls(1)

    @staticmethod
    def is_valid_radius(radius):
        """Return whether a value is a valid circle radius."""
        # This validation rule belongs with Circle but needs neither an existing
        # instance (`self`) nor the class used for the call (`cls`).
        return radius >= 0


class Wheel(Circle):
    """A Circle subclass used to demonstrate class-method inheritance."""


if __name__ == "__main__":
    dog1 = Dog("Rex", 3)
    dog2 = Dog("Fido", 5)

    # Accessing a method through an instance creates a bound method that
    # remembers that instance, so it can be stored and called later.
    saved_bark = dog1.bark

    print(dog1.bark())
    print(dog2.describe())
    bound_result = saved_bark()
    class_result = Dog.bark(dog1)
    print("Stored bound method:", bound_result)
    print("Dog.bark(dog1):", class_result)
    print("The two calls are equivalent:", bound_result == class_result)
    print("Species:", dog1.species)
    print("Printed object:", dog1)

    circle = Circle(2)
    print("Circle area:", circle.area)
    print("Is 2 a valid radius?", Circle.is_valid_radius(2))

    unit = Circle.unit_circle()
    print("Unit circle area:", unit.area)

    # Wheel inherits unit_circle(). Because the class method constructs `cls`,
    # calling it through Wheel returns a Wheel rather than a Circle.
    unit_wheel = Wheel.unit_circle()
    print("Inherited constructor made a Wheel:", isinstance(unit_wheel, Wheel))
