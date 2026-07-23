"""
Exercises: Chapter 1 - Python Fundamentals

This file has no function definitions -- Chapter 1 has not taught `def` yet.
Each task below is a small top-level script step: replace the initial value
marked with TODO, then run this file directly:

    python exercises/01_python_fundamentals/exercises.py

Each task uses only Chapter 1's `assert` self-checks. The first incorrect task
stops with a focused message; completed tasks print an "OK" line.
"""

# --- Task 1: classify values by type -------------------------------------
# Check each value with isinstance(...), plus the standard `is None` test.
# This is deliberately different data than the lesson used (which classified
# name/age/height/is_learning/favorite_color).
mystery_count = 7
mystery_ratio = 0.5
mystery_label = "Bristol"
mystery_flag = False
mystery_missing = None

# TODO: replace each None with the requested isinstance(...) or `is None` check.
count_is_int = None
ratio_is_float = None
label_is_str = None
flag_is_bool = None
missing_is_none = None

assert count_is_int, "Task 1: check mystery_count with isinstance(..., int)"
assert ratio_is_float, "Task 1: check mystery_ratio with isinstance(..., float)"
assert label_is_str, "Task 1: check mystery_label with isinstance(..., str)"
assert flag_is_bool, "Task 1: check mystery_flag with isinstance(..., bool)"
assert missing_is_none, "Task 1: check mystery_missing with `is None`"
print("Task 1 (classify values by type): OK")

# --- Task 2: explicit conversions -----------------------------------------
# Convert the raw inputs below to the requested types, explicitly.
quantity_text = "17"
unit_price_text = "9.5"
remaining_stock = 0

# TODO: replace each initial value with the requested conversion.
quantity = 0  # int(quantity_text)
unit_price = 0.0  # float(unit_price_text)
remaining_stock_label = ""  # str(remaining_stock)
is_in_stock = True  # bool(remaining_stock)

assert quantity == 17, "Task 2: convert quantity_text with int()"
assert unit_price == 9.5, "Task 2: convert unit_price_text with float()"
assert remaining_stock_label == "0", "Task 2: convert remaining_stock with str()"
assert not is_in_stock, "Task 2: convert remaining_stock with bool()"
print("Task 2 (explicit conversions): OK")

# --- Task 3: predict truthiness --------------------------------------------
# Before running, predict bool(...) for each name below, then fill in the
# initial values with your prediction. Remember: truthiness checks
# emptiness/zero-ness, not word content.
empty_text = ""
zero_as_text = "0"
zero_as_int = 0
negative_one = -1
nothing = None

# TODO: replace each None with your predicted result (True or False).
empty_text_is_truthy = None
zero_as_text_is_truthy = None
zero_as_int_is_truthy = None
negative_one_is_truthy = None
nothing_is_truthy = None

assert empty_text_is_truthy == bool(empty_text), "Task 3: predict bool(empty_text)"
assert zero_as_text_is_truthy == bool(zero_as_text), (
    "Task 3: predict bool(zero_as_text)"
)
assert zero_as_int_is_truthy == bool(zero_as_int), "Task 3: predict bool(zero_as_int)"
assert negative_one_is_truthy == bool(negative_one), (
    "Task 3: predict bool(negative_one)"
)
assert nothing_is_truthy == bool(nothing), "Task 3: predict bool(nothing)"
print("Task 3 (predict truthiness): OK")

print("\nAll checks passed!")
