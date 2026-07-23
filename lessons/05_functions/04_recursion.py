"""
Chapter 5, Lesson 4: Recursion

Purpose: cover base cases, progress toward them, stack frames, and when an
iterative solution is the clearer choice.

Prerequisites: 03_scope_closures_and_higher_order.py.

Read this file top to bottom, predict each output, then run it:

    python lessons/05_functions/04_recursion.py
"""


# Step 1: a recursive function calls itself with a smaller version of the
# problem. It needs two things: a base case that stops the recursion
# without recursing further, and progress -- each call must move closer to
# that base case, or the recursion never ends.
def factorial(n):
    if n <= 1:  # base case: nothing left to multiply
        return 1
    return n * factorial(n - 1)  # progress: a strictly smaller n


assert factorial(0) == 1
assert factorial(5) == 120


# Step 2: each active call occupies its own stack frame, holding that
# call's local variables (here, its own `n`). factorial(3) calls
# factorial(2), which calls factorial(1) -- three frames stack up, then
# unwind in reverse as each pending multiplication resolves:
# factorial(1) -> 1
# factorial(2) -> 2 * 1 = 2
# factorial(3) -> 3 * 2 = 6
assert factorial(3) == 6


# Step 3: an equivalent iterative version needs no extra stack frames --
# for a straightforward accumulation like this, iteration is usually the
# clearer and more efficient choice. Recursion earns its keep on problems
# whose shape is naturally recursive, like traversing nested data.
def factorial_iterative(n):
    result = 1
    for factor in range(2, n + 1):
        result *= factor
    return result


assert factorial_iterative(5) == 120


# Step 4: nested lists are a naturally recursive shape -- an element might
# be a plain number, or it might be another list that needs the same
# treatment. sum_nested demonstrates recursing into whichever case applies.
def sum_nested(values):
    total = 0
    for value in values:
        if isinstance(value, list):
            total += sum_nested(value)  # progress: a strictly shallower value
        else:
            total += value
    return total


assert sum_nested([1, [2, 3], [4, [5, 6]]]) == 21
assert sum_nested([]) == 0  # base case reached immediately: nothing to add


# Step 5: Python limits recursion depth (by default, roughly 1000 nested
# calls) to catch runaway recursion before it exhausts memory. A recursive
# call with no base case, or one that never makes progress toward it,
# eventually raises RecursionError.
#
# Bounded preview: the following would raise RecursionError if actually
# called -- shown here only as a comment, not executed, since triggering
# and catching that error is not this lesson's focus:
#
#     def no_base_case(n):
#         return no_base_case(n)  # never stops: no base case, no progress

# --- One-variable experiment -------------------------------------------
# Change sum_nested's input to [1, [2, [3, [4, [5]]]]] (deeper nesting)
# and predict the total before rerunning -- the recursion depth grows with
# nesting depth, not with the number of top-level elements.

print("factorial(5) =", factorial(5))
print("factorial_iterative(5) =", factorial_iterative(5))
print("sum_nested([1, [2, 3], [4, [5, 6]]]) =", sum_nested([1, [2, 3], [4, [5, 6]]]))
