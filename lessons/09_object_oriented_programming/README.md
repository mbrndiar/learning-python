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

## 🧩 Progressive syntax and mechanism

1. **Classes, `__init__`, and `self`.** Calling a class constructs an
   instance and passes it to `__init__` as `self`; attributes assigned
   through `self` are per-instance, while attributes assigned in the
   class body are shared.
2. **Bound methods.** `instance.method` is a bound method that remembers
   `instance`; `instance.method()` and `Class.method(instance)` do the
   same thing.
3. **`@property`, `@classmethod`, `@staticmethod`.** A property computes
   an attribute-like value on access; a class method receives `cls` (so
   subclasses construct themselves, not the base class); a static method
   needs neither `self` nor `cls`.
4. **Inheritance and `super()`.** `class Dog(Animal):` reuses and can
   override `Animal`'s behavior; `super().__init__(...)` and
   `super().speak()` call the parent's version explicitly.
5. **Composition.** An object can hold another object as an attribute and
   delegate work to it, without being a subtype of it.
6. **Encapsulation conventions.** `_name` signals "not part of the public
   API" by convention only; `__name` triggers name mangling
   (`_ClassName__name`), which reduces accidental collisions but is not
   an access boundary.
7. **The data model.** `__repr__`/`__str__` control representation;
   `__eq__`/`__lt__` control comparison (returning `NotImplemented`, not
   raising, for an unsupported operand type); `__add__` overloads `+`;
   `__len__`/`__iter__` support `len()` and `for`/`list()`.
8. **`abc.ABC`/`@abstractmethod`.** A class inheriting from `ABC` with at
   least one `@abstractmethod` cannot be instantiated until every
   abstract method is overridden.
9. **`@dataclass` and `field(default_factory=...)`.** A dataclass
   generates `__init__`/`__repr__`/`__eq__` from annotated fields;
   dataclasses reject an unhashable mutable default such as `[]`, while
   `field(default_factory=list)` validly gives each instance its own fresh
   list.
10. **`enum.Enum`.** Represents a closed, named set of related constants,
    preventing arbitrary values where only a fixed set is valid.
11. **Custom exceptions.** `class InsufficientFundsError(Exception):` is
    the same subclassing mechanism as any other class inheritance,
    applied to the exception hierarchy, and can carry structured
    attributes a handler reads directly.

## 📖 Read-predict-run-modify workflow

Work through all five lesson files in order, predicting each output
before running:

```bash
python lessons/09_object_oriented_programming/01_classes_objects_and_methods.py
python lessons/09_object_oriented_programming/02_composition_and_inheritance.py
python lessons/09_object_oriented_programming/03_properties_and_encapsulation.py
python lessons/09_object_oriented_programming/04_python_data_model.py
python lessons/09_object_oriented_programming/05_abcs_dataclasses_enums_and_domain_errors.py
```

### Expected output highlights

- `01_classes_objects_and_methods.py`: `Wheel.unit_circle() type: Wheel`
  -- the inherited class method constructs the subclass, not `Circle`.
- `02_composition_and_inheritance.py`: `Is Puppy a Cat? False` -- Puppy
  extends Dog, so the hierarchy stays truthful; swapping in a different
  `Engine` instance changes `car.start()`'s output without any change to
  `Car`'s own code.
- `03_properties_and_encapsulation.py`: assigning `account.balance = ...`
  raises `AttributeError` (`balance` has no setter); the mangled
  `_BankAccount__pin` attribute is still directly reachable.
- `04_python_data_model.py`: `Vector.__add__(Vector(1, 2), 3)` returns the
  literal object `NotImplemented`, not a raised exception.
- `05_abcs_dataclasses_enums_and_domain_errors.py`: instantiating `Shape()`
  directly raises `TypeError` listing its unimplemented abstract methods;
  `InsufficientFundsError` carries `.balance`/`.amount` a handler reads
  without parsing the message text.

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
