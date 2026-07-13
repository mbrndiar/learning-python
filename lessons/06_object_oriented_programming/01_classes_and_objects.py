"""
Lesson 6.1: Classes and Objects

Classes let you bundle data (attributes) and behavior (methods) together
into a single blueprint for creating objects.
"""


class Dog:
    """A simple class representing a dog."""

    species = "Canis familiaris"  # class attribute, shared by all instances

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
        """Compute the area on the fly whenever it is accessed."""
        return 3.14159 * self.radius ** 2

    @staticmethod
    def unit_circle():
        """Demonstrate a static method: doesn't need `self` or an instance."""
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
