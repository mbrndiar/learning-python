# learning-python

A collection of hands-on lessons for learning Python from scratch. Each lesson
is a small, self-contained, runnable script with comments explaining the
concepts.

## Requirements

- Python 3.9+ (no external dependencies required)

## How to run a lesson

From the repository root, run any lesson file with:

```bash
python lessons/01_basics/01_hello_world.py
```

## Course outline

1. **Basics** (`lessons/01_basics/`)
   - `01_hello_world.py` – printing your first message
   - `02_variables_and_types.py` – variables and basic data types
   - `03_operators.py` – arithmetic, comparison and logical operators
   - `04_strings.py` – working with strings
2. **Control Flow** (`lessons/02_control_flow/`)
   - `01_conditionals.py` – `if` / `elif` / `else`
   - `02_loops.py` – `for` and `while` loops
3. **Functions** (`lessons/03_functions/`)
   - `01_functions.py` – defining and calling functions, default/keyword
     arguments, `*args` and `**kwargs`
   - `02_lambdas_closures_and_recursion.py` – lambda expressions, closures
     (including `nonlocal`) and recursive functions
4. **Data Structures** (`lessons/04_data_structures/`)
   - `01_lists_and_tuples.py` – lists, tuples and list comprehensions
   - `02_dictionaries_and_sets.py` – dictionaries and sets
   - `03_comprehensions_and_collections.py` – list/dict/set/generator
     comprehensions and the `collections` module (`Counter`, `defaultdict`,
     `namedtuple`, `OrderedDict`)
5. **Modules and Files** (`lessons/05_modules_and_files/`)
   - `01_modules.py` – using the standard library (`math`, `random`, `datetime`)
   - `02_files_and_exceptions.py` – reading/writing files and handling errors
   - `03_custom_exceptions_and_context_managers.py` – defining custom
     exception classes and writing your own context managers
6. **Object-Oriented Programming** (`lessons/06_object_oriented_programming/`)
   - `01_classes_and_objects.py` – classes, attributes, methods and properties
   - `02_inheritance_and_polymorphism.py` – inheritance, `super()` and
     polymorphism
   - `03_encapsulation_and_magic_methods.py` – protected/private attributes
     and dunder methods (`__repr__`, `__eq__`, `__add__`, etc.)
   - `04_abstract_classes_and_dataclasses.py` – abstract base classes,
     `@dataclass` and `enum.Enum`

Work through the lessons in order, read the comments, then try modifying the
code to experiment with the concepts.