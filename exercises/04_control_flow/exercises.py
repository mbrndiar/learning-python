"""
Exercises: Chapter 4 - Flow and Iteration

Still no function definitions -- Chapter 5 introduces `def`. Every task
below is solved with top-level conditionals, loops, and comprehensions.

Run this file directly:

    python exercises/04_control_flow/exercises.py
"""

from collections import Counter, defaultdict

# --- Task 1: FizzBuzz, 1..15 ------------------------------------------------
# Build `fizzbuzz_lines`, a list of 15 strings for numbers 1 through 15
# (inclusive): multiples of 3 become "Fizz", multiples of 5 become "Buzz",
# multiples of both become "FizzBuzz", everything else is str(number).
fizzbuzz_lines = []

# TODO: build fizzbuzz_lines with a for loop over range(1, 16) and an
# if/elif/else chain.

assert fizzbuzz_lines[:5] == ["1", "2", "Fizz", "4", "Buzz"], (
    "Task 1: build FizzBuzz output with a for loop"
)
assert fizzbuzz_lines[-1] == "FizzBuzz"
print("Task 1 (FizzBuzz): OK")

# --- Task 2: count even numbers --------------------------------------------
# Count how many values in `readings` are even, as `even_count`.
readings = [3, 8, 15, 22, 41, 6, 7]
even_count = 0

# TODO: loop over readings, incrementing even_count for every even value.

assert even_count == 3, "Task 2: count even readings with an accumulator"
print("Task 2 (count evens): OK")

# --- Task 3: first negative, stop looking once found -----------------------
# Find the first negative number in `measurements` as `first_negative`, or
# None if there isn't one. Stop looking as soon as one is found -- use
# `break` and a loop `else` clause to set the None case.
measurements = [12, 4, -7, 30, -2]
first_negative = None

# TODO: loop over measurements; on the first negative value, break and
# record it. Use the loop's else clause to set first_negative = None only
# if no break occurred.

assert first_negative == -7, "Task 3: find the first negative with for/break/else"
print("Task 3 (first negative, with break/else): OK")

# --- Task 4: sum while skipping multiples of three (continue) -------------
# Sum the numbers 1 through 20 (inclusive), skipping any multiple of 3, as
# `skip_multiples_of_three_total`.
skip_multiples_of_three_total = 0

# TODO: loop over range(1, 21); use `continue` to skip multiples of 3
# before adding to the running total.

assert skip_multiples_of_three_total == 147, (
    "Task 4: skip multiples of three with continue"
)
print("Task 4 (sum skipping multiples of three): OK")

# --- Task 5: index of first match, via enumerate ---------------------------
# Find the index of the first occurrence of "kiwi" in `fruit_order`, as
# `kiwi_index`, or -1 if it is not present. Use enumerate().
fruit_order = ["mango", "fig", "kiwi", "kiwi", "date"]
kiwi_index = -1

# TODO: loop with enumerate(fruit_order); break on the first index whose
# fruit is "kiwi"; use the loop's else clause for the -1 case.

assert kiwi_index == 2, "Task 5: find the first kiwi index with enumerate"
print("Task 5 (index of first match via enumerate): OK")

# --- Task 6: pair two lists with zip ---------------------------------------
# Build `shipment_lines`, a list of "<name> x<qty>" strings, pairing
# `items` and `quantities` positionally with zip().
items = ["bolts", "washers", "nuts"]
quantities = [50, 120, 75]
shipment_lines = []

# TODO: use zip(items, quantities) in a for loop (or comprehension) to
# build the formatted strings.

assert shipment_lines == ["bolts x50", "washers x120", "nuts x75"], (
    "Task 6: pair items and quantities with zip"
)
print("Task 6 (pair two lists with zip): OK")

# --- Task 7: invert a dictionary --------------------------------------------
# Build `role_by_id`, swapping keys and values of `id_by_role`.
id_by_role = {"admin": 1, "editor": 2, "viewer": 3}
role_by_id = {}

# TODO: build role_by_id with a loop or a dict comprehension over
# id_by_role.items().

assert role_by_id == {1: "admin", 2: "editor", 3: "viewer"}, "Task 7: invert id_by_role"
print("Task 7 (invert a dictionary): OK")

# --- Task 8: manual word frequencies ---------------------------------------
# Build `tag_counts`, mapping each tag in `tags` to how many times it
# appears, using a hand-built accumulator loop (not Counter).
tags = ["bug", "feature", "bug", "docs", "bug", "feature"]
tag_counts = {}

# TODO: loop over tags, using tag_counts.get(tag, 0) + 1 to accumulate
# counts -- the same pattern used in the Chapter 4 lesson, applied to new
# data.

assert tag_counts == {"bug": 3, "feature": 2, "docs": 1}, (
    "Task 8: count tags with a dictionary accumulator"
)
print("Task 8 (manual word frequencies): OK")

# --- Task 9: most common tags, via Counter ---------------------------------
# Using Counter, find the 2 most common tags in `tags` as
# `top_two_tags`, a list of (tag, count) pairs.
top_two_tags = []

# TODO: build a Counter from tags, then call .most_common(2).

assert top_two_tags == [("bug", 3), ("feature", 2)], (
    "Task 9: use Counter(tags).most_common(2)"
)
print("Task 9 (most common tags via Counter): OK")

# --- Task 10: group words by length, via defaultdict -----------------------
# Using defaultdict(list), group `catalog` entries by their length, as a
# plain dict `by_length`.
catalog = ["ax", "saw", "bit", "drill", "nail", "rope"]
by_length = {}

# TODO: build a defaultdict(list), append each word under its len(word),
# then convert the result to a plain dict as by_length.

assert by_length == {
    2: ["ax"],
    3: ["saw", "bit"],
    4: ["nail", "rope"],
    5: ["drill"],
}, "Task 10: group words by length with defaultdict(list)"
print("Task 10 (group by length via defaultdict): OK")

print("\nAll checks passed!")
