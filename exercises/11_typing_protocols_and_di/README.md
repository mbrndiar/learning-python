# 🧬 Exercises: Chapter 11 - Typing, Protocols, and Dependency Injection

**Prerequisites:** completed
[`lessons/11_typing_protocols_and_di/`](../../lessons/11_typing_protocols_and_di/README.md).

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/11_typing_protocols_and_di/exercises.py

# Compile-check without running:
python -m py_compile exercises/11_typing_protocols_and_di/exercises.py

# Check the reference solution:
python exercises/11_typing_protocols_and_di/solutions.py
```

## Tasks

1. **`describe_optional_name(name)`** - narrow a `str | None` union with
   an `is None` check before calling a `str`-only method.
2. **`last(items)`** - a generic function (`TypeVar`) returning the last
   element of a non-empty list, with its type tied to the list's element
   type.
3. **`access_label` / `repeat_label`** - use `Literal` for a finite choice
   and `Annotated` for metadata, while enforcing the positive-count rule
   explicitly at runtime.
4. **`Query.where`** - use `Self` to describe and implement a fluent method
   that returns the same instance.
5. **`Notifier` Protocol / `AlertService`** - depend on a `Notifier`
   Protocol instead of one concrete class, delegating `alert()` to
   `notifier.notify(...)`.
6. **`RecordingNotifier`** / **`UppercaseNotifier`** - two interchangeable
   `Notifier` implementations, neither inheriting from `Notifier`, proving
   `AlertService` works unchanged with either one.

## Constraints

- Each starter initially raises `NotImplementedError`, so the checks stop
  at the first incomplete task with a focused traceback.
- Neither `RecordingNotifier` nor `UppercaseNotifier` inherits from
  `Notifier` -- both satisfy it purely by defining a matching `notify`
  method (structural typing).
- `AlertService` must not construct a `Notifier` itself; it must only use
  the one passed to it (dependency injection).
- `Annotated` metadata is not runtime validation. `repeat_label` must still
  check `count` and raise `ValueError` when it is not positive.

## Edge cases exercised

- `describe_optional_name` is checked on both `None` and a real string,
  covering both branches of the narrowed union.
- `last` is checked with two different element types (`int` and `str`)
  from the same function definition, confirming the generic is not
  hardcoded to one type.
- `access_label` covers both declared `Literal` values; `repeat_label`
  covers valid and non-positive counts.
- Two chained `Query.where` calls must return the original object, not a
  replacement with lost state.
- `AlertService` is checked against two Notifiers with genuinely
  different behavior (recording verbatim vs. upper-casing), confirming
  `AlertService.alert()` itself never needs to change to support either.
