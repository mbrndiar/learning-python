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
- The core lesson scripts in Chapters 1–15, Chapter 16, Chapter 18's `urllib`
  lessons, Chapter 19, and both capstones use only the standard library. Chapter
  12's pytest lesson, Chapter 14's quality-tool and packaging labs, Chapter 17's
  Flask, FastAPI, and Pydantic APIs, Chapter 18's `requests` and `httpx` clients,
  and the Task project use development or runtime dependencies from this
  repository.
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
python lessons/01_python_fundamentals/01_running_python.py
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

Module 14 explains what each tool checks, how to measure coverage, and how these
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
check your work. After Chapter 18, complete the required
[Task REST API and clients project](projects/tasks/README.md) before moving to
Chapter 19.

## 🏆 Capstone projects

Once you've completed all 19 modules and the required applied project, build both
equally required
[capstone projects](capstones/README.md):

- the [comparative SQLite key/value store](capstones/comparative/README.md);
- the [idiomatic ingestion and reporting pipeline](capstones/idiomatic/README.md).

Use each guided starter one milestone at a time, writing a test before or
alongside each change. Compare with the reference solution only after the
selected milestone tests pass.

The predecessor Task Manager, REST API, and client examples have been removed.
They are distinct from the current required [`projects/tasks/`](projects/tasks/)
learning project and are not a third capstone.

## 🗒️ Cheat sheet

[`CHEATSHEET.md`](CHEATSHEET.md) is a one-page glossary and syntax quick
reference to jog your memory after finishing the course.

<a id="course-outline"></a>

## 🗺️ Course outline

1. **[Python Fundamentals](lessons/01_python_fundamentals/)**
   - [`01_running_python.py`](lessons/01_python_fundamentals/01_running_python.py) – running scripts, comments, and `print`
   - [`02_values_names_and_types.py`](lessons/01_python_fundamentals/02_values_names_and_types.py) – names, assignment, and core scalar types (`str`, `int`, `float`, `bool`, `None`)
   - [`03_conversion_and_truthiness.py`](lessons/01_python_fundamentals/03_conversion_and_truthiness.py) – explicit conversion, comparisons, and truthiness
2. **[Text and Numbers](lessons/02_text_and_numbers/)**
   - [`01_operators_and_expressions.py`](lessons/02_text_and_numbers/01_operators_and_expressions.py) – arithmetic, comparison, and logical operators
   - [`02_strings_and_formatting.py`](lessons/02_text_and_numbers/02_strings_and_formatting.py) – string operations, slicing, and f-string formatting
   - [`03_unicode_text_and_bytes.py`](lessons/02_text_and_numbers/03_unicode_text_and_bytes.py) – Unicode text, UTF-8, `bytes`, and `bytearray`
   - [`04_numeric_representations.py`](lessons/02_text_and_numbers/04_numeric_representations.py) – rounding, explicit conversions, `Decimal`, and `Fraction`
3. **[Collections](lessons/03_collections/)**
   - [`01_lists_and_tuples.py`](lessons/03_collections/01_lists_and_tuples.py) – creating, indexing, slicing, and mutating lists and tuples
   - [`02_dictionaries_and_sets.py`](lessons/03_collections/02_dictionaries_and_sets.py) – dict/set construction, lookup, update, and membership
   - [`03_references_mutation_and_copying.py`](lessons/03_collections/03_references_mutation_and_copying.py) – aliasing, in-place mutation, and shallow copying
4. **[Flow and Iteration](lessons/04_control_flow/)**
   - [`01_conditions_and_truthiness.py`](lessons/04_control_flow/01_conditions_and_truthiness.py) – `if`/`elif`/`else` in depth and truthiness
   - [`02_loops_and_iteration_control.py`](lessons/04_control_flow/02_loops_and_iteration_control.py) – `for`/`while`, `range`, `enumerate`, `zip`, `break`, `continue`, and loop `else`
   - [`03_accumulators_and_specialized_collections.py`](lessons/04_control_flow/03_accumulators_and_specialized_collections.py) – accumulator patterns, then `Counter` and `defaultdict`
   - [`04_comprehensions.py`](lessons/04_control_flow/04_comprehensions.py) – list/set/dict comprehensions derived from equivalent loops
5. **[Function Contracts and Scope](lessons/05_functions/)**
   - [`01_function_contracts.py`](lessons/05_functions/01_function_contracts.py) – defining and calling functions, return values, and basic type hints
   - [`02_parameter_kinds_and_unpacking.py`](lessons/05_functions/02_parameter_kinds_and_unpacking.py) – defaults, positional-only/keyword-only
     parameters, `*args`, `**kwargs`, and call-site unpacking
   - [`03_scope_closures_and_higher_order.py`](lessons/05_functions/03_scope_closures_and_higher_order.py) – LEGB scope, closures
     (including `nonlocal`), functions as values, and lambdas
   - [`04_recursion.py`](lessons/05_functions/04_recursion.py) – base cases, stack frames, and when iteration is clearer
