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

## 🧩 Progressive syntax and mechanism

1. **Iterable vs. iterator.** `iter(obj)` asks an iterable for an
   iterator; `next(iterator)` asks that iterator for its next value,
   raising `StopIteration` when there is none.
2. **The iterator protocol.** A class with `__iter__` (returning `self`)
   and `__next__` (raising `StopIteration` at the end) works with `for`,
   `next()`, and every other iteration tool.
3. **Generator functions.** A function containing `yield` returns a
   generator object immediately when called; its body runs only as
   values are requested, pausing at each `yield` and resuming right
   after it.
4. **Laziness and exhaustion.** A generator computes nothing until
   iterated, and can be iterated through exactly once; a generator
   expression `(... for ... in ...)` is the lazy counterpart of a list
   comprehension.
5. **Decorators.** `@decorator` above a `def` is equivalent to
   `func = decorator(func)`, run once when the `def` executes;
   `functools.wraps(func)` on the inner wrapper preserves `func.__name__`
   and `func.__doc__`.
6. **Decorator factories.** A function that returns a decorator lets the
   decorator itself take arguments (`@repeat(times=3)` calls `repeat(3)`
   first, which returns the actual decorator).
7. **`@contextmanager`.** A generator function decorated with
   `@contextlib.contextmanager` becomes a context manager: code before
   `yield` acts like `__enter__`, the yielded value is what `as` binds,
   and code after `yield` (inside `finally`) acts like `__exit__`,
   running on both success and failure.

## 📖 Read-predict-run-modify workflow

Work through all four lesson files in order, predicting each output
before running:

```bash
python lessons/10_iteration_decorators_and_contexts/01_iterables_iterators_and_stopiteration.py
python lessons/10_iteration_decorators_and_contexts/02_generators_and_lazy_evaluation.py
python lessons/10_iteration_decorators_and_contexts/03_decorators_and_wrappers.py
python lessons/10_iteration_decorators_and_contexts/04_decorator_factories_and_contextmanager.py
```

### Expected output highlights

- `01_iterables_iterators_and_stopiteration.py`: `iterator_a` and
  `iterator_b` advance independently even though both came from the same
  list -- `iter()` on a list always creates a fresh iterator object.
- `02_generators_and_lazy_evaluation.py`: `type(countdown_gen)` prints
  `<class 'generator'>` -- calling a generator function does not run its
  body; re-consuming the already-exhausted `fib_gen` prints `[]`.
- `03_decorators_and_wrappers.py`: `greet.__name__` prints `greet`, not
  `wrapper` -- confirming `functools.wraps` preserved the original
  function's identity through decoration.
- `04_decorator_factories_and_contextmanager.py`: `settings` is restored
  to `{'mode': 'production'}` after both the successful block AND the
  block that raised `RuntimeError` -- the generator's `finally` ran
  either way, and the exception still propagated afterward.

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
