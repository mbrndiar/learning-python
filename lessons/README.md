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
6. [`05_modules_and_files/`](05_modules_and_files/README.md) - modules,
   packages, files and directories, date/time, JSON, exceptions, and context
   managers
7. [`06_object_oriented_programming/`](06_object_oriented_programming/README.md) -
   classes, method kinds, inheritance, encapsulation, abstract classes, and
   dataclasses
8. [`07_advanced_python/`](07_advanced_python/README.md) - decorators,
   generators/iterators, type hints, protocols and dependency injection
9. [`08_testing/`](08_testing/README.md) - testing with `unittest`
10. [`09_tooling_and_debugging/`](09_tooling_and_debugging/README.md) -
    environments, debugging, CLI and process boundaries, packaging,
    documentation, logging, and quality tools
11. [`10_sql_and_sqlite/`](10_sql_and_sqlite/README.md) - relational modeling,
    portable SQL fundamentals, SQLite behavior, and repository boundaries
12. [`11_rest_apis_and_clients/`](11_rest_apis_and_clients/README.md) - HTTP,
    REST boundaries, Flask, FastAPI, `urllib`, `requests`, and `httpx`
    - Complete the required
      [Task REST API and clients project](../projects/tasks/README.md) before the
      next module.
13. [`12_concurrency/`](12_concurrency/README.md) - threads, processes,
    `asyncio`, bounded work, cancellation, and cleanup

Modules 6 through 13 keep their existing `05_`-`12_` directory prefixes from
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
