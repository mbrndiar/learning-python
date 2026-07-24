# 🔁 Chapter 10: Iteration, Decorators, and Contexts

**Semantic ID:** `module.iteration-decorators-and-contexts` · **Prerequisites:**
`module.objects-and-data-models`

## 📍 Where this fits

Chapter 9's `Playlist` implemented `__iter__` to work with `for` loops,
and Chapter 7's `ManagedFile` implemented `__enter__`/`__exit__` to work
with `with`. This chapter generalizes both: how an iterator actually
produces values one at a time (and how `yield` builds one for you
automatically), and how a decorator wraps a function's behavior without
touching its source -- including the decorator-based way to write a
context manager, using the same generator mechanism as `yield`-based
iteration.

## 🎯 Learning objectives

After this chapter, you should be able to:

- distinguish an iterable from an iterator, and explain what `iter()`
  and `next()` each do;
- implement the iterator protocol (`__iter__`/`__next__`) directly, and
  explain `StopIteration` as its ordinary completion signal;
- write a generator function with `yield`, and explain why calling it
  does not run its body immediately;
- explain generator laziness and single-use exhaustion, and write a
  generator expression;
- write a decorator that wraps a function's behavior, and use
  `functools.wraps` to preserve the original function's name and
  docstring;
- write a decorator factory -- a function that returns a decorator so
  the decorator itself can accept arguments;
- write a generator-based context manager with
  `contextlib.contextmanager`, and explain the correspondence between
  code before/after `yield` and `__enter__`/`__exit__`.

## 🧠 Motivation and mental model

A `for` loop, a decorated function call, and a `with` block all look like
special syntax, but each one is built from an ordinary mechanism you can
implement yourself: a `for` loop is just repeated calls to `next()` until
`StopIteration`; a decorator is just a function that returns a different
function; and `@contextmanager` is just a generator function whose single
`yield` splits its body into a "before" half and an "after" half that
always runs, success or failure. Seeing the mechanism underneath the
syntax means none of these ever needs to be memorized as a special case
-- each is a direct, traceable consequence of things Chapters 1-9 already
taught (functions as values, classes, `try`/`finally`).

## 1️⃣ Iterables, iterators, and `StopIteration`

`iter(obj)` asks an iterable for an iterator; `next(iterator)` asks that
iterator for its next value, raising `StopIteration` when there is none:

```python
numbers = [10, 20, 30]
iterator_a = iter(numbers)
iterator_b = iter(numbers)
print(next(iterator_a))
print(next(iterator_a))
print(next(iterator_b))
```

```text
10
20
10
```

A list is *iterable* (`iter()` works on it) but is not itself an
*iterator* -- `iterator_a` and `iterator_b` advance independently even
though both came from the same `numbers` list, because `iter()` on a
list always creates a fresh iterator object that tracks its own
position.

### `StopIteration` is the ordinary completion signal

```python
final_iterator = iter([1, 2])
next(final_iterator)
next(final_iterator)
try:
    next(final_iterator)
except StopIteration:
    print("StopIteration raised once the iterator is exhausted")
```

```text
StopIteration raised once the iterator is exhausted
```

A `for` loop calls `next()` repeatedly and catches `StopIteration`
internally -- that is the entire mechanism a `for` loop uses under the
hood.

### Implementing the iterator protocol directly

```python
class CountUp:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop

    def __iter__(self):
        return self  # this object is its own iterator

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


for value in CountUp(1, 4):
    print(value)

empty = CountUp(4, 4)
try:
    next(iter(empty))
except StopIteration:
    print("empty CountUp raises StopIteration immediately")
```

```text
1
2
3
empty CountUp raises StopIteration immediately
```

`__iter__` (returning `self`) and `__next__` (raising `StopIteration` at
the end) let `CountUp` work with `for`, `next()`, and every other
iteration tool, exactly like the list iterator above -- but with custom
logic controlling what "next" means. An empty range (`CountUp(4, 4)`)
raises `StopIteration` on the very first `next()` call, since
`self.current >= self.stop` is already true.

Run the complete companion:

```bash
python lessons/10_iteration_decorators_and_contexts/01_iterables_iterators_and_stopiteration.py
```

See
[`01_iterables_iterators_and_stopiteration.py`](01_iterables_iterators_and_stopiteration.py)
for the full sequence, including manual `next()` calls on a `CountUp`
instance.

> **Try one change:** change `CountUp(1, 4)` in the `for` loop to
> `CountUp(4, 4)` (an empty range) and predict what the loop prints. The
> `__next__` method's first comparison (`self.current >= self.stop`) is
> what decides this -- no change to the `for` loop itself is needed.

