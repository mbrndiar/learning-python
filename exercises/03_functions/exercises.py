"""
Exercises: 03 Functions

Implement each function below, then run this file directly to check
your work.
"""


def make_multiplier(factor):
    """Return a function that multiplies its argument by `factor`.

    Example: double = make_multiplier(2); double(5) -> 10
    This is a closure, similar to lesson 3.2.
    """
    # TODO: implement this function
    raise NotImplementedError


def sum_all(*args):
    """Return the sum of any number of positional arguments."""
    # TODO: implement this function
    raise NotImplementedError


def describe(**kwargs):
    """Return a string like "name=Ada, age=36" built from keyword
    arguments, in the order they were given."""
    # TODO: implement this function
    raise NotImplementedError


def format_label(name, /, *, category):
    """Return "category: name".

    `name` must be positional and `category` must be passed by keyword.
    """
    # TODO: implement this function
    raise NotImplementedError


def record_topic(topics, topic):
    """Append `topic` to the caller's list in place and return None.

    Mutate the existing list rather than rebinding `topics` to a new list.
    """
    # TODO: implement this function
    raise NotImplementedError


def factorial(n):
    """Return n! computed recursively. factorial(0) == 1."""
    # TODO: implement this function
    raise NotImplementedError


if __name__ == "__main__":
    double = make_multiplier(2)
    triple = make_multiplier(3)
    assert double(5) == 10
    assert triple(5) == 15
    print("make_multiplier: OK")

    assert sum_all(1, 2, 3) == 6
    assert sum_all() == 0
    print("sum_all: OK")

    assert describe(name="Ada", age=36) == "name=Ada, age=36"
    print("describe: OK")

    assert format_label("Functions", category="Lesson") == "Lesson: Functions"
    print("format_label: OK")

    topics = ["parameters"]
    result = record_topic(topics, "return values")
    assert topics == ["parameters", "return values"]
    assert result is None
    print("record_topic: OK")

    assert factorial(0) == 1
    assert factorial(5) == 120
    print("factorial: OK")

    print("\nAll checks passed!")
