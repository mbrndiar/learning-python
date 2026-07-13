# Module 7: Advanced Python

A few more powerful, distinctly "Pythonic" tools that build on functions
and OOP.

## Learning objectives

After this module, you should be able to wrap behavior with decorators,
distinguish iterables, iterators, and generators, evaluate lazy processing, and
write useful modern type annotations.

## Decorators

A decorator receives a callable and returns a callable. `@decorator` syntax
rebinds the function name to the decorator's result:

```python
@logged
def greet(name):
    return f"Hello, {name}"

# Equivalent to: greet = logged(greet)
```

A wrapper generally accepts `*args, **kwargs` and uses `functools.wraps` to
preserve metadata such as the original name and docstring. A decorator factory
adds another function layer to accept configuration. Decoration normally
happens when the containing module is imported, not on each function call.

## Iteration and lazy evaluation

An iterable can produce an iterator with `iter()`. An iterator returns its next
value from `next()` and raises `StopIteration` when exhausted. Iterators are
stateful and usually single-use. A generator function contains `yield`; calling
it creates a generator without immediately running its body.

Lazy pipelines can process large or unbounded streams with little memory, but
errors may occur later during consumption and exhausted values cannot simply
be replayed. `yield from` delegates to another iterable. Generator `.send()`
and `.throw()` exist, but ordinary iteration covers most application needs.

## Type hints

Annotations document intent and support static analysis; Python does not
enforce them at runtime. On Python 3.9+, built-in collections can be
parameterized:

```python
def find_name(user_id: int, names: dict[int, str]) -> str | None:
    return names.get(user_id)
```

The `|` union syntax requires Python 3.10, so this course's Python 3.9-compatible
scripts use `Optional[str]` and `Union[...]`. Useful abstractions include
`Iterable[T]`, `Sequence[T]`, `Mapping[K, V]`, `Callable[[A], R]`, and
`TypeVar`. Annotate public boundaries and non-obvious structures; do not add
annotations that merely repeat obvious local values. Static type checkers need
their own configuration and are separate from tests.

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

## Common mistakes

- Omitting `functools.wraps` from a function wrapper.
- Calling the decorated function while decorating it instead of returning a
  wrapper.
- Trying to consume an exhausted generator a second time.
- Assuming annotations convert or validate values.
- Annotating concrete containers where a broader input protocol is intended.

## Review questions

1. When is a decorator applied?
2. How do an iterable and an iterator differ?
3. When does a generator function begin executing?
4. What trade-off does lazy evaluation make?
5. What is the difference between type checking and runtime testing?
