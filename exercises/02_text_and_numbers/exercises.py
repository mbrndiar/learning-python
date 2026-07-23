"""
Exercises: Chapter 2 - Text and Numbers

This file still has no function definitions -- Chapter 5 introduces `def`.
Each task is a top-level script step: replace the initial value marked TODO, then
run this file directly:

    python exercises/02_text_and_numbers/exercises.py

Each task uses an assertion with a focused failure message. Once every task's
assertions pass, the script prints "All checks passed!".
"""

from decimal import Decimal
from fractions import Fraction

# --- Task 1: Celsius to Fahrenheit ----------------------------------------
# Formula: F = C * 9/5 + 32. Convert both readings below.
morning_celsius = 8
afternoon_celsius = 21

# TODO: replace each None with the Fahrenheit conversion of the reading.
morning_fahrenheit = None
afternoon_fahrenheit = None

assert morning_fahrenheit == 46.4, "Task 1: convert morning_celsius"
assert afternoon_fahrenheit == 69.8, "Task 1: convert afternoon_celsius"
print("Task 1 (Celsius to Fahrenheit): OK")

# --- Task 2: palindrome check ----------------------------------------------
# A palindrome reads the same forwards and backwards, case-insensitively.
# Use string slicing (word[::-1]) and .lower(), as shown in the lesson.
candidate_one = "Level"
candidate_two = "Bristol"

# TODO: replace each None with a computed comparison.
candidate_one_is_palindrome = None
candidate_two_is_palindrome = None

assert candidate_one_is_palindrome, "Task 2: Level should be a palindrome"
assert not candidate_two_is_palindrome, "Task 2: Bristol is not a palindrome"
print("Task 2 (palindrome check): OK")

# --- Task 3: UTF-8 round trip ----------------------------------------------
# Encode the text below as UTF-8, then decode those bytes back to text.
original_text = "naïve"

# TODO: replace each None with the requested encode/decode expression.
encoded_bytes = None
decoded_text = None

assert encoded_bytes == b"na\xc3\xafve", "Task 3: encode original_text as UTF-8"
assert decoded_text == original_text, "Task 3: decode encoded_bytes as UTF-8"
print("Task 3 (UTF-8 round trip): OK")

# --- Task 4: exact decimal total -------------------------------------------
# Construct Decimal directly from text -- do not pass through float.
unit_price_text = "4.25"
quantity = 6

# TODO: replace None with the Decimal total (unit price * quantity).
order_total = None

assert order_total == Decimal("25.50"), (
    "Task 4: build Decimal(unit_price_text) and multiply by quantity"
)
print("Task 4 (exact decimal total): OK")

# --- Task 5: exact fraction addition ---------------------------------------
# Parse both strings as Fraction and add them exactly.
left_fraction_text = "2/3"
right_fraction_text = "1/6"

# TODO: replace None with the Fraction sum.
fraction_sum = None

assert fraction_sum == Fraction(5, 6), "Task 5: construct and add both Fraction values"
print("Task 5 (exact fraction addition): OK")

# --- Task 6: formatted receipt line ----------------------------------------
# Build one line for a two-column receipt: the item name left-aligned in a
# 12-character field, then the price right-aligned in an 8-character field
# with 2 decimal places, using a single f-string.
item_name = "Notebook"
item_price = 3.5

# TODO: replace None with an f-string using format specifiers, for example
# f"{item_name:<12}{item_price:>8.2f}".
receipt_line = None

assert receipt_line == "Notebook        3.50", (
    "Task 6: use widths 12 and 8 with two decimal places"
)
assert len(receipt_line) == 20
print("Task 6 (formatted receipt line): OK")

print("\nAll checks passed!")
