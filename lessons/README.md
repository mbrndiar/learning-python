# 🎓 Lessons

This is the main course content. Each module combines a self-contained,
textbook-style `README.md` chapter with small runnable `.py` companions. The
chapter teaches the concept and explains its examples; the companions let you
observe the complete mechanism and safely vary one assumption. Modules build on
the ones before them, so work through them in order.

Open a module below and read its chapter first. Run its companion commands from
the repository root, for example:

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
15. [`15_sql_and_sqlite/`](15_sql_and_sqlite/README.md) - connection/cursor
    ownership, relational SQL, SQLite transactions and behavior, and repository
    contract tests
16. [`16_http_fundamentals_and_stdlib/`](16_http_fundamentals_and_stdlib/README.md) -
    the HTTP request/response lifecycle, URL parsing and routing, and a
    standard-library `http.server` adapter
17. [`17_web_apis_with_flask_and_fastapi/`](17_web_apis_with_flask_and_fastapi/README.md) -
    minimal Flask apps and test clients, application factories, centralized
    errors, Pydantic boundary models, and FastAPI dependencies, responses, and
    OpenAPI
18. [`18_http_clients_and_transports/`](18_http_clients_and_transports/README.md) -
    `urllib.request`, status and JSON validation, error shapes, `requests`
    sessions, `httpx` clients, and one shared transport contract
    - Complete the required
      [Task REST API and clients project](../projects/tasks/README.md) before the
      next chapter.
19. [`19_concurrency/`](19_concurrency/README.md) - threads, processes,
    `asyncio`, bounded work, cancellation, and cleanup

## ▶️ How to use a module

1. Read the module `README.md` one numbered concept section at a time.
2. Follow that section's link to its runnable companion and read the docstring
   and `Step` comments.
3. Predict the output, then run the exact command shown in the chapter.
4. Make the bounded experiment suggested by the chapter and explain the
   observed change.
5. Answer the closed-notes review questions and complete the matching exercises
   in
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

Each module `README.md` is independently readable and includes small authentic
fragments, but does not duplicate an entire program. Its `.py` companions
contain the complete runnable demonstrations. Each companion starts with a
module docstring describing its topic, while inline comments explain the reason
for an operation rather than merely repeating the code. Most demonstrations
execute when the file is run. Files containing reusable functions commonly
protect demonstrations with:

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
- After chapter 15, replace file persistence with a constrained SQLite schema
  and parameterized repository operations.
- After chapters 16–18, build and test one small HTTP/JSON boundary with injected
  dependencies and finite client timeouts.
- Complete the required Task project, preserving one domain and contract across
  its persistence, server, and client adapters.
- After chapter 19, explain which concurrency model—if any—fits the program.

These checkpoints are deliberately open-ended. Define expected inputs and
outputs first, split the work into functions, and test important edge cases.
