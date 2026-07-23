"""
Exercises: Chapter 5 - Function Contracts and Scope

This is the first exercise file in the course that defines functions.
Implement each function below, then run this file directly to check your
work.

    python exercises/05_functions/exercises.py

Each starter returns None until you implement it. The top-level assertions stop
at the first incomplete contract with a focused message; exception syntax is
not required by this chapter.
"""


def sum_all(*numbers):
    """Return the sum of any number of positional arguments.

    sum_all(1, 2, 3) -> 6
    sum_all() -> 0
    """
    # TODO: implement this function.
    return None


def format_label(name, /, *, category):
    """Return "category: name".

    `name` must be positional-only; `category` must be keyword-only.
    """
    # TODO: implement this function.
    return None


def describe(**details):
    """Return a string like "name=Ada, age=36" built from keyword
    arguments, in the order they were given."""
    # TODO: implement this function.
    return None


def append_and_return_none(items, item):
    """Append `item` to the caller's list `items` in place, and return
    None. Mutate the existing list; do not rebind `items`."""
    # TODO: implement this function.
    return None


def make_running_total():
    """Return a function `add(amount)` that, on each call, adds `amount`
    to a running total and returns the new total.

    This is a closure: it must remember the running total between calls,
    without any global or outer-scope variable outside this function.

    running_total = make_running_total()
    running_total(10) -> 10
    running_total(5) -> 15
    """
    # TODO: implement this function, returning a nested `add` function.
    return None


def sort_by_length(words):
    """Return a new list of `words` sorted by length, shortest first.

    Use a lambda as the sort key -- do not modify `words` in place.
    """
    # TODO: implement this function.
    return None


def recursive_sum(nested):
    """Return the total of every number in `nested`, a list that may
    contain further nested lists to any depth.

    recursive_sum([1, [2, 3], [4, [5, 6]]]) -> 21
    recursive_sum([]) -> 0

    Implement this recursively: a base case for an empty list, and
    progress by recursing into any element that is itself a list.
    """
    # TODO: implement this function.
    return None


assert sum_all(1, 2, 3) == 6, "Task 1: sum every positional argument"
assert sum_all() == 0, "Task 1: an empty sum is zero"
print("sum_all: OK")

assert format_label("Functions", category="Lesson") == "Lesson: Functions", (
    "Task 2: format the positional name and keyword category"
)
print("format_label: OK")

assert describe(name="Ada", age=36) == "name=Ada, age=36", (
    "Task 3: preserve keyword argument order"
)
print("describe: OK")

topics = ["parameters"]
result = append_and_return_none(topics, "return values")
assert topics == ["parameters", "return values"], "Task 4: mutate items in place"
assert result is None, "Task 4: return None"
print("append_and_return_none: OK")

running_total = make_running_total()
assert running_total is not None, "Task 5: return the nested add function"
assert running_total(10) == 10
assert running_total(5) == 15
another_total = make_running_total()
assert another_total(100) == 100  # independent from running_total
assert running_total(1) == 16  # unaffected by another_total
print("make_running_total: OK")

words = ["banana", "kiwi", "apple", "fig"]
assert sort_by_length(words) == ["fig", "kiwi", "apple", "banana"], (
    "Task 6: return a new list sorted by len"
)
assert words == ["banana", "kiwi", "apple", "fig"]  # original unchanged
print("sort_by_length: OK")

assert recursive_sum([1, [2, 3], [4, [5, 6]]]) == 21, (
    "Task 7: recursively sum nested lists"
)
assert recursive_sum([]) == 0, "Task 7: handle the empty-list base case"
print("recursive_sum: OK")

print("\nAll checks passed!")
