# 📦 Exercises: Chapter 6 - Modules and Packages

**Prerequisites:** completed
[`lessons/06_modules_and_packages/`](../../lessons/06_modules_and_packages/README.md).

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/06_modules_and_packages/exercises.py

# Compile-check without running:
python -m py_compile exercises/06_modules_and_packages/exercises.py

# Check the reference solution:
python exercises/06_modules_and_packages/solutions.py
```

## Tasks

1. **`describe_greeting(name)`** - import `hello` from
   `example_package.greetings` (a parallel package fixture) with an
   absolute import, and return its result.
2. **`public_api_names()`** - import the `example_package` package itself
   and return the sorted list of names its `__init__.py` re-exports through
   `__all__`.
3. **`entry_point_label(module_name)`** - classify the `__name__` string as
   `"script"` (`"__main__"`) or `"import"` (anything else).

## Constraints

- This chapter's checks do not require `try`/`except`; every task is
  solved with a direct import, attribute access, or comparison.
- Each starter initially returns `None`, so the first assertion fails with
  the task's contract until you implement it.
- `example_package` lives beside the exercise script, so normal script
  import resolution finds it without path manipulation.

## Edge cases exercised

- `public_api_names()` must return a *sorted* list -- `__all__`'s
  definition order is not guaranteed to already be alphabetical, so relying
  on it unsorted would be a latent bug even though this particular
  `__all__` happens to already look sorted.
- `entry_point_label` is checked with `sample_module.__name__` (reached
  through import) and this directly-run file's own `__name__`.
