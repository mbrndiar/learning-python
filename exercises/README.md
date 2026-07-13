# Exercises

Each lesson module in `lessons/` has a matching folder here with practice
problems that reinforce what you just learned.

Every module folder contains:

- `exercises.py` - function stubs to implement yourself. Each raises
  `NotImplementedError` with a `# TODO` comment describing the task.
  Fill in the body, then run the file:

  ```bash
  python exercises/01_basics/exercises.py
  ```

  The bottom of the file runs simple checks and prints `All checks
  passed!` once every function is implemented correctly.

- `solutions.py` - a reference implementation, in case you get stuck or
  want to compare approaches. Try to solve each exercise yourself first!

## How to work through an exercise

1. Read the corresponding lesson in `lessons/`.
2. Open `exercises/<module>/exercises.py` and implement each `TODO`.
3. Run the file with `python`; fix any failing checks.
4. Compare with `exercises/<module>/solutions.py` if you'd like a second
   opinion or got stuck.

## A useful problem-solving process

1. Restate the task using concrete inputs and outputs.
2. Write down normal cases, boundary cases, and invalid inputs.
3. Solve one small example manually.
4. Turn those steps into code.
5. Run the supplied checks, then add checks for cases you identified.
6. Refactor only after the behavior is correct.

If you are stuck, reduce the problem. Hard-code one example, replace it with a
variable, then generalize it into a function. Use `print()` or the debugger to
inspect intermediate values. Look at the solution only after making a genuine
attempt; then close it and recreate the idea independently.

## Understanding the checks

The supplied `assert` statements are lightweight feedback, not exhaustive
proof. An assertion raises `AssertionError` when its condition is false:

```python
assert double(4) == 8
```

Add your own assertions for empty values, zero, negative values, mixed case,
and other boundaries when they make sense. Modules 8 and 9 turn this habit
into structured automated testing.

## Using reference solutions well

A reference solution demonstrates one clear approach. Your answer may be
equally correct even if it uses different names or operations. Compare:

- whether both implementations satisfy the stated contract;
- what each does at boundaries or with invalid input;
- which version communicates its intent more clearly; and
- whether either performs unnecessary work.

Do not edit `solutions.py` while solving a task; preserve it as a comparison
point.
