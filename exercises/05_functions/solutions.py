"""
Solutions: Chapter 5 - Function Contracts and Scope

Reference solutions for exercises/05_functions/exercises.py.

Run this file directly:

    python exercises/05_functions/solutions.py
"""


def sum_all(*numbers):
    return sum(numbers)


def format_label(name, /, *, category):
    return f"{category}: {name}"


def describe(**details):
    parts = [f"{key}={value}" for key, value in details.items()]
    return ", ".join(parts)


def append_and_return_none(items, item):
    items.append(item)


def make_running_total():
    total = 0

    def add(amount):
        nonlocal total
        total += amount
        return total

    return add


def sort_by_length(words):
    return sorted(words, key=lambda word: len(word))


def recursive_sum(nested):
    total = 0
    for value in nested:
        if isinstance(value, list):
            total += recursive_sum(value)
        else:
            total += value
    return total


assert sum_all(1, 2, 3) == 6
assert sum_all() == 0
print("sum_all: OK")

assert format_label("Functions", category="Lesson") == "Lesson: Functions"
print("format_label: OK")

assert describe(name="Ada", age=36) == "name=Ada, age=36"
print("describe: OK")

topics = ["parameters"]
result = append_and_return_none(topics, "return values")
assert topics == ["parameters", "return values"]
assert result is None
print("append_and_return_none: OK")

running_total = make_running_total()
assert running_total(10) == 10
assert running_total(5) == 15
another_total = make_running_total()
assert another_total(100) == 100
assert running_total(1) == 16
print("make_running_total: OK")

words = ["banana", "kiwi", "apple", "fig"]
assert sort_by_length(words) == ["fig", "kiwi", "apple", "banana"]
assert words == ["banana", "kiwi", "apple", "fig"]
print("sort_by_length: OK")

assert recursive_sum([1, [2, 3], [4, [5, 6]]]) == 21
assert recursive_sum([]) == 0
print("recursive_sum: OK")

print("\nAll checks passed!")
