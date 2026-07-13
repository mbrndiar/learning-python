# learning-python

A collection of hands-on lessons for learning Python from scratch. Each lesson
is a small, self-contained, runnable script with comments explaining the
concepts. The course also includes practice exercises with solutions, a
capstone project, and a cheat sheet, so it can be used as a standalone,
self-taught path to learning Python.

## Requirements

- Python 3.9+ (the lessons themselves need no external dependencies)
- A couple of lessons and the exercises optionally use `pytest`; install it
  with `pip install -r requirements-dev.txt`

New to Python or setting up for the first time? See
[`docs/SETUP.md`](docs/SETUP.md) for installing Python, creating a virtual
environment, and choosing an editor.

## How to run a lesson

From the repository root, run any lesson file with:

```bash
python lessons/01_basics/01_hello_world.py
```

## Practice exercises

Each module has a matching folder under [`exercises/`](exercises/README.md)
with hands-on problems to implement yourself, plus reference solutions to
check your work. After finishing a lesson, do its exercises before moving on.

## Capstone project

Once you've completed the course, build on what you've learned with the
[Task Manager capstone project](project/task_manager/README.md) - a small
command-line to-do app that combines classes, custom exceptions, file
persistence, argparse, and unit tests.

## Cheat sheet

[`CHEATSHEET.md`](CHEATSHEET.md) is a one-page glossary and syntax quick
reference to jog your memory after finishing the course.

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
7. **Advanced Python** (`lessons/07_advanced_python/`)
   - `01_decorators.py` – function decorators, decorator factories and
     `functools.wraps`
   - `02_generators_and_iterators.py` – `yield`, generator expressions and
     the iterator protocol (`__iter__` / `__next__`)
   - `03_type_hints.py` – annotating variables, functions and classes with
     the `typing` module
8. **Testing** (`lessons/08_testing/`)
   - `01_unittest_basics.py` – writing and running tests with the
     `unittest` standard-library framework
9. **Tooling and Debugging** (`lessons/09_tooling_and_debugging/`)
   - `01_virtual_environments_and_pip.py` – virtual environments, `pip`,
     and why to use them
   - `02_debugging_and_tracebacks.py` – reading tracebacks, common
     errors, and the interactive debugger
   - `03_command_line_arguments.py` – `input()` and parsing CLI
     arguments with `argparse`
   - `04_pytest_basics.py` – an introduction to `pytest` as an
     alternative to `unittest`
10. **Concurrency** (`lessons/10_concurrency/`)
    - `01_threading_and_multiprocessing.py` – `threading` for I/O-bound
      work and `multiprocessing` for CPU-bound work
    - `02_asyncio_basics.py` – `async`/`await` and `asyncio.gather`

Work through the lessons in order, read the comments, then try modifying the
code to experiment with the concepts. After each module, complete the
matching exercises in [`exercises/`](exercises/README.md) to practice what
you learned.