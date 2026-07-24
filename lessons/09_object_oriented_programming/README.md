# 🧩 Chapter 9: Objects and Data Models

**Semantic ID:** `module.objects-and-data-models` · **Prerequisites:**
`module.structured-data-and-time`

## 📍 Where this fits

Every value you have modeled so far has been a plain function, dict, or
built-in type -- Chapter 8's `validate_record` checked a dict's shape, but
nothing enforced that shape once the dict escaped the function. This
chapter introduces classes as a way to bundle data with the behavior that
keeps it valid, so a `Task` or a `BankAccount` can defend its own
invariants (a non-negative balance, a fixed set of statuses) instead of
relying on every caller to validate it correctly, every time.

## 🎯 Learning objectives

After this chapter, you should be able to:

- distinguish class attributes (shared) from instance attributes
  (per-object), and explain what a bound method remembers;
- choose among `@property`, `@classmethod`, and `@staticmethod` for a
  given piece of class-related behavior;
- decide between inheritance ("is a") and composition ("has a") for a
  given relationship, and use `super()` to extend a parent's behavior;
- explain what `_name` and `__name` signal about intended access, and
  what name mangling does (and does not) protect against;
- implement dunder methods (`__repr__`, `__str__`, `__eq__`, `__lt__`,
  `__add__`, `__len__`, `__iter__`) so a custom object participates in
  Python's built-in operators and functions;
- enforce a required interface with `abc.ABC`/`@abstractmethod`;
- reduce boilerplate for data-holding classes with `@dataclass`,
  including `field(default_factory=...)` for mutable defaults, and
  convert an instance to a plain dict with `asdict()`;
- represent a closed set of named constants with `enum.Enum`;
- define and raise a custom exception now that inheritance has been
  taught, carrying structured attributes a handler can inspect.

## 🧠 Motivation and mental model

A class is not a new kind of syntax to memorize -- it is a way to keep
data and the operations that preserve its invariants next to each other,
so the invariant cannot be violated by code that forgot to check it. The
`BankAccount` in this chapter could not have its balance corrupted by a
careless assignment, because the balance is only ever changed through
`deposit`/`withdraw`, which validate first. Inheritance and composition
are two different tools for reusing that structure: inheritance says "this
new type genuinely is a kind of that one," while composition says "this
object needs another object's help but is not one itself." Confusing the
two produces hierarchies where a subtype cannot honestly stand in for its
parent -- exactly the trap this chapter's `Puppy` example avoids by
extending `Dog`, not `Cat`.

## 1️⃣ Classes, objects, and methods

A class bundles state (attributes) with the behavior that operates on
it. Calling the class constructs an instance and passes it to
`__init__` as `self`; attributes assigned through `self` are
per-instance, while attributes assigned directly in the class body are
shared across every instance that does not shadow them:

```python
class Dog:
    species = "Canis familiaris"  # class attribute: shared

    def __init__(self, name, age):
        self.name = name  # instance attribute: per-object
        self.age = age

    def bark(self):
        return f"{self.name} says Woof!"


dog1 = Dog("Rex", 3)
dog2 = Dog("Fido", 5)
print(dog1.bark())
print("Both share species:", dog1.species, "/", dog2.species)
```

```text
Rex says Woof!
Both share species: Canis familiaris / Canis familiaris
```

`dog1` and `dog2` get independent `name`/`age`, but both read the same
`species` because it lives on the class, not on either instance.

### Bound methods remember their instance

```python
saved_bark = dog1.bark
print(saved_bark())
print(Dog.bark(dog1))
```

```text
Rex says Woof!
Rex says Woof!
```

`dog1.bark` is a *bound method* -- an object that already remembers
`dog1` and will supply it as `self` whenever called. Calling the
class's function directly and passing the instance explicitly
(`Dog.bark(dog1)`) does exactly the same thing.

### `@property`, `@classmethod`, and `@staticmethod` are three different kinds of method

```python
import math


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return math.pi * self.radius**2

    @classmethod
    def unit_circle(cls):
        return cls(1)

    @staticmethod
    def is_valid_radius(radius):
        return radius >= 0


class Wheel(Circle):
    """A Circle subclass, used only to demonstrate classmethod inheritance."""


circle = Circle(2)
print(circle.area)
print(Circle.is_valid_radius(-1))
print(type(Circle.unit_circle()).__name__)
print(type(Wheel.unit_circle()).__name__)
```

```text
12.566370614359172
False
Circle
Wheel
```

`area` reads like a plain attribute but recomputes from `radius` on
every access, avoiding stale cached state. `is_valid_radius` needs
neither `self` nor `cls`, so it is a static method. `unit_circle`
constructs `cls(1)`, not `Circle(1)` -- so calling it through `Wheel`
returns a `Wheel`, not a `Circle`, even though `unit_circle` itself is
defined only once, on `Circle`.

