"""
Solutions: Chapter 2 - Text and Numbers

Reference implementation for exercises/02_text_and_numbers/exercises.py.
Try to solve the exercises yourself before checking this file!
"""

from decimal import Decimal
from fractions import Fraction

# --- Task 1: Celsius to Fahrenheit ----------------------------------------
morning_celsius = 8
afternoon_celsius = 21

morning_fahrenheit = morning_celsius * 9 / 5 + 32
afternoon_fahrenheit = afternoon_celsius * 9 / 5 + 32

assert morning_fahrenheit == 46.4
assert afternoon_fahrenheit == 69.8
print("Task 1 (Celsius to Fahrenheit): OK")

# --- Task 2: palindrome check ----------------------------------------------
candidate_one = "Level"
candidate_two = "Bristol"

candidate_one_is_palindrome = candidate_one.lower() == candidate_one.lower()[::-1]
candidate_two_is_palindrome = candidate_two.lower() == candidate_two.lower()[::-1]

assert candidate_one_is_palindrome is True
assert candidate_two_is_palindrome is False
print("Task 2 (palindrome check): OK")

# --- Task 3: UTF-8 round trip ----------------------------------------------
original_text = "naïve"

encoded_bytes = original_text.encode("utf-8")
decoded_text = encoded_bytes.decode("utf-8")

assert encoded_bytes == b"na\xc3\xafve"
assert decoded_text == original_text
print("Task 3 (UTF-8 round trip): OK")

# --- Task 4: exact decimal total -------------------------------------------
unit_price_text = "4.25"
quantity = 6

order_total = Decimal(unit_price_text) * quantity

assert order_total == Decimal("25.50")
print("Task 4 (exact decimal total): OK")

# --- Task 5: exact fraction addition ---------------------------------------
left_fraction_text = "2/3"
right_fraction_text = "1/6"

fraction_sum = Fraction(left_fraction_text) + Fraction(right_fraction_text)

assert fraction_sum == Fraction(5, 6)
print("Task 5 (exact fraction addition): OK")

# --- Task 6: formatted receipt line ----------------------------------------
item_name = "Notebook"
item_price = 3.5

receipt_line = f"{item_name:<12}{item_price:>8.2f}"

assert receipt_line == "Notebook        3.50"
assert len(receipt_line) == 20
print("Task 6 (formatted receipt line): OK")

print("\nAll checks passed!")
