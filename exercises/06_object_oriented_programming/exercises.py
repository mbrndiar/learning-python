"""
Exercises: 06 Object-Oriented Programming

Implement the classes below, then run this file directly to check
your work.
"""


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

    print("\nAll checks passed!")
