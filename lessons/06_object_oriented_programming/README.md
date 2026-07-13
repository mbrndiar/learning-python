# Module 6: Object-Oriented Programming

How to bundle data and behavior together into classes, and the main OOP
tools Python offers.

## Concepts covered

- **`01_classes_and_objects.py`** - defining classes, `__init__`,
  instance vs. class attributes, methods and properties.
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

## Running

```bash
python lessons/06_object_oriented_programming/01_classes_and_objects.py
python lessons/06_object_oriented_programming/02_inheritance_and_polymorphism.py
python lessons/06_object_oriented_programming/03_encapsulation_and_magic_methods.py
python lessons/06_object_oriented_programming/04_abstract_classes_and_dataclasses.py
```

Once you've read through all four files, practice what you learned in
[`exercises/06_object_oriented_programming/`](../../exercises/06_object_oriented_programming/README.md).
