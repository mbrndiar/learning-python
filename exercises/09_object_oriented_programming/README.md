# 🧩 Exercises: Chapter 9 - Objects and Data Models

**Prerequisites:** completed
[`lessons/09_object_oriented_programming/`](../../lessons/09_object_oriented_programming/README.md).

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/09_object_oriented_programming/exercises.py

# Compile-check without running:
python -m py_compile exercises/09_object_oriented_programming/exercises.py

# Check the reference solution:
python exercises/09_object_oriented_programming/solutions.py
```

## Tasks

1. **`Rectangle`** / **`Square`** - store dimensions on the instance and
   implement `area()`/`perimeter()`; `Square` reuses `Rectangle.__init__`
   via `super()`.
2. **`Animal`** / **`Dog`** / **`Cat`** - practice a coherent "is a"
   hierarchy and polymorphism by overriding `speak()`.
3. **`BankAccount`** - expose a read-only `balance` property, validate
   `deposit`, and raise the custom `InsufficientFundsError` (not a plain
   `ValueError`) from `withdraw` when funds are insufficient.
4. **`InsufficientFundsError`** - a custom exception, defined only now
   that inheritance has been taught, storing `balance` and `amount` as
   attributes a handler can read directly.
5. **`Vector`** - implement `__eq__` and `__add__`, returning
   `NotImplemented` for an unsupported operand type.
6. **`Task`** / **`TaskStatus`** - combine a `@dataclass` with an `Enum`,
   keep each task's notes independent with `field(default_factory=list)`,
   and export an independent dictionary with `asdict()`.

## Constraints

- Each starter initially raises `NotImplementedError`, so the checks stop
  at the first incomplete task with a focused traceback.
- `InsufficientFundsError` must be constructed as
  `InsufficientFundsError(balance, amount)` and must still call
  `super().__init__(...)` with a descriptive message, so it remains a
  well-formed `Exception` as well as a structured one.
- `__eq__`/`__add__` must return the literal `NotImplemented` object (not
  raise) for a non-`Vector` operand.

## Edge cases exercised

- `BankAccount.withdraw` is checked on a request that exceeds the current
  balance, asserting both that `InsufficientFundsError` is raised (not
  `ValueError`) and that its `.balance`/`.amount` attributes match the
  account state at the time of the failed withdrawal.
- `Vector.__add__(Vector(1, 2), 3)` is checked directly against the
  literal `NotImplemented` object, not just "raises an exception."
- `Task` checks prove that mutable defaults are not shared, `asdict()` returns
  independent nested containers, and generated equality includes enum and
  list fields after `complete()`.