6. **[Modules and Packages](lessons/06_modules_and_packages/)**
   - [`01_modules_and_imports.py`](lessons/06_modules_and_packages/01_modules_and_imports.py) – module objects, the import cache, import forms, and namespacing
   - [`02_packages_and_resolution.py`](lessons/06_modules_and_packages/02_packages_and_resolution.py) – package layout, `__init__.py`, absolute/relative imports, and `python -m`
   - [`03_scripts_modules_and_public_apis.py`](lessons/06_modules_and_packages/03_scripts_modules_and_public_apis.py) – `__name__`, import-time side effects, guarded entry points, re-exports, and `__all__`
7. **[Exceptions, Files, and Paths](lessons/07_exceptions_files_and_paths/)**
   - [`01_exception_flow.py`](lessons/07_exceptions_files_and_paths/01_exception_flow.py) – traceback propagation, narrow `except`, `else`, `finally`, `raise`, and chaining
   - [`02_paths_and_directories.py`](lessons/07_exceptions_files_and_paths/02_paths_and_directories.py) – `Path`, relative/absolute paths, iteration, metadata, and temporary directories
   - [`03_text_and_binary_files.py`](lessons/07_exceptions_files_and_paths/03_text_and_binary_files.py) – `open`, modes, encodings, newline behavior, bytes, and explicit ownership
   - [`04_context_managers_and_resource_lifetimes.py`](lessons/07_exceptions_files_and_paths/04_context_managers_and_resource_lifetimes.py) – `with`, `__enter__`/`__exit__`, `closing`, and `memoryview` lifetime
8. **[Structured Data and Time](lessons/08_structured_data_and_time/)**
   - [`01_json_boundaries.py`](lessons/08_structured_data_and_time/01_json_boundaries.py) – JSON vs. Python values, `dump`/`load`/`dumps`/`loads`, validation, and malformed input
   - [`02_datetimes_timezones_and_clocks.py`](lessons/08_structured_data_and_time/02_datetimes_timezones_and_clocks.py) – naive/aware datetimes, UTC, parsing/formatting, elapsed clocks, and injected clocks
9. **[Objects and Data Models](lessons/09_object_oriented_programming/)**
   - [`01_classes_objects_and_methods.py`](lessons/09_object_oriented_programming/01_classes_objects_and_methods.py) – classes, attributes, bound/class/static methods, and properties
   - [`02_composition_and_inheritance.py`](lessons/09_object_oriented_programming/02_composition_and_inheritance.py) – composition versus inheritance, and a coherent multi-level hierarchy
   - [`03_properties_and_encapsulation.py`](lessons/09_object_oriented_programming/03_properties_and_encapsulation.py) – properties, name-mangling, and encapsulated invariants
   - [`04_python_data_model.py`](lessons/09_object_oriented_programming/04_python_data_model.py) – dunder methods (`__repr__`, `__eq__`, `__add__`, `__iter__`, etc.)
   - [`05_abcs_dataclasses_enums_and_domain_errors.py`](lessons/09_object_oriented_programming/05_abcs_dataclasses_enums_and_domain_errors.py) – abstract base classes, `@dataclass`, `enum.Enum`, and a custom exception after inheritance
10. **[Iteration, Decorators, and Contexts](lessons/10_iteration_decorators_and_contexts/)**
    - [`01_iterables_iterators_and_stopiteration.py`](lessons/10_iteration_decorators_and_contexts/01_iterables_iterators_and_stopiteration.py) – the iterable/iterator protocol and `StopIteration`
    - [`02_generators_and_lazy_evaluation.py`](lessons/10_iteration_decorators_and_contexts/02_generators_and_lazy_evaluation.py) – `yield`, laziness, and generator expressions
    - [`03_decorators_and_wrappers.py`](lessons/10_iteration_decorators_and_contexts/03_decorators_and_wrappers.py) – decorators, wrapper state, and `functools.wraps`
    - [`04_decorator_factories_and_contextmanager.py`](lessons/10_iteration_decorators_and_contexts/04_decorator_factories_and_contextmanager.py) – decorator factories and generator-based context managers via `@contextmanager`
