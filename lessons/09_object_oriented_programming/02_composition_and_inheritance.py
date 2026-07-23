"""
Chapter 9, Lesson 2: Composition and Inheritance

Purpose: contrast inheritance ("is a", extending a shared base class) with
composition ("has a", delegating to another object); use `super()` to
reuse a parent's behavior; and show polymorphism, where the same method
call behaves differently depending on the actual type of the object.

Prerequisites: Lesson 1 (classes, objects, and methods).

Read this file top to bottom, predict each output, then run it:

    python lessons/09_object_oriented_programming/02_composition_and_inheritance.py
"""


# Step 1: a coherent "is a" hierarchy. Every subclass below is genuinely a
# kind of Animal, which is the test inheritance should pass: could you
# truthfully say "a Dog IS AN Animal"? Animal.speak() raises deliberately,
# documenting that every concrete subclass must override it.
class Animal:
    """Base class shared by all animals in this hierarchy."""

    def __init__(self, name):
        self.name = name

    def speak(self):
        """Return the sound this animal makes. Subclasses must override this."""
        raise NotImplementedError("Subclasses must implement speak()")

    def describe(self):
        """Return a description that uses the (possibly overridden) speak()."""
        # describe() never needs editing when a new Animal subclass
        # appears -- it relies only on the Animal interface, not on any
        # one subclass's implementation.
        return f"{self.name} says {self.speak()}"


class Dog(Animal):
    """A dog is an animal that barks."""

    def speak(self):
        return "Woof"


class Cat(Animal):
    """A cat is an animal that meows."""

    def speak(self):
        return "Meow"


class Cow(Animal):
    """A cow is an animal that moos."""

    def speak(self):
        return "Moo"


class Puppy(Dog):
    """A puppy IS a dog -- a valid multi-level "is a" relationship.

    Puppy adds a breed and extends (rather than replaces) Dog's speak(),
    which is what distinguishes genuine specialization from merely
    reusing code that happens to be nearby.
    """

    def __init__(self, name, breed):
        super().__init__(name)  # reuse Animal's initialization via Dog
        self.breed = breed

    def speak(self):
        # Extend the parent's behavior rather than fully replacing it.
        return super().speak() + " (still a puppy)"


# Step 2: polymorphism. The same describe() call, made on different
# objects, runs different speak() implementations depending on each
# object's actual type -- callers do not need to check types themselves.
animals = [Dog("Rex"), Cat("Whiskers"), Cow("Bessie"), Puppy("Buddy", "Labrador")]
for animal in animals:
    print(animal.describe())

puppy = animals[-1]
print("\nIs Puppy an Animal?", isinstance(puppy, Animal))
print("Is Puppy a Dog?", isinstance(puppy, Dog))
print("Is Puppy a Cat?", isinstance(puppy, Cat))
print("Puppy breed:", puppy.breed)


# Step 3: composition. An Engine is not a kind of Car -- a Car HAS an
# Engine and delegates work to it. Composition is the right tool here:
# there is no truthful "is a" relationship between Car and Engine.
class Engine:
    """A component with its own state and behavior, independent of any Car."""

    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        self.running = True
        return f"Engine ({self.horsepower} hp) starting"


class Car:
    """A car delegates starting behavior to the engine it is composed of."""

    def __init__(self, make, engine):
        self.make = make
        self.engine = engine  # composition: Car holds an Engine, not IS one

    def start(self):
        # Car does not know HOW an engine starts -- it only knows it can
        # ask its engine to do so. Swapping in a different Engine
        # instance changes the car's behavior without changing Car itself.
        return f"{self.make}: {self.engine.start()}"


car = Car("Volt", Engine(120))
print("\n" + car.start())
print("Engine running:", car.engine.running)

# --- One-variable experiment -------------------------------------------
# Give Car a second engine variant (e.g. Engine(300)) and swap
# car.engine to it before calling car.start() again. Predict: does Car's
# own code need to change at all? (It should not -- that is exactly what
# delegating to a composed object buys you.)