Run the complete companion:

```bash
python lessons/09_object_oriented_programming/01_classes_objects_and_methods.py
```

See
[`01_classes_objects_and_methods.py`](01_classes_objects_and_methods.py)
for the full sequence, including the `Dog.bark(dog1)` equivalence check.

> **Try one change:** change `dog2`'s age to a different number and
> predict how `dog2.describe()`'s printed sentence changes. `dog1` is
> unaffected -- each instance's attributes are independent.

## 2️⃣ Composition vs. inheritance, and `super()`

Inheritance says "this new type genuinely **is a** kind of that one";
composition says "this object **has a** collaborator it delegates to,
but is not one itself." A coherent inheritance hierarchy should pass a
simple test: could you truthfully say "a `Dog` IS AN `Animal`"?

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Subclasses must implement speak()")

    def describe(self):
        return f"{self.name} says {self.speak()}"


class Dog(Animal):
    def speak(self):
        return "Woof"


class Cat(Animal):
    def speak(self):
        return "Meow"


class Puppy(Dog):
    def __init__(self, name, breed):
        super().__init__(name)  # reuse Animal's initialization via Dog
        self.breed = breed

    def speak(self):
        return super().speak() + " (still a puppy)"  # extend, not replace


puppy = Puppy("Buddy", "Labrador")
print(puppy.describe())
print("Is Puppy a Dog?", isinstance(puppy, Dog))
print("Is Puppy a Cat?", isinstance(puppy, Cat))
```

```text
Buddy says Woof (still a puppy)
Is Puppy a Dog? True
Is Puppy a Cat? False
```

`Puppy` extends `Dog`, so the hierarchy stays truthful: `isinstance`
confirms it is a `Dog` and, correctly, not a `Cat`. `super().__init__(name)`
reuses `Animal`'s initialization instead of duplicating it, and
`super().speak()` extends the parent's return value rather than fully
replacing it. `describe()` (defined once, on `Animal`) never needs
editing when a new subclass appears -- polymorphism means the same
`describe()` call runs whichever `speak()` the actual object's type
provides.

### Composition: delegating without being a subtype

```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        self.running = True
        return f"Engine ({self.horsepower} hp) starting"


class Car:
    def __init__(self, make, engine):
        self.make = make
        self.engine = engine  # composition: Car HAS an Engine, not IS one

    def start(self):
        return f"{self.make}: {self.engine.start()}"


car = Car("Volt", Engine(120))
print(car.start())
```

```text
Volt: Engine (120 hp) starting
```

There is no truthful "is a" relationship between `Car` and `Engine` --
a `Car` is not a kind of `Engine`. `Car` only knows it can ask its
`engine` to start; it does not know *how*. Swapping in a different
`Engine` instance changes `car.start()`'s output without any change to
`Car`'s own code, which is exactly what delegating to a composed object
buys you.

Run the complete companion:

```bash
python lessons/09_object_oriented_programming/02_composition_and_inheritance.py
```

See
[`02_composition_and_inheritance.py`](02_composition_and_inheritance.py)
for the full sequence, including all four `Animal` subclasses.

> **Try one change:** give `car` a second `Engine` instance (e.g.
> `Engine(300)`) and reassign `car.engine` to it before calling
> `car.start()` again. Predict: does `Car`'s own code need to change at
> all?

## 3️⃣ Properties and encapsulation

A property reads like a plain attribute (no parentheses) but runs code
on every access, which is how a class can expose a read-only view of
state it still validates on every write:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance  # convention: "not part of the public API"
        self.__pin = "0000"  # name-mangled to _BankAccount__pin

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount


account = BankAccount("Ada", 100)
account.deposit(50)
print(f"{account.owner}'s balance: {account.balance}")

try:
    account.balance = 1_000_000
except AttributeError as error:
    print("Cannot assign to a read-only property:", error)
```

```text
Ada's balance: 150
Cannot assign to a read-only property: property 'balance' of 'BankAccount' object has no setter
```

`balance` has no setter, so assigning `account.balance = ...` raises
`AttributeError` -- the property alone controls *reading*; `deposit`/
`withdraw` control *writing*, validating their input before mutating
`_balance`. A single leading underscore (`_balance`) is a convention
meaning "not part of the public API"; Python does not enforce it.

### Name mangling caveat

```python
print("Direct pin check via method:", account._check_pin("0000"))
print("Mangled attribute is reachable:", account._BankAccount__pin)
```

```text
Direct pin check via method: True
Mangled attribute is reachable: 0000
```