11. **[Typing, Protocols, and Dependency Injection](lessons/11_typing_protocols_and_di/)**
    - [`01_annotations_and_narrowing.py`](lessons/11_typing_protocols_and_di/01_annotations_and_narrowing.py) – runtime versus static annotations, unions, `None`, narrowing, and aliases
    - [`02_collections_callables_and_generics.py`](lessons/11_typing_protocols_and_di/02_collections_callables_and_generics.py) – `Iterable`, `Sequence`, `Mapping`, `Callable`, and generic functions with `TypeVar`
    - [`03_literal_annotated_and_self.py`](lessons/11_typing_protocols_and_di/03_literal_annotated_and_self.py) – `Literal`, `Annotated`, and `Self`
    - [`04_protocols_adapters_and_dependency_injection.py`](lessons/11_typing_protocols_and_di/04_protocols_adapters_and_dependency_injection.py) – structural interfaces (`Protocol`), interchangeable implementations, and dependency injection
12. **[Automated Testing](lessons/12_testing/)**
    - [`01_testing_mental_model.py`](lessons/12_testing/01_testing_mental_model.py) – observable behavior, arrange-act-assert, and determinism
    - [`02_unittest_lifecycle_and_assertions.py`](lessons/12_testing/02_unittest_lifecycle_and_assertions.py) – `TestCase`, the `setUp`/`tearDown` lifecycle, precise assertions, and `subTest`
    - [`03_pytest_assertions_parameterization_and_fixtures.py`](lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py) – plain `assert`, `pytest.raises`, `@pytest.mark.parametrize`, and fixtures such as `tmp_path`
    - [`04_test_doubles_and_mocking.py`](lessons/12_testing/04_test_doubles_and_mocking.py) – fakes, stubs, mocks, `Mock(spec=...)`, and `patch`
13. **[Debugging and Command-Line Interfaces](lessons/13_debugging_and_cli/)**
    - [`01_tracebacks_and_pdb.py`](lessons/13_debugging_and_cli/01_tracebacks_and_pdb.py) – reading tracebacks, common errors, and the interactive debugger
    - [`02_argparse_basics.py`](lessons/13_debugging_and_cli/02_argparse_basics.py) – parsing CLI arguments with `argparse` at a thin boundary
    - [`03_subcommands_and_custom_validation.py`](lessons/13_debugging_and_cli/03_subcommands_and_custom_validation.py) – custom `type=` validators and `add_subparsers`
    - [`04_logging_and_diagnostics.py`](lessons/13_debugging_and_cli/04_logging_and_diagnostics.py) – the `logging` module, severity levels, and choosing among `print()`, `pdb`, and `logging`
