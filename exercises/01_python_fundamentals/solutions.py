"""
Solutions: Chapter 1 - Python Fundamentals

Reference implementation for exercises/01_python_fundamentals/exercises.py.
Try to solve the exercises yourself before checking this file!
"""

# --- Task 1: classify values by type -------------------------------------
mystery_count = 7
mystery_ratio = 0.5
mystery_label = "Bristol"
mystery_flag = False
mystery_missing = None

count_is_int = isinstance(mystery_count, int)
ratio_is_float = isinstance(mystery_ratio, float)
label_is_str = isinstance(mystery_label, str)
flag_is_bool = isinstance(mystery_flag, bool)
missing_is_none = mystery_missing is None

assert count_is_int
assert ratio_is_float
assert label_is_str
assert flag_is_bool
assert missing_is_none
print("Task 1 (classify values by type): OK")

# --- Task 2: explicit conversions -----------------------------------------
quantity_text = "17"
unit_price_text = "9.5"
remaining_stock = 0

quantity = int(quantity_text)
unit_price = float(unit_price_text)
remaining_stock_label = str(remaining_stock)
is_in_stock = bool(remaining_stock)

assert quantity == 17
assert unit_price == 9.5
assert remaining_stock_label == "0"
assert not is_in_stock
print("Task 2 (explicit conversions): OK")

# --- Task 3: predict truthiness --------------------------------------------
empty_text = ""
zero_as_text = "0"
zero_as_int = 0
negative_one = -1
nothing = None

empty_text_is_truthy = False
zero_as_text_is_truthy = True
zero_as_int_is_truthy = False
negative_one_is_truthy = True
nothing_is_truthy = False

assert empty_text_is_truthy == bool(empty_text)
assert zero_as_text_is_truthy == bool(zero_as_text)
assert zero_as_int_is_truthy == bool(zero_as_int)
assert negative_one_is_truthy == bool(negative_one)
assert nothing_is_truthy == bool(nothing)
assert not empty_text_is_truthy
assert zero_as_text_is_truthy
assert not zero_as_int_is_truthy
assert negative_one_is_truthy
assert not nothing_is_truthy
print("Task 3 (predict truthiness): OK")

print("\nAll checks passed!")
