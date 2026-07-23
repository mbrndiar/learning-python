# Exercises: Chapter 5 - Function Contracts and Scope

**Prerequisites:** completed
[`lessons/05_functions/`](../../lessons/05_functions/README.md).
This is the first exercise file in the course that defines functions.

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/05_functions/exercises.py

# Compile-check without running:
python -m py_compile exercises/05_functions/exercises.py

# Check the reference solution:
python exercises/05_functions/solutions.py
```

## Tasks

1. **`sum_all(*numbers)`** - sum any number of positional arguments,
   including zero.
2. **`format_label(name, /, *, category)`** - positional-only `name`,
   keyword-only `category`.
3. **`describe(**details)`** - build a string from keyword arguments,
   preserving call order.
4. **`append_and_return_none(items, item)`** - mutate the caller's list in
   place and return `None`; do not rebind `items`.
5. **`make_running_total()`** - a closure returning an `add(amount)`
   function that accumulates a running total across calls, independent of
   any other closure created from the same factory.
6. **`sort_by_length(words)`** - return a new, length-sorted list using a
   `lambda` sort key, leaving the input list unchanged.
7. **`recursive_sum(nested)`** - recursively total an arbitrarily nested
   list of numbers, with a base case for an empty list.

## Constraints

- Every task is implemented with `def` -- this chapter is where function
  definitions become the normal exercise contract.
- Inputs and expected outputs are fixed and asserted in `exercises.py`.
  Each starter initially returns `None`, so the first assertion fails with
  the task's contract until you implement it.
- The starter is expected to fail on `sum_all` until you fill it in -- that
  nonzero exit is the correct, focused starting state, not a bug.

## Edge cases exercised

- `make_running_total()` is called twice in the checks
  (`running_total` and `another_total`) to confirm each closure's state is
  independent -- a common closure mistake is accidentally sharing state
  across instances.
- `sort_by_length` and `recursive_sum` both assert the original input is
  left unchanged (no in-place mutation) where the contract calls for a new
  value.
- `recursive_sum([])` exercises the base case directly, with no recursive
  call at all.
