# 🏗️ Module 6: Object-Oriented Programming

How to bundle data and behavior together into classes, and the main OOP
tools Python offers.

## 🎯 Learning objectives

After this module, you should be able to model related state and behavior,
distinguish class and instance data, use composition or inheritance
deliberately, define useful object protocols, and reduce data-class
boilerplate.

## 🧱 Objects and classes

A class creates a new type; calling it constructs an instance. `self` is the
instance receiving a method call and is supplied automatically:

```python
class BankAccount:
    currency = "EUR"  # shared class attribute

    def __init__(self, owner, balance=0):
        self.owner = owner       # per-instance attributes
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
```

Instance lookup checks the instance and then its class hierarchy. Avoid
mutable class attributes for per-instance state. A property exposes method
logic through attribute syntax and is useful for a computed value or a stable
interface—not merely to imitate getters and setters from another language.

Accessing an instance method through an instance creates a **bound method**:
the instance is remembered and will be supplied as `self` when the method is
called. Therefore `account.deposit(10)` is equivalent in effect to
`BankAccount.deposit(account, 10)`, although normal code uses the bound form.

Use `@classmethod` for behavior that receives the class as `cls`, such as an
alternative constructor that should also construct subclasses. Use
`@staticmethod` only for closely related behavior that genuinely needs neither
an instance nor the class; a module-level function is often clearer otherwise.

## 🧩 Composition and inheritance

Composition gives one object another object to delegate work to ("has a").
Inheritance specializes a genuine subtype ("is a"). Prefer composition when
the relationship is only code reuse. An overriding method can call its parent
implementation with `super()`. Polymorphism means callers rely on supported
behavior rather than checking exact types.

Python uses naming conventions rather than absolute access restrictions:
`_name` means non-public API, while `__name` triggers name mangling to reduce
accidental clashes in subclasses. Neither mechanism makes data secure.

## ✨ Object protocols

Special methods let instances participate in Python syntax. `__repr__` should
give a developer-oriented representation; `__str__` gives user-facing text.
`__eq__`, `__lt__`, `__len__`, `__iter__`, and context-manager methods support
comparison and built-in operations. Return `NotImplemented` from binary
protocol methods when the other operand is unsupported.

A special method should preserve the ordinary meaning of its protocol.
`__len__` should describe a non-negative item count, not an unrelated numeric
property merely because `len(obj)` looks convenient. Prefer a named method or a
more suitable conversion protocol when the meaning would surprise a caller.

Abstract base classes can require methods from concrete subclasses.
`@dataclass` can generate initialization, representation, and equality for
data-oriented classes. Use `field(default_factory=list)` rather than `[]` for
mutable defaults. An `Enum` represents a closed set of named values.

Use these tools for different jobs: an ABC defines a nominal family with
required operations, a dataclass removes record-like boilerplate, and an Enum
prevents arbitrary values where the valid choices are closed. They can be
combined, but none is a general replacement for thoughtful class design.

## 📚 Concepts covered

- **`01_classes_and_objects.py`** - defining classes, `__init__`, instance vs.
  class attributes, bound instance methods, class and static methods, and
  properties.
- **`02_inheritance_and_polymorphism.py`** - inheritance (a class reusing
  and extending another's behavior), `super()`, and polymorphism
  (different classes responding to the same method call in their own
  way).
- **`03_encapsulation_and_magic_methods.py`** - encapsulation
  (protected/private attributes by convention) and magic/dunder methods
  such as `__repr__`, `__eq__` and `__add__` that integrate objects with
  Python's built-in operators and functions.
- **`04_abstract_classes_and_dataclasses.py`** - abstract base classes
  with `abc.ABC` / `@abstractmethod` to enforce an interface, `@dataclass`
  to reduce boilerplate for data-holding classes, and `enum.Enum` for
  fixed sets of named constants.

## ▶️ Running

```bash
python lessons/06_object_oriented_programming/01_classes_and_objects.py
python lessons/06_object_oriented_programming/02_inheritance_and_polymorphism.py
python lessons/06_object_oriented_programming/03_encapsulation_and_magic_methods.py
python lessons/06_object_oriented_programming/04_abstract_classes_and_dataclasses.py
```

Once you've read through all four files, practice what you learned in
[`exercises/06_object_oriented_programming/`](../../exercises/06_object_oriented_programming/README.md).

## ⚠️ Common mistakes

- Storing per-instance mutable state as a class attribute.
- Using inheritance only to share implementation.
- Calling methods on the class when an instance is required.
- Using a static method for an alternative constructor that should respect
  subclasses.
- Expecting a leading underscore to enforce privacy.
- Giving a data class a mutable default without `default_factory`.

## ❓ Review questions

1. Where should state unique to one object be initialized?
2. How do composition and inheritance express different relationships?
3. What does `super()` resolve?
4. When is a property useful?
5. What does a bound method remember?
6. When should an alternative constructor be a class method?
7. Why should unsupported binary operations return `NotImplemented`?
