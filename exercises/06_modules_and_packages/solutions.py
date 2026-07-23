"""
Solutions: Chapter 6 - Modules and Packages

Reference solutions for exercises/06_modules_and_packages/exercises.py.

Run this file directly:

    python exercises/06_modules_and_packages/solutions.py
"""

import sample_module


def describe_greeting(name: str) -> str:
    from example_package.greetings import hello

    return hello(name)


def public_api_names() -> list:
    import example_package

    return sorted(example_package.__all__)


def entry_point_label(module_name: str) -> str:
    return "script" if module_name == "__main__" else "import"


assert describe_greeting("Ada") == "Hello, Ada!"
assert describe_greeting("  grace   hopper ") == "Hello, Grace Hopper!", (
    "Task 1: preserve the package helper's whitespace normalization"
)
print("describe_greeting: OK")

assert public_api_names() == ["hello", "shout_hello"]
print("public_api_names: OK")

assert entry_point_label(sample_module.__name__) == "import"
assert entry_point_label(__name__) == "script"
print("entry_point_label: OK")

print("\nAll checks passed!")
