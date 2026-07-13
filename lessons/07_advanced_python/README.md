# Module 7: Advanced Python

A few more powerful, distinctly "Pythonic" tools that build on functions
and OOP.

## Concepts covered

- **`01_decorators.py`** - functions that wrap another function (or
  class) to add behavior without modifying its source, built on closures
  and higher-order functions; includes `functools.wraps` and decorator
  factories.
- **`02_generators_and_iterators.py`** - the iterator protocol
  (`__iter__` / `__next__`) and generators, the easiest way to create an
  iterator using `yield` instead of `return`.
- **`03_type_hints.py`** - optional type annotations for variables,
  function arguments and return values using the `typing` module (e.g.
  `List`, `Dict`, `Optional`, `Union`); not enforced at runtime, but used
  by tools like `mypy` and IDEs.

## Running

```bash
python lessons/07_advanced_python/01_decorators.py
python lessons/07_advanced_python/02_generators_and_iterators.py
python lessons/07_advanced_python/03_type_hints.py
```

Once you've read through all three files, practice what you learned in
[`exercises/07_advanced_python/`](../../exercises/07_advanced_python/README.md).
