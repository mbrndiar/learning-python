# 🎓 Lessons

This is the main course content: small, self-contained, runnable scripts that
teach Python from the ground up. Each module builds on the ones before it, so
work through them in order.

Run any lesson file from the repository root, for example:

```bash
python lessons/01_basics/01_hello_world.py
```

## 🗂️ Modules

1. [`01_basics/`](01_basics/README.md) - printing, variables, types,
   operators and strings
2. [`02_control_flow/`](02_control_flow/README.md) - conditionals and loops
3. [`03_functions/`](03_functions/README.md) - functions, lambdas, closures
   and recursion
4. [`04_data_structures/`](04_data_structures/README.md) - lists, tuples,
   dictionaries, sets, comprehensions and `collections`
5. [`05_modules_and_files/`](05_modules_and_files/README.md) - modules,
   file I/O, JSON, exceptions, custom exceptions and context managers
6. [`06_object_oriented_programming/`](06_object_oriented_programming/README.md) -
   classes, inheritance, encapsulation, abstract classes and dataclasses
7. [`07_advanced_python/`](07_advanced_python/README.md) - decorators,
   generators/iterators, type hints, protocols and dependency injection
8. [`08_testing/`](08_testing/README.md) - testing with `unittest`
9. [`09_tooling_and_debugging/`](09_tooling_and_debugging/README.md) -
   virtual environments, debugging, CLI arguments, logging and quality tools
10. [`10_sql_and_sqlite/`](10_sql_and_sqlite/README.md) - relational modeling,
   portable SQL fundamentals, SQLite behavior, and repository boundaries
11. [`11_rest_apis_and_clients/`](11_rest_apis_and_clients/README.md) - HTTP,
    REST boundaries, Flask, FastAPI, `urllib`, `requests`, and `httpx`

> **Temporary course-order compatibility:** Continue next to
> [`11_concurrency/`](11_concurrency/README.md). Its directory and internal
> heading remain Module 11 until the separately planned renumbering, so this
> learner-facing index does not assign concurrency a duplicate module number.

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

This distinction becomes important when modules are imported in module 5.

## 🚩 Checkpoints

- After modules 1–2, write a number-guessing or menu-driven program.
- After modules 3–4, build a text analyzer using functions and collections.
- After modules 5–6, model and persist a small collection of objects.
- After modules 7–9, add annotations, tests, logging, and a CLI.
- After module 10, replace file persistence with a constrained SQLite schema
  and parameterized repository operations.
- After module 11, build and test one small HTTP/JSON boundary with injected
  dependencies and finite client timeouts.
- After the following concurrency material, explain which concurrency model—if
  any—fits the program.

These checkpoints are deliberately open-ended. Define expected inputs and
outputs first, split the work into functions, and test important edge cases.
