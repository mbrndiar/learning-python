"""
Solutions: 06 Object-Oriented Programming
"""


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
