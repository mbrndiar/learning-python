"""
Chapter 4, Lesson 4: Comprehensions

Purpose: derive list, set, and dict comprehensions directly from an
equivalent loop, then extend to a filtering condition and a nested (two-
level) form once the basic translation is clear.

Prerequisites: 03_accumulators_and_specialized_collections.py.

Read this file top to bottom, predict each output, then run it:

    python lessons/04_control_flow/04_comprehensions.py
"""

numbers = range(1, 11)

# Step 1: a list comprehension is a direct translation of this loop --
# start an empty list, append one transformed value per pass.
squares_loop = []
for n in numbers:
    squares_loop.append(n**2)

# `[expression for name in iterable]` says exactly the same thing in one
# expression: evaluate `expression` once for each `name` drawn from
# `iterable`, and collect the results into a new list.
squares_comprehension = [n**2 for n in numbers]

print("squares_loop:", squares_loop)
print("squares_comprehension:", squares_comprehension)
assert squares_loop == squares_comprehension

# Step 2: adding `if condition` after the `for` clause filters which values
# are included -- again, a direct translation of an `if` inside the loop.
even_squares_loop = []
for n in numbers:
    if n % 2 == 0:
        even_squares_loop.append(n**2)

even_squares_comprehension = [n**2 for n in numbers if n % 2 == 0]

print("\neven_squares_loop:", even_squares_loop)
print("even_squares_comprehension:", even_squares_comprehension)
assert even_squares_loop == even_squares_comprehension

# Step 3: the same translation works for dict and set comprehensions. A
# dict comprehension needs a `key: value` expression; duplicates in a set
# comprehension simply collapse, exactly like a manually built set would.
square_lookup_loop = {}
for n in numbers:
    square_lookup_loop[n] = n**2
square_lookup_comprehension = {n: n**2 for n in numbers}
print("\nsquare_lookup_comprehension:", square_lookup_comprehension)
assert square_lookup_loop == square_lookup_comprehension

remainders_loop = set()
for n in numbers:
    remainders_loop.add(n % 3)
remainders_comprehension = {n % 3 for n in numbers}
print("remainders_comprehension:", sorted(remainders_comprehension))
assert remainders_loop == remainders_comprehension

# Step 4: a nested comprehension mirrors a nested loop. Read it in the same
# order the equivalent loop would run: the leftmost `for` is the outer
# loop.
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

flattened_loop = []
for row in matrix:
    for value in row:
        flattened_loop.append(value)

flattened_comprehension = [value for row in matrix for value in row]

print("\nflattened_loop:", flattened_loop)
print("flattened_comprehension:", flattened_comprehension)
assert flattened_loop == flattened_comprehension

# Step 5: a generator expression looks like a list comprehension without
# the brackets. It computes values lazily, on demand, instead of building
# the whole list first -- useful when a result (such as a sum) is all that
# is needed.
sum_of_squares = sum(n**2 for n in numbers)
print("\nsum_of_squares:", sum_of_squares)
assert sum_of_squares == sum(squares_comprehension)

# --- One-variable experiment -------------------------------------------
# Change the filter in Step 2 from `n % 2 == 0` to `n % 2 != 0` and predict
# even_squares_comprehension's new contents before rerunning.
