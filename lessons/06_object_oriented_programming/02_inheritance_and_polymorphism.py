"""
Lesson 6.2: Inheritance and Polymorphism

Inheritance lets a class reuse and extend the behavior of another class.
Polymorphism lets different classes respond to the same method call in
their own way.
"""


class Animal:
    """Base class shared by all animals."""

    def __init__(self, name):
        self.name = name

    def speak(self):
        """Return the sound this animal makes. Meant to be overridden."""
        raise NotImplementedError("Subclasses must implement speak()")

    def describe(self):
        """Return a description that uses the (possibly overridden) speak()."""
        return f"{self.name} says {self.speak()}"


class Cat(Animal):
    """A cat is an animal that meows."""

    def speak(self):
        return "Meow"


class Cow(Animal):
    """A cow is an animal that moos."""

    def speak(self):
        return "Moo"


class Puppy(Cat):
    """Demonstrate multi-level inheritance and `super()`."""

    def __init__(self, name, breed):
        super().__init__(name)  # reuse the parent's initialization logic
        self.breed = breed

    def speak(self):
        # Extend the parent behavior instead of fully replacing it.
        return super().speak() + " (but really a puppy pretending to be a cat)"


if __name__ == "__main__":
    animals = [Cat("Whiskers"), Cow("Bessie"), Puppy("Buddy", "Labrador")]

    for animal in animals:
        # Polymorphism: the same `describe()` call behaves differently
        # depending on the actual type of `animal`.
        print(animal.describe())

    puppy = animals[-1]
    print("Is Puppy an Animal?", isinstance(puppy, Animal))
    print("Is Puppy a Cat?", isinstance(puppy, Cat))
    print("Puppy breed:", puppy.breed)
