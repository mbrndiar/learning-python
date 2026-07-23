"""
Exercises: Chapter 3 - Collections

Still no function definitions -- Chapter 5 introduces `def`. Every task
below is solvable with construction, indexing, membership tests, and
methods alone: no `for`, `while`, comprehensions, or `zip`.

Run this file directly:

    python exercises/03_collections/exercises.py
"""

# --- Task 1: mutate one byte, leave the original bytes untouched ----------
# Replace the second byte of `original_code` with the byte value for "X"
# (ord("X")), producing `updated_code`, without changing `original_code`.
original_code = b"A1B2"

# TODO: build a bytearray from original_code, replace index 1, then convert
# the result back to bytes as `updated_code`.
updated_code = original_code

assert updated_code == b"AXB2", "Task 1: replace byte index 1 with ord('X')"
assert original_code == b"A1B2"
print("Task 1 (mutate one byte): OK")

# --- Task 2: in-place list mutation is visible through every alias --------
# `topics` and `topics_alias` are two names for the same list. Append
# "recursion" through `topics_alias`, in place (do not rebind either name).
topics = ["variables", "loops"]
topics_alias = topics

# TODO: mutate the shared list in place through topics_alias.

assert topics == ["variables", "loops", "recursion"], (
    "Task 2: append 'recursion' through topics_alias"
)
assert topics_alias == topics
assert topics_alias is topics
print("Task 2 (in-place mutation through an alias): OK")

# --- Task 3: unique, sorted values -----------------------------------------
# Build a sorted list of the unique values in `readings`, using set() to
# deduplicate and sorted() to order the result.
readings = [7, 3, 7, 1, 3, 9, 1]

# TODO: replace the initial value with the sorted, deduplicated list.
unique_readings = readings

assert unique_readings == [1, 3, 7, 9], "Task 3: build sorted(set(readings))"
print("Task 3 (unique, sorted values): OK")

# --- Task 4: dict construction, lookup, update, and membership ------------
# Build `inventory` mapping item names to counts, then perform the requested
# operations without rebinding `inventory` to a new dict.
inventory = {"pencils": 12, "erasers": 4}

# TODO 4a: add a new key "rulers" with value 6.
# TODO 4b: update "erasers" to 10.
# TODO 4c: use .get() to look up "staplers" with a default of 0, storing the
# result as `stapler_count`.
stapler_count = None
# TODO 4d: store whether "pencils" is a key in inventory as `has_pencils`.
has_pencils = None

assert inventory == {"pencils": 12, "erasers": 10, "rulers": 6}, (
    "Task 4: add rulers and update erasers in inventory"
)
assert stapler_count == 0, "Task 4: use inventory.get('staplers', 0)"
assert has_pencils, "Task 4: test whether pencils is a key"
print("Task 4 (dict construction, lookup, update, membership): OK")

# --- Task 5: set algebra ----------------------------------------------------
# Compute the union, intersection, and difference of the two tag sets below.
backend_tags = {"python", "sql", "testing"}
frontend_tags = {"javascript", "testing", "css"}

# TODO: replace each empty set with the requested set.
shared_tags = set()  # tags in both sets
all_tags = set()  # tags in either set
backend_only_tags = set()  # tags only in backend_tags

assert shared_tags == {"testing"}, "Task 5: compute the intersection with &"
assert all_tags == {"python", "sql", "testing", "javascript", "css"}
assert backend_only_tags == {"python", "sql"}
print("Task 5 (set algebra): OK")

# --- Task 6: shallow copy versus shared inner mutation ---------------------
# `grouped` is a list of two inner lists. `grouped_copy` is a shallow copy.
# Mutate grouped_copy[0] in place (so it also changes `grouped`), then
# *replace* grouped_copy[1] with a new list (so it does NOT change `grouped`).
grouped = [["red", "green"], ["small", "medium"]]
grouped_copy = grouped.copy()

# TODO 6a: mutate grouped_copy[0] in place to add "blue".
# TODO 6b: replace grouped_copy[1] entirely with ["large"].

assert grouped == [["red", "green", "blue"], ["small", "medium"]], (
    "Task 6: append 'blue' through the shallow copy"
)
assert grouped_copy == [["red", "green", "blue"], ["large"]]
print("Task 6 (shallow copy versus shared inner mutation): OK")

print("\nAll checks passed!")
