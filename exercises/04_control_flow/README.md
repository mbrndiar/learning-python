# Exercises: Chapter 4 - Flow and Iteration

**Prerequisites:** completed
[`lessons/04_control_flow/`](../../lessons/04_control_flow/README.md).
No function definitions yet -- Chapter 5 introduces `def`.

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/04_control_flow/exercises.py

# Compile-check without running:
python -m py_compile exercises/04_control_flow/exercises.py

# Check the reference solution:
python exercises/04_control_flow/solutions.py
```

## Tasks

1. **FizzBuzz** - build a 15-line FizzBuzz list with a `for` loop and an
   `if`/`elif`/`else` chain.
2. **Count evens** - count even values in a list with an accumulator.
3. **First negative (break/else)** - find the first negative value, using
   `break` on success and the loop's `else` clause for "not found."
4. **Sum skipping multiples of three (continue)** - sum 1 through 20 while
   using `continue` to skip multiples of 3.
5. **Index of first match (enumerate)** - use `enumerate()` with
   `break`/`else` to find an index, or `-1` if absent.
6. **Pair two lists (zip)** - use `zip()` to build formatted strings from
   two same-length lists.
7. **Invert a dictionary** - swap keys and values.
8. **Manual word frequencies** - build a frequency dict by hand with an
   accumulator loop.
9. **Most common tags (Counter)** - use `collections.Counter.most_common()`.
10. **Group by length (defaultdict)** - use `collections.defaultdict(list)`
    to group values, then convert to a plain `dict`.

## Constraints

- No learner-authored `def` -- every task is a top-level script computation.
- Every task is solved with the mechanisms from this chapter's lessons:
  `if`/`elif`/`else`, `for`, `while`, `range`, `enumerate`, `zip`, `break`,
  `continue`, loop `else`, accumulators, `Counter`, `defaultdict`.
- Inputs and expected outputs are fixed and asserted in-file. The first
  incomplete task fails with an assertion message naming the required pattern.
- The starter is expected to fail on Task 1 until you fill it in -- that
  nonzero exit is the correct, focused starting state, not a bug.

## Edge cases exercised

- Task 3 and Task 5 both require the loop's `else` clause to fire only when
  no `break` occurred -- notice this is the *same* pattern applied to two
  different searches.
- Task 6's `zip()` call receives equal-length lists on purpose; the lesson
  file demonstrates what happens with mismatched lengths.
- Task 9's tie-breaking behavior for `Counter.most_common()` follows
  first-seen order among equal counts.
