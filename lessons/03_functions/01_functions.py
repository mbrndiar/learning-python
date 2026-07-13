"""
Lesson 3.1: Functions

Functions package reusable logic behind a name and a contract. Parameters are
local names bound to arguments supplied by the caller; return passes a result
back and immediately ends the call.
"""


def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"


def add(a, b=0):
    """Add two numbers together. Defaults are evaluated when `def` runs."""
    return a + b


def describe_person(name, age, city="Unknown"):
    """Demonstrate positional, default and keyword arguments."""
    return f"{name} is {age} years old and lives in {city}."


def sum_all(*numbers):
    """Accept positional arguments collected into the tuple `numbers`."""
    return sum(numbers)


def print_info(**details):
    """Accept keyword arguments collected into the dictionary `details`."""
    for key, value in details.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print(greet("Ada"))
    print("add(2, 3) =", add(2, 3))
    print("add(5) =", add(5))
    print(describe_person("Grace", 34, city="London"))
    print(describe_person("Alan", 40))
    print("sum_all(1, 2, 3, 4) =", sum_all(1, 2, 3, 4))
    print("print_info(...):")
    print_info(language="Python", level="beginner")
