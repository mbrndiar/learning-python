# 🎓 Lessons

This is the main course content: small, self-contained, runnable scripts that
teach Python from the ground up. Each module builds on the ones before it, so
work through them in order.

Run any lesson file from the repository root, for example:

```bash
python lessons/01_python_fundamentals/01_running_python.py
```

## 🗂️ Modules

1. [`01_python_fundamentals/`](01_python_fundamentals/README.md) - running
   scripts, comments, names and assignment, core scalar types, print,
   comparisons, and truthiness
2. [`02_text_and_numbers/`](02_text_and_numbers/README.md) - operators,
   string operations, slicing, formatting, Unicode text, bytes, and numeric
   representations
3. [`03_collections/`](03_collections/README.md) - lists, tuples,
   dictionaries, sets, membership, aliasing, mutation, and copying
4. [`04_control_flow/`](04_control_flow/README.md) -
   conditionals in depth, `for`/`while` loops, `range`, `enumerate`, `zip`,
   `break`/`continue`, accumulators, and comprehensions
5. [`05_functions/`](05_functions/README.md) -
   function definitions, parameters, return values, scope, closures,
   higher-order functions, lambdas, and recursion
6. [`06_modules_and_packages/`](06_modules_and_packages/README.md) - module
   objects, the import cache, package layout, `__init__.py`, absolute/relative
   imports, `python -m`, and public APIs
7. [`07_exceptions_files_and_paths/`](07_exceptions_files_and_paths/README.md) -
   exception flow, narrow `except`, `else`/`finally`/`raise`/chaining, `Path`,
   text/binary files, and context managers
8. [`08_structured_data_and_time/`](08_structured_data_and_time/README.md) -
   JSON boundaries, validation, naive/aware datetimes, UTC, and injected clocks
9. [`09_object_oriented_programming/`](09_object_oriented_programming/README.md) -
   classes, composition and inheritance, properties and encapsulation, the
   Python data model, ABCs, dataclasses, enums, and domain errors
10. [`10_iteration_decorators_and_contexts/`](10_iteration_decorators_and_contexts/README.md) -
    iterables/iterators, generators, decorators and wrappers, decorator
    factories, and `@contextmanager`
11. [`11_typing_protocols_and_di/`](11_typing_protocols_and_di/README.md) -
    annotations and narrowing, generic collections/callables, `Literal`,
    `Annotated`, `Self`, and `Protocol`-based dependency injection
12. [`12_testing/`](12_testing/README.md) - automated testing with `unittest`,
    pytest, fixtures, parameterization, and test doubles
13. [`13_debugging_and_cli/`](13_debugging_and_cli/README.md) - tracebacks,
    `pdb`, `argparse` boundaries, custom validators, subcommands, and logging
14. [`14_environments_processes_and_packaging/`](14_environments_processes_and_packaging/README.md) -
    virtual environments, streams and exit status, subprocess ownership,
    quality gates and CI, and packaging distributions
15. [`10_sql_and_sqlite/`](10_sql_and_sqlite/README.md) - relational modeling,
    portable SQL fundamentals, SQLite behavior, and repository boundaries
16. [`11_rest_apis_and_clients/`](11_rest_apis_and_clients/README.md) - HTTP,
    REST boundaries, Flask, FastAPI, `urllib`, `requests`, and `httpx`
    - Complete the required
      [Task REST API and clients project](../projects/tasks/README.md) before the
      next module.
17. [`12_concurrency/`](12_concurrency/README.md) - threads, processes,
    `asyncio`, bounded work, cancellation, and cleanup

Modules 15 through 17 keep their existing `10_`-`12_` directory prefixes from
before this migration; the numbered list above reflects each module's
authoritative teaching order, not its directory name.

## ▶️ How to use a module

1. Open the lesson file(s) in order and read the docstrings and comments.
2. Run the file to see the output.
3. Tweak the code and re-run it to check your understanding.
4. Complete the matching exercises in
   [`exercises/`](../exercises/README.md) before moving to the next module.

## 🔁 Recommended study loop

Use active recall instead of only reading:

1. **Preview:** read the objectives and identify unfamiliar terms.
2. **Predict:** before running each example, write down its expected output.
3. **Experiment:** change one thing at a time and explain the result.
4. **Practice:** solve the exercises without copying the lesson.
5. **Review:** answer the questions at the end of the module aloud or in
   writing.
6. **Reflect:** note one concept you can use and one you need to revisit.

Code that seems obvious while visible can still be difficult to reproduce.
Close the lesson and rebuild a small example from memory before moving on.

## 🧱 How the examples are structured

Each `.py` file starts with a module docstring describing its topic. Inline
comments explain the reason for an operation rather than merely repeating the
code. Most demonstrations execute when the file is run. Files containing
reusable functions commonly protect demonstrations with:

```python
if __name__ == "__main__":
    # Runs only when this file is executed directly.
    ...
```

This distinction becomes important when modules are imported in module 6.

## 🚩 Checkpoints

- After modules 1–4, write a number-guessing or menu-driven program.
- After module 5, build a text analyzer using functions and collections.
- After modules 6–7, model and persist a small collection of objects.
- After modules 8–10, add annotations, tests, logging, and a CLI.
- After module 11, replace file persistence with a constrained SQLite schema
  and parameterized repository operations.
- After module 12, build and test one small HTTP/JSON boundary with injected
  dependencies and finite client timeouts.
- Complete the required Task project, preserving one domain and contract across
  its persistence, server, and client adapters.
- After module 13, explain which concurrency model—if any—fits the program.

These checkpoints are deliberately open-ended. Define expected inputs and
outputs first, split the work into functions, and test important edge cases.
