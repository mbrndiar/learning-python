"""
Chapter 3, Lesson 1: Lists and Tuples

Purpose: construct, index, slice, and mutate lists; construct and unpack
tuples; contrast list mutability with tuple immutability.

Prerequisites: Chapter 2 (operators, strings, indexing/slicing on str).

This lesson deliberately does not use `for`, `while`, or comprehensions --
those arrive in Chapter 4. Every task here is solvable with construction,
indexing, slicing, and methods alone.

Read this file top to bottom, predict each output, then run it:

    python lessons/03_collections/01_lists_and_tuples.py
"""

# Step 1: a list literal is written with square brackets. Lists are ordered
# and mutable: the same list object can change after it is created.
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print("original list:", numbers)
print("first element:", numbers[0])
print("last element:", numbers[-1])
print("slice [1:4]:", numbers[1:4])
print("every other element [::2]:", numbers[::2])

# Step 2: mutating methods change the same list object in place and
# typically return None -- printing their return value directly is a common
# mistake this lesson deliberately avoids.
numbers.append(10)
print("\nafter append(10):", numbers)
numbers.remove(1)  # removes only the first occurrence of the value 1
print("after remove(1):", numbers)
numbers.insert(0, 100)
print("after insert(0, 100):", numbers)
popped = numbers.pop()  # removes and returns the last element
print("after pop():", numbers, "| popped value:", popped)
numbers.sort()  # mutates numbers, returns None
print("after sort():", numbers)
numbers.extend([20, 21])  # appends every element of the given iterable
print("after extend([20, 21]):", numbers)

# Step 3: sorted(list) instead returns a *new* list and leaves the original
# unchanged -- contrast this with list.sort() above.
unsorted_copy = [5, 3, 4]
result_of_sorted = sorted(unsorted_copy)
print("\nsorted(unsorted_copy):", result_of_sorted)
print("unsorted_copy unchanged:", unsorted_copy)

# Step 4: a tuple is written with parentheses (or, for a single-element
# tuple, a trailing comma). Tuples fix their sequence of references; the
# commented item assignment below would raise TypeError.
point = (3, 4)
single_item_tuple = (5,)  # the comma, not the parentheses, makes this a tuple
print("\npoint:", point)
print("single_item_tuple:", single_item_tuple, type(single_item_tuple).__name__)

# point[0] = 10

# Step 5: unpacking assigns each element of a fixed-size sequence to a name
# in one statement. A starred target collects "everything else" into a list.
x, y = point
print("\nx =", x, "| y =", y)

first, *middle, last = [10, 20, 30, 40, 50]
print("first =", first, "| middle =", middle, "| last =", last)

# --- One-variable experiment -------------------------------------------
# Change the starred unpacking above to `first, second, *rest = [10, 20, 30,
# 40, 50]` and predict what `rest` will contain before rerunning.
