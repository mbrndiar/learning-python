# 🧠 Exercises

Each lesson module in `lessons/` has a matching folder here with practice
problems that reinforce what you just learned.

For experiments that do not belong to a graded module, use the optional
[`00_playground/`](00_playground/README.md). Its local `main.py` is ignored by
Git and is never treated as course progress or evaluator input.

Every module folder contains a primary pair:

- `exercises.py` - top-level tasks (Chapters 1-4) or function/class stubs
  (from Chapter 5 onward) to implement yourself. TODO comments describe the
  missing behavior, and focused assertions identify the next unfinished task.
  Fill in the requested parts, then run the file:

  ```bash
  python exercises/01_python_fundamentals/exercises.py
  ```

  The file stops at the first unfinished task and prints `All checks passed!`
  once every requested behavior is implemented correctly. The testing module
  instead refuses to report success until all requested test methods exist.

- `solutions.py` - a reference implementation, in case you get stuck or
  want to compare approaches. Try to solve each exercise yourself first!

## 🧭 Modules 14–16 and the applied project

Complete the advanced sequence in this order:

1. [`10_sql_and_sqlite/`](10_sql_and_sqlite/README.md);
2. [`11_rest_apis_and_clients/`](11_rest_apis_and_clients/README.md);
3. the required
   [Task REST API and clients project](../projects/tasks/README.md); and
4. [`12_concurrency/`](12_concurrency/README.md).

The REST exercises practice request mapping, exact query parsing, error/status
mapping, injected HTTP transports, and malformed-response validation.

## ▶️ How to work through an exercise

1. Read the corresponding lesson in `lessons/`.
2. Open `exercises/<module>/exercises.py` and implement each `TODO`.
3. Run the file with `python`; fix any failing checks.
4. Compare with `exercises/<module>/solutions.py` if you'd like a second
   opinion or got stuck.

## 🧩 A useful problem-solving process

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

## ✅ Understanding the checks

The supplied `assert` statements are lightweight feedback, not exhaustive
proof. An assertion raises `AssertionError` when its condition is false:

```python
assert double(4) == 8
```

Add your own assertions for empty values, zero, negative values, mixed case,
and other boundaries when they make sense. Modules 9 and 10 turn this habit
into structured automated testing.

## 🔍 Using reference solutions well

A reference solution demonstrates one clear approach. Your answer may be
equally correct even if it uses different names or operations. Compare:

- whether both implementations satisfy the stated contract;
- what each does at boundaries or with invalid input;
- which version communicates its intent more clearly; and
- whether either performs unnecessary work.

Do not edit `solutions.py` while solving a task; preserve it as a comparison
point.
