# 🗒️ Python Cheat Sheet & Glossary

A quick-reference companion to the lessons. Use it to jog your memory
after finishing the course, or while working through the exercises.

## 📖 Glossary

| Term | Meaning |
| --- | --- |
| Variable | A name bound to a value (`x = 5`) |
| Function | A reusable block of code, defined with `def` |
| Argument / Parameter | Values passed into a function |
| `*args` / `**kwargs` | Collect extra positional/keyword arguments |
| Bound method | A method value that remembers the instance supplied as `self` |
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
| Protocol | A structural interface describing required behavior |
| Dependency injection | Giving an object its collaborator instead of constructing it internally |
| Module | A single `.py` file that can be imported |
| Package | A namespace grouping importable modules; regular packages commonly contain `__init__.py` |
| Distribution package | An installable archive described by project metadata; it may provide one or more import packages |
| Virtual environment | An isolated Python installation for a single project (`venv`) |
| `pip` | Python's package installer |
| Unit test | An automated test that checks a small piece of code in isolation |
| Coroutine | An `async def` function, used with `await` for concurrency |
| JSON | A portable text representation of structured values |
| SQLite | An embedded relational database available through `sqlite3` |
| Primary key | A column or column set that uniquely identifies a row |
| Foreign key | A constraint referring to a key in another table |
| Transaction | A unit of database work committed or rolled back together |
| Index | A database structure trading write cost and space for selected faster reads |
| Repository | A boundary exposing domain-oriented persistence operations |
| HTTP request / response | A method, target, headers, and optional bytes sent to a server; then a status, headers, and optional bytes returned |
| REST API | An HTTP interface organized around resources and documented methods, routes, statuses, and representations |
| Finite timeout | A positive upper bound on how long an outbound operation may wait |
| Thread | A concurrent execution path sharing process memory |
| Process | An isolated interpreter and memory space that can run CPU work in parallel |
| Aware datetime | A date and time with enough time-zone information to identify an instant |

## ⚡ Quick syntax reference

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
def greet(name, /, greeting="Hello", *, uppercase=False):
    if uppercase:
        greeting = greeting.upper()
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

# Files and paths
from pathlib import Path

path = Path("file.txt")
with path.open("w", encoding="utf-8") as file:
    file.write("hello")

binary_path = Path("payload.bin")
with binary_path.open("wb") as file:
    file.write(b"\x00\xff")
with binary_path.open("rb") as file:
    payload = file.read()

folder = Path("output")
folder.mkdir(parents=True, exist_ok=True)
python_files = sorted(folder.rglob("*.py"))

# JSON
import json

text = json.dumps({"name": "Ada", "active": True})
data = json.loads(text)

# Parameterized SQLite
import sqlite3
from contextlib import closing

with closing(sqlite3.connect(":memory:")) as connection:
    connection.execute(
        "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)"
    )
    with connection:  # commits on success, rolls back when an exception escapes
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            ("Use parameters",),
        )
    rows = connection.execute(
        "SELECT id, title FROM tasks ORDER BY id"
    ).fetchall()

# HTTP client boundary
from urllib.request import Request, urlopen

request = Request(
    "http://127.0.0.1:8000/tasks/1",
    headers={"Accept": "application/json"},
)
with urlopen(request, timeout=5.0) as response:
    if response.status != 200:
        raise RuntimeError(f"unexpected HTTP status: {response.status}")
    task = json.loads(response.read().decode("utf-8"))

# Decorators
from functools import wraps


def logged(func):
    @wraps(func)
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

def find_name(user_id: int, names: dict[int, str]) -> str | None:
    return names.get(user_id)
```

## 🧰 Core type operations

| Goal | Example |
| --- | --- |
| inspect a type | `type(value)`, `isinstance(value, str)` |
| convert a value | `int("42")`, `float("2.5")`, `str(42)`, `bool(value)` |
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

## 🔢 Numbers, text, and bytes

```python
import math
from decimal import Decimal
from fractions import Fraction

price = Decimal("19.99")          # construct exact decimal input from text
ratio = Fraction(3, 4)            # exact rational value
close_enough = math.isclose(0.1 + 0.2, 0.3)

text = "café"
payload = text.encode("utf-8")    # str -> bytes
decoded = payload.decode("utf-8") # bytes -> str
mutable = bytearray(payload)
view = memoryview(mutable)        # view without copying the buffer
```

Binary `float` is appropriate for measurements and approximate computation.
Use `Decimal` when a decimal rounding contract matters and `Fraction` for exact
rational arithmetic. Do not construct a `Decimal` from an already approximated
float when the original decimal text is available.

## 📞 Function call contracts

```python
def connect(host, /, port=443, *, timeout=5.0):
    return host, port, timeout

