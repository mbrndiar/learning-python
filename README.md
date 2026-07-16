# 🐍 learning-python

A complete, hands-on introduction to Python for independent learners. The
course combines written explanations, small runnable programs, exercises with
solutions, review questions, two capstone projects, and a syntax reference. No
previous programming experience is assumed.

## 🎯 What you will learn

By the end of the course, you will be able to:

- read, write, run, and debug Python programs;
- choose suitable data types and control program flow;
- decompose problems into functions, modules, and classes;
- read and write files and handle failures safely;
- exchange structured data with JSON and persist records in SQLite;
- use Python's iterator, generator, decorator, and type-hinting features;
- create isolated environments and install third-party packages;
- test programs with `unittest` and
  [pytest](https://docs.pytest.org/en/stable/);
- build command-line programs and small HTTP/JSON integrations;
- select an appropriate concurrency model for I/O- or CPU-bound work;
- implement and test a versioned SQLite CLI against a frozen behavioral
  contract; and
- design a strictly typed ingestion and reporting pipeline with streaming I/O,
  SQLite, injected HTTP, and bounded concurrency.

## ✅ Requirements

- Python 3.11+ (the lessons themselves need no external dependencies)
- The lessons use only the standard library at runtime. Install the development
  tools ([pytest](https://docs.pytest.org/en/stable/),
  [Ruff](https://docs.astral.sh/ruff/),
  [mypy](https://mypy.readthedocs.io/en/stable/), and
  [Coverage.py](https://coverage.readthedocs.io/en/stable/)) with
  `python -m pip install -r requirements-dev.txt`.

New to Python or setting up for the first time? See
[`docs/SETUP.md`](docs/SETUP.md) for installing Python, creating a virtual
environment, and choosing an editor.

## ▶️ How to run a lesson

From the repository root, run any lesson file with:

```bash
python lessons/01_basics/01_hello_world.py
```

Do not only run the files. For each module:

1. Read its `README.md`, including the examples and common mistakes.
2. Predict a lesson script's output before running it.
3. Run the script, then change values and observe what changes.
4. Answer the module's review questions without looking back.
5. Complete its exercises before reading `solutions.py`.
6. Revisit anything you could not explain in your own words.

The modules build on one another. Beginners should follow them in order.

## 🔁 Developer feedback loop

When you change code, first run the smallest relevant example or test. After it
passes, widen the feedback:

```bash
python scripts/check_markdown_links.py
ruff format .
ruff check .
mypy
python -m compileall -q \
  capstones/comparative/starter capstones/comparative/solution \
  capstones/idiomatic/starter capstones/idiomatic/solution
(cd capstones/comparative/spec && sha256sum -c MANIFEST.sha256)
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/comparative/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=starter python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_harness.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/comparative/tests -p 'test_*.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py' -v
```

The starter packages are also strict-type-checked as learner scaffolding:

```bash
mypy --strict \
  capstones/comparative/starter/comparative_kv \
  capstones/idiomatic/starter/ingest_report
```

Module 9 explains what each tool checks, how to measure coverage, and how these
local commands map to
[GitHub Actions](https://docs.github.com/en/actions). The
[setup guide](docs/SETUP.md#optional-modern-setup-with-uv) also provides the
equivalent optional [uv](https://docs.astral.sh/uv/) workflow.

## 📐 Conventions used in this course

- Code intended for a terminal is marked `bash`; Python code is marked
  `python`.
- `>>>` denotes an interactive Python prompt. Do not type the prompt itself.
- `...` in a code sample means omitted code; it is not always literal input.
- Names such as `value` or `items` are placeholders you may replace.
- Examples use four spaces for indentation, as Python convention requires.
- An exception shown intentionally is part of the lesson, not a broken example.

## 🧠 Practice exercises

Each module has a matching folder under [`exercises/`](exercises/README.md)
with hands-on problems to implement yourself, plus reference solutions to
check your work. After finishing a lesson, do its exercises before moving on.

## 🏆 Capstone projects

Once you've completed the course, build both equally required
[capstone projects](capstones/README.md):

- the [comparative SQLite key/value store](capstones/comparative/README.md);
- the [idiomatic ingestion and reporting pipeline](capstones/idiomatic/README.md).

Use each guided starter one milestone at a time, writing a test before or
alongside each change. Compare with the reference solution only after the
selected milestone tests pass.

The predecessor Task Manager, REST API, and client examples have been removed;
they are not a third capstone. See the
[capstone migration guide](docs/CAPSTONE_MIGRATION.md) for concept mappings and
the exact Git revision that still contains their source.

## 🗒️ Cheat sheet

[`CHEATSHEET.md`](CHEATSHEET.md) is a one-page glossary and syntax quick
reference to jog your memory after finishing the course.

<a id="course-outline"></a>

## 🗺️ Course outline

1. **[Basics](lessons/01_basics/)**
   - [`01_hello_world.py`](lessons/01_basics/01_hello_world.py) – printing your first message
   - [`02_variables_and_types.py`](lessons/01_basics/02_variables_and_types.py) – variables and basic data types
   - [`03_operators.py`](lessons/01_basics/03_operators.py) – arithmetic, comparison and logical operators
   - [`04_strings.py`](lessons/01_basics/04_strings.py) – working with strings
2. **[Control Flow](lessons/02_control_flow/)**
   - [`01_conditionals.py`](lessons/02_control_flow/01_conditionals.py) – `if` / `elif` / `else`
   - [`02_loops.py`](lessons/02_control_flow/02_loops.py) – `for` and `while` loops
3. **[Functions](lessons/03_functions/)**
   - [`01_functions.py`](lessons/03_functions/01_functions.py) – defining and calling functions, default/keyword
     arguments, `*args` and `**kwargs`
   - [`02_lambdas_closures_and_recursion.py`](lessons/03_functions/02_lambdas_closures_and_recursion.py) – lambda expressions, closures
     (including `nonlocal`) and recursive functions
4. **[Data Structures](lessons/04_data_structures/)**
   - [`01_lists_and_tuples.py`](lessons/04_data_structures/01_lists_and_tuples.py) – lists, tuples and list comprehensions
   - [`02_dictionaries_and_sets.py`](lessons/04_data_structures/02_dictionaries_and_sets.py) – dictionaries and sets
   - [`03_comprehensions_and_collections.py`](lessons/04_data_structures/03_comprehensions_and_collections.py) – list/dict/set/generator
     comprehensions and the `collections` module (`Counter`, `defaultdict`,
     `namedtuple`, `OrderedDict`)
5. **[Modules and Files](lessons/05_modules_and_files/)**
   - [`01_modules.py`](lessons/05_modules_and_files/01_modules.py) – using the standard library (`math`, `random`, `datetime`)
   - [`02_packages.py`](lessons/05_modules_and_files/02_packages.py) – modules vs. packages, absolute/relative imports,
     `__init__.py` re-exports and `__all__`
   - [`03_files_and_exceptions.py`](lessons/05_modules_and_files/03_files_and_exceptions.py) – reading/writing files and handling errors
   - [`04_custom_exceptions_and_context_managers.py`](lessons/05_modules_and_files/04_custom_exceptions_and_context_managers.py) – defining custom
     exception classes and writing your own context managers
   - [`05_json_and_structured_data.py`](lessons/05_modules_and_files/05_json_and_structured_data.py) – serializing structured data with JSON
6. **[Object-Oriented Programming](lessons/06_object_oriented_programming/)**
   - [`01_classes_and_objects.py`](lessons/06_object_oriented_programming/01_classes_and_objects.py) – classes, attributes, methods and properties
   - [`02_inheritance_and_polymorphism.py`](lessons/06_object_oriented_programming/02_inheritance_and_polymorphism.py) – inheritance, `super()` and
     polymorphism
   - [`03_encapsulation_and_magic_methods.py`](lessons/06_object_oriented_programming/03_encapsulation_and_magic_methods.py) – protected/private attributes
     and dunder methods (`__repr__`, `__eq__`, `__add__`, etc.)
   - [`04_abstract_classes_and_dataclasses.py`](lessons/06_object_oriented_programming/04_abstract_classes_and_dataclasses.py) – abstract base classes,
     `@dataclass` and `enum.Enum`
7. **[Advanced Python](lessons/07_advanced_python/)**
   - [`01_decorators.py`](lessons/07_advanced_python/01_decorators.py) – function decorators, decorator factories and
     `functools.wraps`
   - [`02_generators_and_iterators.py`](lessons/07_advanced_python/02_generators_and_iterators.py) – `yield`, generator expressions and
     the iterator protocol (`__iter__` / `__next__`)
   - [`03_type_hints.py`](lessons/07_advanced_python/03_type_hints.py) – annotating variables, functions and classes with
     modern Python type syntax
   - [`04_protocols_and_dependency_injection.py`](lessons/07_advanced_python/04_protocols_and_dependency_injection.py) – structural interfaces,
     dependency injection and adapters
8. **[Testing](lessons/08_testing/)**
   - [`01_unittest_basics.py`](lessons/08_testing/01_unittest_basics.py) – writing and running tests with the
     `unittest` standard-library framework
9. **[Tooling and Debugging](lessons/09_tooling_and_debugging/)**
   - [`01_virtual_environments_and_pip.py`](lessons/09_tooling_and_debugging/01_virtual_environments_and_pip.py) – virtual environments, `pip`,
     and why to use them
   - [`02_debugging_and_tracebacks.py`](lessons/09_tooling_and_debugging/02_debugging_and_tracebacks.py) – reading tracebacks, common
     errors, and the interactive debugger
   - [`03_command_line_arguments.py`](lessons/09_tooling_and_debugging/03_command_line_arguments.py) – `input()` and parsing CLI
     arguments with `argparse`
   - [`04_pytest_basics.py`](lessons/09_tooling_and_debugging/04_pytest_basics.py) – an introduction to
     [pytest](https://docs.pytest.org/en/stable/) as an
     alternative to `unittest`
   - [`05_logging_and_quality_tools.py`](lessons/09_tooling_and_debugging/05_logging_and_quality_tools.py) – structured diagnostics,
     [Ruff](https://docs.astral.sh/ruff/),
     [mypy](https://mypy.readthedocs.io/en/stable/), and
     [Coverage.py](https://coverage.readthedocs.io/en/stable/)
10. **[Application Integration](lessons/10_application_integration/)**
    - [`01_sqlite_basics.py`](lessons/10_application_integration/01_sqlite_basics.py) – storing and querying records with SQLite
    - [`02_http_and_json.py`](lessons/10_application_integration/02_http_and_json.py) – HTTP routes, JSON boundaries and clients
11. **[Concurrency](lessons/11_concurrency/)**
    - [`01_threading_and_multiprocessing.py`](lessons/11_concurrency/01_threading_and_multiprocessing.py) – `threading` for I/O-bound
      work and `multiprocessing` for CPU-bound work
    - [`02_asyncio_basics.py`](lessons/11_concurrency/02_asyncio_basics.py) – `async`/`await` and `asyncio.gather`

Work through the lessons in order, read the comments, then try modifying the
code to experiment with the concepts. After each module, complete the
matching exercises in [`exercises/`](exercises/README.md) to practice what
you learned.

## 🆘 Getting help from the material

When something fails, read the final line of the traceback first: it names the
exception and usually explains the immediate cause. Then inspect the referenced
line in your code and work upward through the traceback. Search this repository
for the exception or concept before consulting another source. Module 9 gives a
systematic debugging process.

Solutions are examples, not the only correct answers. Compare behavior,
readability, handling of edge cases, and tests rather than requiring identical
code.

## 🧭 Course boundaries

This course aims to make a beginner independently productive with core Python.
Python's ecosystem is much larger than any single introductory course:
specialized work such as web development, data science, machine learning,
desktop interfaces, and cloud deployment requires domain-specific study after
the foundations here. The final section of [`CHEATSHEET.md`](CHEATSHEET.md)
points to authoritative references for continued learning.