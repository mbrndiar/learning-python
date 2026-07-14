# ✨ Module 7: Advanced Python

A few more powerful, distinctly "Pythonic" tools that build on functions
and OOP.

## 🎯 Learning objectives

After this module, you should be able to wrap behavior with decorators,
distinguish iterables, iterators, and generators, evaluate lazy processing, and
write useful modern type annotations.

## 🎁 Decorators

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
The wrapper runs on each later call. Keeping those two moments separate helps
explain why expensive or stateful work in the decorator itself can happen
surprisingly early.

## ♻️ Iteration and lazy evaluation

An iterable can produce an iterator with `iter()`. An iterator returns its next
value from `next()` and raises `StopIteration` when exhausted. Iterators are
stateful and usually single-use. A generator function contains `yield`; calling
it creates a generator without immediately running its body.

Lazy pipelines can process large or unbounded streams with little memory, but
errors may occur later during consumption and exhausted values cannot simply
be replayed. `yield from` delegates to another iterable. Generator `.send()`
and `.throw()` exist, but ordinary iteration covers most application needs.

## 🏷️ Type hints

Annotations document intent and support static analysis; Python does not
enforce them at runtime. Modern Python parameterizes built-in collections and
uses `|` for unions:

```python
def find_name(user_id: int, names: dict[int, str]) -> str | None:
    return names.get(user_id)
```

Older codebases may use `typing.List`, `Optional` and `Union`; understand them
when reading legacy code, but prefer `list[T]` and `T | None` in new Python
3.11+ code. Useful abstractions include `Iterable[T]`, `Sequence[T]`,
`Mapping[K, V]`, `Callable[[A], R]`, `TypeVar`, and `Protocol`. Annotate public
boundaries and non-obvious structures. Static type checkers need their own
configuration and are separate from tests.

For example, Python can execute `add("2", "3")` and return `"23"` even when
`add` is annotated with `int`. A configured
[mypy](https://mypy.readthedocs.io/en/stable/) run reports the inconsistent call
without executing it. A test answers whether a chosen example behaves as
expected; a type checker examines compatible uses across annotated paths.

## 🔌 Protocols and dependency injection

Suppose a reminder service constructs an email client internally. A test must
then prevent a real email while also reaching the service logic. If the sender
is passed in, the same service can use a console sender, an adapter around a
legacy API, or a recording fake in a test. A `Protocol` describes the required
`send()` behavior without forcing those classes to inherit from one base class.

Dependency injection is therefore not mainly about frameworks. It is the small
design decision to receive a collaborator rather than hiding its construction
inside business logic. An adapter translates an incompatible existing API at
the boundary instead of spreading special cases through the core.

## 📚 Concepts covered

- **`01_decorators.py`** - functions that wrap another function (or
  class) to add behavior without modifying its source, built on closures
  and higher-order functions; includes `functools.wraps` and decorator
  factories.
- **`02_generators_and_iterators.py`** - the iterator protocol
  (`__iter__` / `__next__`) and generators, the easiest way to create an
  iterator using `yield` instead of `return`.
- **`03_type_hints.py`** - optional type annotations for variables,
  function arguments and return values using modern built-in generics and
  union syntax; not enforced at runtime, but used by tools like
  [mypy](https://mypy.readthedocs.io/en/stable/).
- **`04_protocols_and_dependency_injection.py`** - structural interfaces with
  `Protocol`, injecting collaborators instead of constructing them inside
  business logic, and adapting one interface to another.

## ▶️ Running

```bash
python lessons/07_advanced_python/01_decorators.py
python lessons/07_advanced_python/02_generators_and_iterators.py
python lessons/07_advanced_python/03_type_hints.py
python lessons/07_advanced_python/04_protocols_and_dependency_injection.py
```

Once you've read through all four files, practice what you learned in
[`exercises/07_advanced_python/`](../../exercises/07_advanced_python/README.md).

## ⚠️ Common mistakes

- Omitting `functools.wraps` from a function wrapper.
- Calling the decorated function while decorating it instead of returning a
  wrapper.
- Trying to consume an exhausted generator a second time.
- Assuming annotations convert or validate values.
- Annotating concrete containers where a broader input protocol is intended.

## ❓ Review questions

1. When is a decorator applied?
2. How do an iterable and an iterator differ?
3. When does a generator function begin executing?
4. What trade-off does lazy evaluation make?
5. What is the difference between type checking and runtime testing?
6. How does a protocol let callers depend on behavior instead of a concrete
   class?