14. **[Environments, Processes, and Packaging](lessons/14_environments_processes_and_packaging/)**
    - [`01_virtual_environments_and_pip.py`](lessons/14_environments_processes_and_packaging/01_virtual_environments_and_pip.py) – virtual environments, `pip`, and why to use them
    - [`02_environment_streams_and_exit_status.py`](lessons/14_environments_processes_and_packaging/02_environment_streams_and_exit_status.py) – environment configuration, standard streams, and exit status
    - [`03_subprocess_ownership.py`](lessons/14_environments_processes_and_packaging/03_subprocess_ownership.py) – argument lists, allowlisted environments, timeouts, and the subprocess error taxonomy
    - [`04_format_lint_type_test_coverage_ci.py`](lessons/14_environments_processes_and_packaging/04_format_lint_type_test_coverage_ci.py) – [Ruff](https://docs.astral.sh/ruff/), [mypy](https://mypy.readthedocs.io/en/stable/), [pytest](https://docs.pytest.org/en/stable/), [Coverage.py](https://coverage.readthedocs.io/en/stable/), and CI
    - [`05_distributions_builds_and_public_apis.py`](lessons/14_environments_processes_and_packaging/05_distributions_builds_and_public_apis.py) – import packages versus distributions, `pyproject.toml`, `src/` layout, editable installs, builds, and public API documentation
15. **[SQL and SQLite](lessons/15_sql_and_sqlite/)**
    - [`01_sqlite_connection_cursor_and_rows.py`](lessons/15_sql_and_sqlite/01_sqlite_connection_cursor_and_rows.py) – connection ownership, cursor results, batch execution, fetching, row factories, and row mapping
    - [`02_relational_schema_and_crud.py`](lessons/15_sql_and_sqlite/02_relational_schema_and_crud.py) – relational constraints, value parameters, deterministic CRUD, and missing update/delete paths
    - [`03_joins_aggregates_indexes_and_plans.py`](lessons/15_sql_and_sqlite/03_joins_aggregates_indexes_and_plans.py) – inner/left joins, parameterized aggregates, indexes, and version-sensitive query plans
    - [`04_transactions_and_sqlite_behavior.py`](lessons/15_sql_and_sqlite/04_transactions_and_sqlite_behavior.py) – explicit and context-managed transactions, affinity, generated IDs, and concurrency boundaries
    - [`05_repository_and_contract_tests.py`](lessons/15_sql_and_sqlite/05_repository_and_contract_tests.py) – one protocol and behavior contract shared by in-memory and SQLite adapters
16. **[HTTP Fundamentals and the Standard Library](lessons/16_http_fundamentals_and_stdlib/)**
    - [`01_http_request_response_lifecycle.py`](lessons/16_http_fundamentals_and_stdlib/01_http_request_response_lifecycle.py) – methods, request targets, headers, body bytes, statuses, UTF-8, JSON, and Content-Length
    - [`02_urls_queries_and_routing.py`](lessons/16_http_fundamentals_and_stdlib/02_urls_queries_and_routing.py) – URL components, query parsing, and routing by method and path with deliberate 400/404/405 responses
    - [`03_stdlib_http_server.py`](lessons/16_http_fundamentals_and_stdlib/03_stdlib_http_server.py) – a `BaseHTTPRequestHandler` adapter over a pure boundary with explicit server ownership
17. **[Web APIs with Flask and FastAPI](lessons/17_web_apis_with_flask_and_fastapi/)**
    - [`01_flask_minimal_app_and_test_client.py`](lessons/17_web_apis_with_flask_and_fastapi/01_flask_minimal_app_and_test_client.py) – a minimal Flask app, the `request` proxy, and testing without a live server
    - [`02_flask_factory_errors_and_dependencies.py`](lessons/17_web_apis_with_flask_and_fastapi/02_flask_factory_errors_and_dependencies.py) – application factories, injected dependencies, and centralized error handlers
    - [`03_pydantic_boundary_models.py`](lessons/17_web_apis_with_flask_and_fastapi/03_pydantic_boundary_models.py) – strict Pydantic models with `ConfigDict`, `Field`, `Annotated`, `Literal`, and `model_dump()`
    - [`04_fastapi_dependencies_responses_and_openapi.py`](lessons/17_web_apis_with_flask_and_fastapi/04_fastapi_dependencies_responses_and_openapi.py) – synchronous `Depends`, `app.state`, `response_model`, exception overrides, `TestClient`, and generated OpenAPI
18. **[HTTP Clients and Transports](lessons/18_http_clients_and_transports/)**
    - [`01_urls_queries_and_urllib_request.py`](lessons/18_http_clients_and_transports/01_urls_queries_and_urllib_request.py) – build URLs, encode queries, and construct a `urllib.request.Request` with a finite timeout
    - [`02_status_content_type_and_json_validation.py`](lessons/18_http_clients_and_transports/02_status_content_type_and_json_validation.py) – branch on status first, read content type case-insensitively, and validate decoded JSON strictly
    - [`03_urllib_responses_and_errors.py`](lessons/18_http_clients_and_transports/03_urllib_responses_and_errors.py) – `HTTPError` as a response versus `URLError` as no response, distinguishing timeouts
    - [`04_requests_sessions.py`](lessons/18_http_clients_and_transports/04_requests_sessions.py) – owned `requests.Session`, `params`/`json` helpers, raw bytes, and exception families
    - [`05_httpx_clients.py`](lessons/18_http_clients_and_transports/05_httpx_clients.py) – owned `httpx.Client`, explicit timeouts, and its exception families
    - [`06_transport_contract_and_client_policy.py`](lessons/18_http_clients_and_transports/06_transport_contract_and_client_policy.py) – one small transport `Protocol` and a client policy that validates timeouts and performs one attempt per call
    - **Required applied project:** [Task REST API and clients](projects/tasks/README.md) – implement the shared Task domain, SQLite and Markdown repositories, three server adapters, three client transports, and their contract tests
19. **[Concurrency](lessons/12_concurrency/)**
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
for the exception or concept before consulting another source. Module 13 gives a
systematic debugging process.

Solutions are examples, not the only correct answers. Compare behavior,
readability, handling of edge cases, and tests rather than requiring identical
code.

## 🤖 Optional AI Learning Mentor

This repository includes an AI Learning Mentor for GitHub Copilot CLI, OpenAI
Codex, and Claude Code. It follows course prerequisites, uses deterministic
checks, protects locked solutions, and asks before editing learner work. See the
[AI Learning Mentor guide](docs/AI_TUTOR.md) for setup, start/resume commands,
state privacy, and milestone coaching.

## 🧭 Course boundaries

This course aims to make a beginner independently productive with core Python.
Python's ecosystem is much larger than any single introductory course:
specialized work such as web development, data science, machine learning,
desktop interfaces, and cloud deployment requires domain-specific study after
the foundations here. The final section of [`CHEATSHEET.md`](CHEATSHEET.md)
points to authoritative references for continued learning.