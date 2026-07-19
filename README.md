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
- distinguish text from binary data and choose suitable numeric representations;
- navigate files and directories, represent time explicitly, and handle failures
  safely;
- exchange structured data with JSON and persist records in SQLite;
- use Python's iterator, generator, decorator, and type-hinting features;
- create isolated environments, install third-party packages, and build a small
  documented distribution;
- test programs with `unittest` and
  [pytest](https://docs.pytest.org/en/stable/);
- build command-line programs and small HTTP/JSON integrations;
- cross environment, standard-stream, exit-status, and subprocess boundaries
  safely;
- complete a required Task project with SQLite and Markdown repositories, three
  server adapters, and three client transports;
- select an appropriate concurrency model for I/O- or CPU-bound work;
- implement and test a versioned SQLite CLI against a frozen behavioral
  contract; and
- design a strictly typed ingestion and reporting pipeline with streaming I/O,
  SQLite, injected HTTP, and bounded concurrency.

## ✅ Requirements

- Python 3.11 through 3.14. CI validates the oldest and newest supported
 versions; newer Python releases may work but are outside the current verified
 course range.
- The documented interpreter is CPython on Linux, macOS, or Windows. GitHub
 Actions verifies Ubuntu; platform-specific commands and project limitations
 are called out where they matter.
- The core lesson scripts in Modules 1–10, Module 11's HTTP fundamentals
  lesson, Module 12, and both capstones use only the standard library. Module
  9's pytest and packaging labs, Module 11's Flask, FastAPI, `requests`, and
  `httpx` comparisons, and the Task project use development or runtime
  dependencies from this repository.
  Task runtime dependencies are declared in
  [`projects/tasks/requirements.txt`](projects/tasks/requirements.txt).
- Install those dependencies and the development tools
  ([pytest](https://docs.pytest.org/en/stable/),
  [build](https://build.pypa.io/en/stable/),
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
  capstones/idiomatic/starter/ingest_report \
  projects/tasks/starter
PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests -q
PROJECT_IMPLEMENTATION=solution python -m pytest projects/tasks/tests -q
```

The project and capstones have independent branch-coverage gates. Measure the
project solution without allowing the mature capstones to hide gaps:

```bash
python scripts/erase_coverage_data.py
PROJECT_IMPLEMENTATION=solution \
  coverage run -m pytest projects/tasks/tests -q
coverage report --include="projects/tasks/solution/**/*.py"
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
check your work. After Module 11, complete the required
[Task REST API and clients project](projects/tasks/README.md) before moving to
Module 12.

## 🏆 Capstone projects

Once you've completed all 12 modules and the required applied project, build both
equally required
[capstone projects](capstones/README.md):

- the [comparative SQLite key/value store](capstones/comparative/README.md);
- the [idiomatic ingestion and reporting pipeline](capstones/idiomatic/README.md).

Use each guided starter one milestone at a time, writing a test before or
alongside each change. Compare with the reference solution only after the
selected milestone tests pass.

The predecessor Task Manager, REST API, and client examples have been removed.
They are distinct from the current required [`projects/tasks/`](projects/tasks/)
learning project and are not a third capstone. See the
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
   - [`05_text_and_binary_data.py`](lessons/01_basics/05_text_and_binary_data.py) – Unicode text, UTF-8, `bytes`, `bytearray`, and `memoryview`
   - [`06_numeric_types_and_conversions.py`](lessons/01_basics/06_numeric_types_and_conversions.py) – explicit conversions, float precision, `Decimal`, `Fraction`, and `complex`
2. **[Control Flow](lessons/02_control_flow/)**
   - [`01_conditionals.py`](lessons/02_control_flow/01_conditionals.py) – `if` / `elif` / `else`
   - [`02_loops.py`](lessons/02_control_flow/02_loops.py) – `for` and `while` loops
3. **[Functions](lessons/03_functions/)**
   - [`01_functions.py`](lessons/03_functions/01_functions.py) – defining and calling functions, positional-only/keyword-only
     parameters, defaults, argument unpacking, binding, `*args`, `**kwargs`, and return values
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
   - [`03_files_and_exceptions.py`](lessons/05_modules_and_files/03_files_and_exceptions.py) – reading/writing UTF-8 text and raw bytes, plus handling errors
   - [`04_custom_exceptions_and_context_managers.py`](lessons/05_modules_and_files/04_custom_exceptions_and_context_managers.py) – defining custom
     exception classes and writing your own context managers
   - [`05_json_and_structured_data.py`](lessons/05_modules_and_files/05_json_and_structured_data.py) – serializing structured data with JSON
   - [`06_directories_and_paths.py`](lessons/05_modules_and_files/06_directories_and_paths.py) – directory creation/traversal, metadata, deterministic globbing, copy/move, and path boundaries
   - [`07_dates_and_times.py`](lessons/05_modules_and_files/07_dates_and_times.py) – dates, times, durations, aware/naive datetimes, UTC, IANA zones, timestamps, DST, and monotonic clocks
6. **[Object-Oriented Programming](lessons/06_object_oriented_programming/)**
   - [`01_classes_and_objects.py`](lessons/06_object_oriented_programming/01_classes_and_objects.py) – classes, attributes, bound/class/static methods, and properties
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
   - [`06_os_processes_and_streams.py`](lessons/09_tooling_and_debugging/06_os_processes_and_streams.py) – environment validation, standard streams, exit statuses, and safe subprocess execution
   - [`07_packaging_and_public_apis.py`](lessons/09_tooling_and_debugging/07_packaging_and_public_apis.py) – import packages versus distributions, `pyproject.toml`, `src/` layout, editable installs, builds, and public API documentation
10. **[SQL and SQLite](lessons/10_sql_and_sqlite/)**
    - [`01_relational_model_and_sql.py`](lessons/10_sql_and_sqlite/01_relational_model_and_sql.py) – schemas, constraints, parameterized CRUD, filtering, ordering, limits, and row mapping
    - [`02_joins_aggregates_and_indexes.py`](lessons/10_sql_and_sqlite/02_joins_aggregates_and_indexes.py) – related tables, joins, grouped aggregates, indexes, and query plans
    - [`03_transactions_and_sqlite.py`](lessons/10_sql_and_sqlite/03_transactions_and_sqlite.py) – transactions, generated IDs, SQLite affinity, pragmas, and limitations
    - [`04_repository_pattern.py`](lessons/10_sql_and_sqlite/04_repository_pattern.py) – a small injected repository and reusable contract checks
11. **[REST APIs and HTTP Clients](lessons/11_rest_apis_and_clients/)**
    - [`01_http_fundamentals.py`](lessons/11_rest_apis_and_clients/01_http_fundamentals.py) – methods, routes, queries, headers, statuses, bytes, UTF-8, JSON, and finite timeouts
    - [`02_flask_api.py`](lessons/11_rest_apis_and_clients/02_flask_api.py) – an application factory, thin routes, injected dependencies, centralized errors, and Flask's test client
    - [`03_fastapi_api.py`](lessons/11_rest_apis_and_clients/03_fastapi_api.py) – Pydantic boundary models, dependency providers, response models, exception mapping, OpenAPI, and `TestClient`
    - [`04_http_clients.py`](lessons/11_rest_apis_and_clients/04_http_clients.py) – `urllib`, `requests`, and `httpx` transports with finite timeouts and status-first validation
    - **Required applied project:** [Task REST API and clients](projects/tasks/README.md) – implement the shared Task domain, SQLite and Markdown repositories, three server adapters, three client transports, and their contract tests
12. **[Concurrency](lessons/12_concurrency/)**
    - [`01_threading_and_multiprocessing.py`](lessons/12_concurrency/01_threading_and_multiprocessing.py) – threads for blocking I/O, processes for CPU-bound work, shared-state hazards, and cleanup
    - [`02_asyncio_basics.py`](lessons/12_concurrency/02_asyncio_basics.py) – cooperative concurrency, owned tasks, `async`/`await`, and `asyncio.gather`

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

## 🤖 Optional AI learning tutor

This repository includes a Socratic GitHub Copilot CLI tutor that follows course
prerequisites, uses deterministic checks, protects locked solutions, and asks
before editing learner work. See the [AI tutor guide](docs/AI_TUTOR.md) for
setup, start/resume commands, state privacy, and milestone coaching.

## 🧭 Course boundaries

This course aims to make a beginner independently productive with core Python.
Python's ecosystem is much larger than any single introductory course:
specialized work such as web development, data science, machine learning,
desktop interfaces, and cloud deployment requires domain-specific study after
the foundations here. The final section of [`CHEATSHEET.md`](CHEATSHEET.md)
points to authoritative references for continued learning.