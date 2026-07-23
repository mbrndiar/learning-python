"""
Chapter 4, Lesson 3: Accumulators and Specialized Collections

Purpose: build frequency and grouping dictionaries by hand with a loop
first, then compare that manual approach with `collections.Counter` and
`collections.defaultdict`, which solve the same problems more concisely.

Prerequisites: 02_loops_and_iteration_control.py (for loops, accumulators).

The standard-library import is the same bounded preview used in Chapter 2:
it only makes Counter and defaultdict available here. Chapter 6 explains the
import system itself.

Read this file top to bottom, predict each output, then run it:

    python lessons/04_control_flow/03_accumulators_and_specialized_collections.py
"""

from collections import Counter, defaultdict

words = ["fox", "dog", "fox", "cat", "dog", "fox"]

# Step 1: a frequency count, built by hand. `dict.get(key, default)` reads
# "0 if key is new, otherwise its current count" without raising KeyError.
manual_counts = {}
for word in words:
    manual_counts[word] = manual_counts.get(word, 0) + 1
print("manual_counts:", manual_counts)

# Step 2: Counter does exactly this, in one call, and adds convenience
# methods such as .most_common().
counter_counts = Counter(words)
print("\ncounter_counts:", counter_counts)
print("most_common(2):", counter_counts.most_common(2))
assert dict(counter_counts) == manual_counts

# Step 3: a grouping dictionary, built by hand. `dict.setdefault(key, [])`
# returns the existing list for `key`, or inserts and returns a new empty
# list if `key` is new -- either way, the returned list can be appended to
# immediately.
animals = ["fox", "dog", "cat", "ferret", "camel", "capybara"]
manual_groups = {}
for animal in animals:
    first_letter = animal[0]
    manual_groups.setdefault(first_letter, []).append(animal)
print("\nmanual_groups:", manual_groups)

# Step 4: defaultdict(list) removes the need for setdefault: looking up a
# missing key automatically creates one empty list (from calling the
# factory, `list`) instead of raising KeyError.
default_groups = defaultdict(list)
for animal in animals:
    default_groups[animal[0]].append(animal)
print("\ndefault_groups:", dict(default_groups))
assert dict(default_groups) == manual_groups

# --- One-variable experiment -------------------------------------------
# Change `words` to include one more "cat" and predict how
# `counter_counts.most_common(2)` changes before rerunning -- ties in
# Counter.most_common() keep first-seen order.