## 2️⃣ Generators and lazy evaluation

`yield` is the easiest way to build an iterator, without hand-writing
`__iter__`/`__next__`: a function containing `yield` returns a generator
object immediately when called, and its body runs only as values are
requested.

```python
def countdown(start):
    while start > 0:
        yield start
        start -= 1
    yield "Liftoff!"


countdown_gen = countdown(3)
print(type(countdown_gen))
for value in countdown_gen:
    print(value)
```

```text
<class 'generator'>
3
2
1
Liftoff!
```

Calling `countdown(3)` does not execute anything yet -- `type(countdown_gen)`
is `<class 'generator'>`, not a list, confirming the body has not run.
Execution pauses at each `yield` and resumes right after it the next
time a value is requested, exactly like `CountUp` kept `self.current`
between calls in concept 1, but here Python manages that suspended state
automatically.

### Laziness and one-shot exhaustion

```python
def fibonacci_up_to(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


fib_gen = fibonacci_up_to(30)
print(list(fib_gen))
print(list(fib_gen))
```

```text
[0, 1, 1, 2, 3, 5, 8, 13, 21]
[]
```

Calling `fibonacci_up_to(30)` does no computation -- only iterating it
(here, via `list()`) pulls values out one at a time. A generator can be
iterated through exactly once: re-consuming the already-exhausted
`fib_gen` prints `[]`, not the same sequence again. A fresh call, such
as `fibonacci_up_to(30)` a second time, still works.

A generator expression `(... for ... in ...)` is the lazy counterpart of
a list comprehension -- same syntax, wrapped in `()` instead of `[]`.

Run the complete companion:

```bash
python lessons/10_iteration_decorators_and_contexts/02_generators_and_lazy_evaluation.py
```

See
[`02_generators_and_lazy_evaluation.py`](02_generators_and_lazy_evaluation.py)
for the full sequence, including a generator expression over `range(5)`.

> **Try one change:** change `while a < limit` to `while a <= limit` in
> `fibonacci_up_to` and predict whether `fibonacci_up_to(21)` then
> includes `21` in its output. Laziness is a property of *how* values
> are produced, independent of what condition decides when to stop.

## 3️⃣ Decorators and wrappers

A decorator is a function that wraps another function to add behavior
without changing its source. `@decorator` above a `def` is equivalent to
`func = decorator(func)`, run once when the `def` executes.

```python
import functools


def uppercase(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()

    return wrapper


@uppercase
def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"


print(greet("Ada"))
print(greet.__name__)
```

```text
HELLO, ADA!
greet
```

`@uppercase` ran when Python executed the `def greet` statement, before
`greet("Ada")` was ever called. `greet.__name__` prints `greet`, not
`wrapper` -- `functools.wraps(func)` on the inner `wrapper` copies
`func.__name__`/`func.__doc__` onto `wrapper` (and sets
`wrapper.__wrapped__`), preserving the original function's identity
through decoration.

### A wrapper can hold its own state

```python
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


@count_calls
def add(a, b):
    return a + b


print(add(2, 3))
print(add(4, 5))
print(add.calls)
```

```text
5
9
2
```

`wrapper.calls` lives on the wrapper function object itself, so state
persists across calls to the decorated function without any global
variable -- each decorated function gets its own `wrapper` closure.

Run the complete companion:

```bash
python lessons/10_iteration_decorators_and_contexts/03_decorators_and_wrappers.py
```

See [`03_decorators_and_wrappers.py`](03_decorators_and_wrappers.py) for
the full sequence, including `greet.__doc__`.

> **Try one change:** remove the `@functools.wraps(func)` line from
> `uppercase` and predict what `greet.__name__` prints afterward.
> Without it, `wrapper` itself (not `greet`) is the function object being
> introspected, so its name and docstring would be `wrapper`'s, not the
> original `greet`'s.

## 4️⃣ Decorator factories and `@contextmanager`

A decorator factory is a function that returns a decorator, letting the
decorator itself accept arguments:

```python
import functools


def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]

        return wrapper

    return decorator


@repeat(times=3)
def greet_once(name):
    return f"Hi, {name}"


print(greet_once("Ada"))
```

```text
['Hi, Ada', 'Hi, Ada', 'Hi, Ada']
```

Calling `repeat(3)` runs immediately and returns `decorator`, which
Python then applies to `greet_once` at `def` time -- `repeat(3)`'s
argument (`times=3`) shaped what `decorator` built, before `greet_once`
was ever called. Only `wrapper` runs on each later call.

### `@contextmanager`: one `yield`, `finally` for cleanup

