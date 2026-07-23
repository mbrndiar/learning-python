"""
Chapter 9, Lesson 1: Classes, Objects, and Methods

Purpose: introduce classes as a way to bundle state (attributes) and
behavior (methods); the difference between class attributes and instance
attributes; bound methods; and `@property`, `@classmethod`, and
`@staticmethod` as three different kinds of method.

Prerequisites: Chapters 1-8 (values through structured data and time).
This is the first lesson in the course to define a class of its own.

Read this file top to bottom, predict each output, then run it:

    python lessons/09_object_oriented_programming/01_classes_objects_and_methods.py
"""

import math


class Dog:
    """A simple class bundling a dog's state and behavior together."""

    # A class attribute is found through every instance that does not
    # shadow it. It is shared, so it belongs here only when every
    # instance genuinely shares the same value.
    species = "Canis familiaris"

    def __init__(self, name, age):
        """Initialize a new Dog instance with a name and age."""
        # Assigning through self stores state on THIS particular
        # instance -- dog1 and dog2 below get independent names and ages,
        # unlike the shared class attribute above.
        self.name = name
        self.age = age

    def bark(self):
        """Return a string describing the dog barking."""
        return f"{self.name} says Woof!"

    def describe(self):
        """Return a human-readable description of the dog."""
        return f"{self.name} is {self.age} year(s) old."


# Step 1: calling a class constructs an instance. Python calls __init__
# automatically, passing the new instance as `self`.
dog1 = Dog("Rex", 3)
dog2 = Dog("Fido", 5)
print("dog1.bark():", dog1.bark())
print("dog2.describe():", dog2.describe())
print("Both share species:", dog1.species, "/", dog2.species)

# Step 2: accessing a method through an instance (dog1.bark) creates a
# *bound method* -- an object that remembers dog1 and will supply it as
# `self` when called later. Calling the class's function directly and
# passing the instance explicitly does the same thing.
saved_bark = dog1.bark
bound_result = saved_bark()
class_result = Dog.bark(dog1)
print("\nStored bound method call:", bound_result)
print("Dog.bark(dog1) call:", class_result)
print("The two calls are equivalent:", bound_result == class_result)

# --- One-variable experiment -------------------------------------------
# Change dog2's age (Dog("Fido", 5) above) to a different number and
# predict how dog2.describe()'s printed sentence changes. dog1 is
# unaffected -- each instance's attributes are independent.


class Circle:
    """Demonstrate the three method kinds a class can define."""

    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        """Compute an attribute-like value without storing duplicate state."""
        # Deriving area from radius on every access avoids stale
        # duplicated state if radius changes after construction --
        # unlike caching area once in __init__.
        return math.pi * self.radius**2

    @classmethod
    def unit_circle(cls):
        """Return a radius-one instance of the class actually used to call this."""
        # Using cls instead of Circle means a subclass calling
        # unit_circle() constructs an instance of ITSELF, not of Circle --
        # Step 4 below demonstrates that directly.
        return cls(1)

    @staticmethod
    def is_valid_radius(radius):
        """Return whether a value is usable as a circle radius."""
        # This validation rule belongs conceptually with Circle but needs
        # neither an existing instance (self) nor the calling class
        # (cls), so a plain function attached to the class is the
        # simplest fit.
        return radius >= 0


class Wheel(Circle):
    """A Circle subclass, used only to demonstrate classmethod inheritance."""


# Step 3: a property reads like an attribute (no parentheses) but runs
# code on every access.
circle = Circle(2)
print("\nCircle(2).area:", circle.area)
print("Circle.is_valid_radius(2):", Circle.is_valid_radius(2))
print("Circle.is_valid_radius(-1):", Circle.is_valid_radius(-1))

# Step 4: unit_circle() is inherited by Wheel unchanged, but because it
# constructs `cls(1)` rather than `Circle(1)`, calling it through Wheel
# returns a Wheel.
unit = Circle.unit_circle()
unit_wheel = Wheel.unit_circle()
print("\nCircle.unit_circle() type:", type(unit).__name__)
print("Wheel.unit_circle() type:", type(unit_wheel).__name__)
print("Wheel.unit_circle() is still a Circle:", isinstance(unit_wheel, Circle))
