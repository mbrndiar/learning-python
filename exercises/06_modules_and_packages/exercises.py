"""
Exercises: Chapter 6 - Modules and Packages

Implement each function below, then run this file directly to check your
work.

    python exercises/06_modules_and_packages/exercises.py

Each starter returns None until you implement it. The top-level assertions
stop at the first incomplete function with a focused message; this chapter's
checks do not require exception syntax.
"""

import sample_module


def describe_greeting(name: str) -> str:
    """Return a polite greeting for *name* by importing `hello` from
    `example_package.greetings` and calling it.

    Use an absolute import (`from example_package.greetings import hello`).
    The exercise package lives beside this script, so it is importable
    without changing Python's search path.
    """
    # TODO: import hello from example_package.greetings and return hello(name)
    return None


def public_api_names() -> list:
    """Return the sorted list of names that `example_package`'s
    `__init__.py` re-exports as its public API.

    Import the `example_package` package itself (not a submodule) and read
    its `__all__` attribute.
    """
    # TODO: import example_package and return sorted(example_package.__all__)
    return None


def entry_point_label(module_name: str) -> str:
    """Return "script" for "__main__", or "import" for any other name."""
    # TODO: implement this function
    return None


assert describe_greeting("Ada") == "Hello, Ada!", (
    "Task 1: import hello from example_package.greetings"
)
assert describe_greeting("  grace   hopper ") == "Hello, Grace Hopper!", (
    "Task 1: preserve the package helper's whitespace normalization"
)
print("describe_greeting: OK")

assert public_api_names() == ["hello", "shout_hello"], (
    "Task 2: read example_package.__all__ and sort it"
)
print("public_api_names: OK")

assert entry_point_label(sample_module.__name__) == "import", (
    "Task 3: sample_module was reached through import, not run as a script"
)
assert entry_point_label(__name__) == "script", (
    "Task 3: this directly-run exercise has __name__ == '__main__'"
)
print("entry_point_label: OK")

print("\nAll checks passed!")