positionals = ("example.com", 8443)
options = {"timeout": 2.0}
connect(*positionals, **options)
```

Parameters before `/` are positional-only; parameters after a bare `*` are
keyword-only. Arguments are bound to local names by assignment. Mutating a
shared mutable object can be visible to the caller; rebinding the local
parameter cannot replace the caller's reference.

## 🔭 Scope, copying, and identity

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

## 🛡️ Exceptions and context managers

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

## 📦 Imports and script entry points

```python
import math
from pathlib import Path

if __name__ == "__main__":
    main()
```

Top-level module code executes on first import. Protect application startup so
the module can also be imported safely by tests or other modules.

## 🕐 Dates, times, and clocks

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

instant = datetime.fromisoformat("2026-07-17T21:00:00+00:00")
prague = instant.astimezone(ZoneInfo("Europe/Prague"))
later = instant + timedelta(minutes=30)
unix_seconds = instant.timestamp()
restored = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)
```

Prefer aware datetimes for real instants and normalize storage or interchange
deliberately, commonly to UTC. State timestamp units. Use `time.monotonic()` for
elapsed duration because wall-clock time can be adjusted.

## 🖥️ Environment, processes, and streams

```python
import os
import subprocess
import sys

mode = os.environ.get("APP_MODE", "development")
result = subprocess.run(
    [sys.executable, "-c", "print('child')"],
    check=True,
    capture_output=True,
    text=True,
    timeout=5,
    env=os.environ.copy(),
)
print(result.stdout, end="")
```

Pass subprocess arguments as a sequence. Do not interpolate untrusted values
into a shell command. Write diagnostics to `sys.stderr` and return a nonzero
exit status when a CLI cannot complete its request.

## 🧪 Testing reminders

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

## ⌨️ Command-line quick reference

```bash
python3 --version                 # check Python version
python3 -m venv .venv             # create a virtual environment
source .venv/bin/activate         # activate it (Linux/macOS)
python -m pip install -r requirements-dev.txt  # tools + Task project libraries
python -m pip list                # inspect installed packages
python -m pip freeze              # snapshot this environment
python -m pip install -e path/to/project  # editable local distribution
python -m build path/to/project   # build wheel + source distribution
python script.py arg1 --flag      # run a script with arguments
python -m unittest discover       # run all unittest tests
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
ruff format .                     # format files
ruff check .                      # lint
ruff format --check .             # verify formatting
mypy                              # statically check project annotations
python scripts/erase_coverage_data.py  # clear normal + parallel coverage data
coverage run -m unittest ...      # execute tests while measuring
coverage report                   # show measured test coverage
```

Task project checks use an environment variable to select the matching source
root:

```bash
PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests -q
PROJECT_IMPLEMENTATION=solution python -m pytest projects/tasks/tests -q

python scripts/erase_coverage_data.py
PROJECT_IMPLEMENTATION=solution \
  coverage run -m pytest projects/tasks/tests -q
coverage report --include="projects/tasks/solution/**/*.py"
```

Optional equivalent setup with [uv](https://docs.astral.sh/uv/):

```bash
uv python install 3.14
uv venv --python 3.14
uv pip install -r requirements-dev.txt
source .venv/bin/activate
python script.py
python -m pytest lessons/09_tooling_and_debugging/04_pytest_basics.py
ruff format .
ruff check .
mypy
```

## 🚀 Advanced course sequence

1. [Module 14: SQL and SQLite](lessons/10_sql_and_sqlite/README.md)
2. [Module 15: REST APIs and HTTP Clients](lessons/11_rest_apis_and_clients/README.md)
3. Required [Task REST API and clients project](projects/tasks/README.md)
4. [Module 16: Concurrency](lessons/12_concurrency/README.md)
5. Both required [capstones](capstones/README.md)

## 🧭 Where to go next

- [Python official documentation](https://docs.python.org/3/)
- [pytest documentation](https://docs.pytest.org/en/stable/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [Coverage.py documentation](https://coverage.readthedocs.io/en/stable/)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Python Packaging User Guide](https://packaging.python.org/)
- [build documentation](https://build.pypa.io/en/stable/)
- [pip local project installs](https://pip.pypa.io/en/stable/topics/local-project-installs/)
- [`pydoc` documentation](https://docs.python.org/3/library/pydoc.html)
- [Real Python](https://realpython.com/) - in-depth tutorials
- [PEP 8](https://peps.python.org/pep-0008/) - the official style guide

When references disagree, prefer the documentation for the Python version you
are running. Check it with `python --version`.