A double leading underscore (`__pin`) triggers name mangling: Python
rewrites it to `_BankAccount__pin` at class-definition time, which
reduces accidental collisions with a subclass's own attributes -- but
the mangled name is still directly reachable from outside the class, as
`account._BankAccount__pin` shows. This is obscurity, not a security
boundary.

Run the complete companion:

```bash
python lessons/09_object_oriented_programming/03_properties_and_encapsulation.py
```

See
[`03_properties_and_encapsulation.py`](03_properties_and_encapsulation.py)
for the full sequence, including the `withdraw` failure path.

> **Try one change:** add a `set_pin(self, old_pin, new_pin)` method that
> only updates `self.__pin` when `old_pin` matches. Predict: does that
> method need any special name-mangling handling, or does `__pin` work
> normally from *inside* the class? (Mangling only affects the *lookup*
> -- `__pin` means the same mangled name everywhere inside `BankAccount`.)

## 4️⃣ The Python data model (dunder methods)

Special ("dunder") methods let a custom object participate in Python's
built-in operators and functions, instead of needing bespoke method
names for each one:

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        return f"Money({self.amount!r})"

    def __str__(self):
        return f"${self.amount:.2f}"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount + other.amount)


total = Money(19.99) + Money(5.01)
print(repr(total))
print(total)
print(sorted([Money(5.01), Money(19.99)]))
```

```text
Money(25.0)
$25.00
[Money(5.01), Money(19.99)]
```

`repr()` favors an unambiguous, code-like form; `str()` (used by
`print()`) favors a human-friendly one. `__eq__`/`__lt__` let `Money`
participate in `==`, `<`, and `sorted()` directly.

### `NotImplemented` for an unsupported operand

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)


print(Vector.__add__(Vector(1, 2), 3))
```

```text
NotImplemented
```

`Vector.__add__(Vector(1, 2), 3)` returns the literal object
`NotImplemented` -- it does not raise. Returning `NotImplemented` (not
the exception `NotImplementedError`) tells Python to try the other
operand's reflected method, and ultimately to raise a clear `TypeError`
itself only once neither side supports the operation.

### `__len__`/`__iter__` support `len()` and `for`/`list()`

```python
class Playlist:
    def __init__(self, titles):
        self._titles = list(titles)

    def __len__(self):
        return len(self._titles)

    def __iter__(self):
        return iter(self._titles)


playlist = Playlist(["First", "Second", "Third"])
print(len(playlist))
print(list(playlist))
```

```text
3
['First', 'Second', 'Third']
```

`Playlist` works with `len()` and `for`/`list()` exactly like a
built-in sequence, without exposing its internal `_titles` list
directly.

Run the complete companion:

```bash
python lessons/09_object_oriented_programming/04_python_data_model.py
```

See [`04_python_data_model.py`](04_python_data_model.py) for the full
sequence, including `__float__` and the `Playlist` for-loop.

> **Try one change:** remove `Vector`'s `__eq__` (or comment it out) and
> predict what `Vector(1, 2) == Vector(1, 2)` returns then. Without a
> custom `__eq__`, the inherited default from `object` compares identity
> (`is`), not value -- so two distinct, equal-looking `Vector`s would no
> longer compare equal.

## 5️⃣ ABCs, dataclasses, enums, and domain errors

`abc.ABC` plus `@abstractmethod` enforces a required interface: a class
inheriting from `ABC` with at least one abstract method cannot be
instantiated until every abstract method is overridden.

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        raise NotImplementedError

    @abstractmethod
    def perimeter(self):
        raise NotImplementedError

    def describe(self):
        return f"{type(self).__name__}: area={self.area():.2f}"


try:
    Shape()
except TypeError as error:
    print("Cannot instantiate Shape directly:", error)
```

```text
Cannot instantiate Shape directly: Can't instantiate abstract class Shape with abstract methods area, perimeter
```

`Shape()` fails outright -- `TypeError` lists exactly which abstract
methods are still unimplemented, before any instance is ever created.

### `@dataclass` and the mutable-default guard

```python
from dataclasses import dataclass, field
from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    DONE = auto()


@dataclass
class Task:
    title: str
    status: TaskStatus = TaskStatus.PENDING
    tags: list = field(default_factory=list)  # NOT tags: list = []


task = Task("Write the lesson", tags=["writing"])
print(task)
```

```text
Task(title='Write the lesson', status=<TaskStatus.PENDING: 1>, tags=['writing'])
```

`@dataclass` generates `__init__`/`__repr__`/`__eq__` from annotated
fields. A bare `tags: list = []` default would raise `ValueError` while
`@dataclass` processes the class body -- a mutable default shared by
every instance is exactly the class-attribute trap from concept 1, and
`@dataclass` refuses to create it silently. `field(default_factory=list)`
gives each `Task` instance its own fresh list instead. `enum.Enum`
represents a closed, named set of constants (`PENDING`/`DONE`),
preventing an arbitrary string where only a fixed set is valid.

### A structured custom exception

```python
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"cannot withdraw {amount}: balance is only {balance}")


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance

    def withdraw(self, amount):
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount


account = BankAccount("Grace", 100)
try:
    account.withdraw(500)
except InsufficientFundsError as error:
    print("balance:", error.balance, "| requested:", error.amount)
```

```text
balance: 100 | requested: 500
```

`class InsufficientFundsError(Exception):` is the same subclassing
mechanism concept 2 already taught, applied to the exception hierarchy.
The domain error exposes `.balance`/`.amount` as structured attributes,
so a handler reads the failure directly instead of parsing the message
text.

Run the complete companion:

```bash
python lessons/09_object_oriented_programming/05_abcs_dataclasses_enums_and_domain_errors.py
```

See
[`05_abcs_dataclasses_enums_and_domain_errors.py`](05_abcs_dataclasses_enums_and_domain_errors.py)
for the full sequence, including `Rectangle`/`Square`, `asdict()`, and
iterating `TaskStatus`.

> **Try one change:** change `Task`'s `tags` field back to a bare
> `tags: list = []` (remove `field(default_factory=list)`) and predict
> when the failure occurs. Python raises `ValueError` while `@dataclass`
> processes the class, before any `Task` can be created.

## 🔁 Transition to Chapter 10

This chapter modeled state and behavior together with classes. Chapter
10, Iteration, Decorators, and Contexts, looks at two more mechanisms
already used informally here -- `__iter__` from `Playlist`, and the
`with` statement from Chapter 7 -- and generalizes them: how an iterator
actually produces its values one at a time, how a generator function
builds one automatically, and how a function can wrap another function's
behavior with a decorator.

## ⚠️ Common mistakes

- Storing per-instance mutable state as a class attribute, so every
  instance ends up sharing (and corrupting) the same list or dict.
- Using inheritance purely for code reuse when the subtype cannot
  honestly stand in for its parent -- prefer composition instead.
- Expecting a leading underscore (or even name mangling) to enforce
  privacy; both are conventions, not access boundaries.
- Raising an exception directly from `__eq__`/`__add__` for an
  unsupported operand type instead of returning `NotImplemented`.
- Giving a dataclass field an unhashable mutable default
  (`tags: list = []`), which `@dataclass` rejects with `ValueError` while
  creating the class; use `field(default_factory=list)` instead.
- Defining `InsufficientFundsError` as a plain function-raised `ValueError`
  when a handler needs to inspect structured attributes like `.balance`.

## 🧾 Summary

- A class bundles per-instance state with the methods that validate and
  change it; a bound method remembers the instance it was accessed
  through.
- `@property`/`@classmethod`/`@staticmethod` each fit a different need:
  computed attribute access, class-aware construction, and
  neither-self-nor-cls helper behavior, respectively.
- Choose inheritance only for a genuine "is a" relationship; choose
  composition when one object merely needs another's help.
- Dunder methods integrate an object with `==`, `<`, `+`, `len()`, and
  iteration; return `NotImplemented` for unsupported operand types.
- `ABC`/`@abstractmethod` enforce a required interface; `@dataclass` with
  `field(default_factory=...)` removes boilerplate safely;
  `enum.Enum` closes a set of valid values.
- A custom exception can carry structured attributes, and is just another
  application of the subclassing mechanism this chapter already taught.

## ❓ Review questions (closed notes)

1. What is the difference between a class attribute and an instance
   attribute, and when would sharing state between instances be wrong?
2. When should a class method be used instead of a static method?
3. What test distinguishes a genuine inheritance relationship from one
   that should instead be composition?
4. What does name mangling actually change, and what does it not protect
   against?
5. Why should `__eq__`/`__add__` return `NotImplemented` instead of
   raising for an unsupported operand type?
6. Why does `field(default_factory=list)` matter for a dataclass field,
   compared to a bare `[]` default?
7. Why is defining `InsufficientFundsError(Exception)` in this chapter
   different from doing so before inheritance was taught?

## 📚 Authoritative references

- [Classes](https://docs.python.org/3/tutorial/classes.html)
- [`property`](https://docs.python.org/3/library/functions.html#property)
- [Data model -- special method names](https://docs.python.org/3/reference/datamodel.html#special-method-names)
- [`abc` -- Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [`enum`](https://docs.python.org/3/library/enum.html)

Once you can answer the review questions and have run all five lesson
files, continue to
[`exercises/09_object_oriented_programming/`](../../exercises/09_object_oriented_programming/README.md).