```python
from contextlib import contextmanager


@contextmanager
def temporary_value(mapping, key, value):
    had_key = key in mapping
    previous = mapping.get(key)
    mapping[key] = value
    try:
        yield mapping[key]
    finally:
        if had_key:
            mapping[key] = previous
        else:
            del mapping[key]


settings = {"mode": "production"}
with temporary_value(settings, "mode", "debug") as active_mode:
    print("Inside the with block, mode is:", active_mode)
print("After the with block, mode is restored:", settings)
```

```text
Inside the with block, mode is: debug
After the with block, mode is restored: {'mode': 'production'}
```

The code before `yield` acts like `__enter__`; the single yielded value
(`mapping[key]`) is what `as` binds; the code after `yield` -- inside
`finally` -- acts like `__exit__`, exactly like Chapter 7's
`ManagedFile.__exit__`.

### Cleanup runs on failure too, and the exception still propagates

```python
try:
    with temporary_value(settings, "mode", "debug"):
        raise RuntimeError("simulated failure while mode is temporarily changed")
except RuntimeError as error:
    print("Caught the propagated error:", error)
print("settings restored even after failure:", settings)
```

```text
Caught the propagated error: simulated failure while mode is temporarily changed
settings restored even after failure: {'mode': 'production'}
```

`settings` is restored to `{'mode': 'production'}` after both the
successful block above and this block that raised `RuntimeError` -- the
generator's `finally` ran either way, and the exception still propagated
afterward. Neither guarantee (cleanup, propagation) is sacrificed for
the other.

Run the complete companion:

```bash
python lessons/10_iteration_decorators_and_contexts/04_decorator_factories_and_contextmanager.py
```

See
[`04_decorator_factories_and_contextmanager.py`](04_decorator_factories_and_contextmanager.py)
for the full sequence, including a key that did not exist before being
removed entirely afterward.

> **Try one change:** change the `finally:` block's restoration logic to
> omit the `if had_key:` check (always doing `mapping[key] = previous`)
> and predict what `settings` looks like after a block where the key had
> no previous value at all.

## 🔁 Transition to Chapter 11

This chapter generalized iteration and wrapping behavior, but every
function signature so far has stayed informally typed. Chapter 11,
Typing, Protocols, and Dependency Injection, makes contracts explicit --
narrowing types, generic functions over `Iterable`/`Sequence`/`Callable`,
and `Protocol`-based structural typing -- the vocabulary later chapters
(SQL, HTTP) rely on to describe interfaces without inheritance.

## ⚠️ Common mistakes

- Assuming a generator can be iterated more than once, instead of calling
  the generator function again for a fresh one.
- Forgetting `functools.wraps`, which leaves `__name__`/`__doc__`
  reporting the wrapper's identity instead of the wrapped function's.
- Writing a decorator factory's `decorator(func)` step so it re-reads its
  outer argument (like `times`) incorrectly across multiple decorated
  functions, instead of relying on each call's own closure.
- Omitting `finally` inside a `@contextmanager` generator, so cleanup is
  skipped whenever the `with` block raises.
- Yielding more than once from a `@contextmanager` generator without a
  loop, which raises `RuntimeError` at the second `yield`.

## 🧾 Summary

- An iterator is any object supporting `next()`; a `for` loop is just
  repeated `next()` calls until `StopIteration`.
- `yield` builds an iterator automatically: calling a generator function
  is instant, and its body runs lazily, one `yield` at a time.
- A decorator replaces a function with another one at `def` time;
  `functools.wraps` keeps the replacement's identity looking like the
  original.
- A decorator factory returns a decorator, letting the decorator itself
  take configuration.
- `@contextmanager` turns a single-`yield` generator into a context
  manager, with `finally` providing the same success-or-failure cleanup
  guarantee as a class-based `__exit__`.

## ❓ Review questions (closed notes)

1. What is the difference between an iterable and an iterator?
2. What does `StopIteration` signal, and who normally catches it?
3. Why does calling a generator function not run its body immediately?
4. What problem does `functools.wraps` solve, and what would break
   without it?
5. Why does a decorator factory need an extra layer of function
   compared to a plain decorator?
6. In a `@contextmanager` generator, what plays the role of `__exit__`,
   and why must it be wrapped in `finally`?

## 📚 Authoritative references

- [Iterator types](https://docs.python.org/3/library/stdtypes.html#iterator-types)
- [`yield` expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions)
- [`functools.wraps`](https://docs.python.org/3/library/functools.html#functools.wraps)
- [`contextlib.contextmanager`](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)

Once you can answer the review questions and have run all four lesson
files, continue to
[`exercises/10_iteration_decorators_and_contexts/`](../../exercises/10_iteration_decorators_and_contexts/README.md).
