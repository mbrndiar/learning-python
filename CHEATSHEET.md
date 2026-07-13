# Python Cheat Sheet & Glossary

A quick-reference companion to the lessons. Use it to jog your memory
after finishing the course, or while working through the exercises.

## Glossary

| Term | Meaning |
| --- | --- |
| Variable | A name bound to a value (`x = 5`) |
| Function | A reusable block of code, defined with `def` |
| Argument / Parameter | Values passed into a function |
| `*args` / `**kwargs` | Collect extra positional/keyword arguments |
| Closure | A function that remembers variables from its enclosing scope |
| List / Tuple | Ordered collections; lists are mutable, tuples are not |
| Dict | A mapping of keys to values (`{"a": 1}`) |
| Set | An unordered collection of unique values |
| Comprehension | A compact way to build a list/dict/set (`[x*x for x in range(5)]`) |
| Class | A blueprint for creating objects, defined with `class` |
| Instance | A concrete object created from a class |
| Inheritance | A class reusing/extending behavior from a parent class |
| `self` | The instance a method is being called on |
| Exception | An error raised during execution, handled with `try`/`except` |
| Context manager | An object usable with `with`, guaranteeing setup/cleanup (`open()`) |
| Decorator | A function that wraps another function to add behavior (`@decorator`) |
| Generator | A function using `yield` to produce values lazily |
| Type hint | An annotation describing expected types (`def f(x: int) -> str`) |
| Module | A single `.py` file that can be imported |
| Package | A namespace grouping importable modules; regular packages commonly contain `__init__.py` |
| Virtual environment | An isolated Python installation for a single project (`venv`) |
| `pip` | Python's package installer |
| Unit test | An automated test that checks a small piece of code in isolation |
| Coroutine | An `async def` function, used with `await` for concurrency |

## Quick syntax reference

```python
# Variables and types
x = 5
name = "Ada"
pi = 3.14
is_ready = True

# Conditionals
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
else:
    print("negative")

# Loops
for item in [1, 2, 3]:
    print(item)

while x > 0:
    x -= 1

# Functions
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Lists, dicts, sets, comprehensions
numbers = [1, 2, 3]
squares = [n * n for n in numbers]
lookup = {n: n * n for n in numbers}
unique = {1, 2, 2, 3}

# Classes
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError


class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

# Exceptions
try:
    1 / 0
except ZeroDivisionError as error:
    print("Error:", error)
finally:
    print("Always runs")

# Files
with open("file.txt", "w", encoding="utf-8") as file:
    file.write("hello")

# Decorators
def logged(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Generators
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# Type hints
def add(a: int, b: int) -> int:
    return a + b
```

## Core type operations

| Goal | Example |
| --- | --- |
| inspect a type | `type(value)`, `isinstance(value, str)` |
| convert a value | `int("42")`, `str(42)`, `list(items)` |
| length | `len(items)` |
| membership | `item in items`, `key in mapping` |
| index and slice | `items[0]`, `items[-1]`, `items[1:4]` |
| enumerate values | `enumerate(items, start=1)` |
| pair iterables | `zip(names, scores)` |
| sort without mutation | `sorted(items, key=..., reverse=True)` |
| aggregate numbers | `sum(values)`, `min(values)`, `max(values)` |
| test conditions | `any(checks)`, `all(checks)` |

### Common collection methods

```python
items.append(value)
items.extend(more_items)
items.pop()                    # remove and return final item

mapping.get(key, default)
mapping.items()                # dynamic (key, value) view
mapping.setdefault(key, value)

unique.add(value)
left | right                   # union
left & right                   # intersection
left - right                   # difference
```

Most methods that mutate a collection return `None`. `list.sort()` mutates;
`sorted(iterable)` returns a new list.

## Scope, copying, and identity

Names resolve in Local, Enclosing, Global, then Built-in scope (LEGB).
Assignment binds another name to the same object:

```python
alias = original
shallow = original.copy()      # nested values may remain shared

left == right                  # equivalent values
left is right                  # the same object
value is None                  # canonical identity check
```

Use `copy.deepcopy()` only when an independent recursive copy is required.

## Exceptions and context managers

```python
try:
    value = int(raw)
except ValueError as error:
    print(error)
else:
    print("conversion succeeded")
finally:
    print("always runs")

with open("file.txt", encoding="utf-8") as file:
    text = file.read()
```

Catch the narrowest exception you can meaningfully handle. Use `raise` to
signal failure and `raise NewError(...) from error` to preserve its cause.

## Imports and script entry points

```python
import math
from pathlib import Path

if __name__ == "__main__":
    main()
```

Top-level module code executes on first import. Protect application startup so
the module can also be imported safely by tests or other modules.

## Testing reminders

```python
import unittest

class TestExample(unittest.TestCase):
    def test_result(self):
        self.assertEqual(calculate(2), 4)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            calculate(-1)
```

Test normal behavior, boundaries, empty input, and expected failures. Keep
tests independent and deterministic.

## Command-line quick reference

```bash
python3 --version                 # check Python version
python3 -m venv .venv             # create a virtual environment
source .venv/bin/activate         # activate it (Linux/macOS)
pip install <package>             # install a package
python -m pip install <package>   # use pip belonging to this Python
pip freeze > requirements.txt     # save installed packages
python script.py arg1 --flag      # run a script with arguments
python -m unittest discover       # run all unittest tests
pytest                            # run all pytest tests
```

## Where to go next

- [Python official documentation](https://docs.python.org/3/)
- [Real Python](https://realpython.com/) - in-depth tutorials
- [PEP 8](https://peps.python.org/pep-0008/) - the official style guide

When references disagree, prefer the documentation for the Python version you
are running. Check it with `python --version`.
