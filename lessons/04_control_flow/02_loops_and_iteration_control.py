"""
Chapter 4, Lesson 2: Loops and Iteration Control

Purpose: introduce `for`, `while`, `range`, `enumerate`, `zip`, accumulator
and search patterns, `break`, `continue`, and the loop `else` clause.

Prerequisites: 01_conditions_and_truthiness.py.

Read this file top to bottom, predict each output, then run it:

    python lessons/04_control_flow/02_loops_and_iteration_control.py
"""

# Step 1: a `for` loop consumes an iterable, one element per pass.
# range(1, 6) yields 1, 2, 3, 4, 5 -- the stop value is excluded.
print("Counting from 1 to 5:")
for number in range(1, 6):
    print(number)

fruits = ["apple", "banana", "cherry"]
print("\nFruits:")
for fruit in fruits:
    print("-", fruit)

# Step 2: a `while` loop repeats for as long as its condition stays truthy.
# The body must eventually make the condition false, or the loop never
# ends (unless it is deliberately exited with `break`).
print("\nCountdown:")
countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Liftoff!")

# Step 3: enumerate() pairs each element with its index, avoiding a manual
# counter. zip() walks several iterables together, stopping at the
# shortest one.
print("\nenumerate(fruits):")
for index, fruit in enumerate(fruits):
    print(f"  {index}: {fruit}")

prices = [1.20, 0.55, 2.10]
print("\nzip(fruits, prices):")
for fruit, price in zip(fruits, prices):
    print(f"  {fruit}: {price:.2f}")

# Step 4: break exits the nearest loop immediately. continue skips only the
# rest of the current pass and asks the loop for its next value.
print("\nSkip even numbers, stop at 7:")
for number in range(1, 10):
    if number == 7:
        break
    if number % 2 == 0:
        continue
    print(number)

# Step 5: a loop's `else` block runs only if the loop finished without
# hitting `break` -- it does not mean "the iterable was empty." This is the
# classic linear-search pattern: search, break on success, else means "not
# found."
print("\nSearch for a fruit:")
target = "pear"
for fruit in fruits:
    if fruit == target:
        print("Found:", target)
        break
else:
    print("Not found:", target)

# Step 6: accumulator pattern. A loop can build up a result across passes --
# here, a running total and a running maximum, both starting from an
# explicit initial value before the loop begins.
readings = [12, 45, 7, 68, 23]
total = 0
highest = readings[0]
for reading in readings:
    total += reading
    if reading > highest:
        highest = reading
print("\ntotal:", total)
print("highest:", highest)

# --- One-variable experiment -------------------------------------------
# Change `target` in Step 5 to "banana" (present in fruits) and predict
# whether the `else` block still runs before rerunning.
