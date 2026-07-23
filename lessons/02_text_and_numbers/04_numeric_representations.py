"""
Chapter 2, Lesson 4: Numeric Representations

Purpose: compare int, float, Decimal, Fraction, and complex, and explain
which accuracy/interoperability trade-off each one makes.

Prerequisites: 03_unicode_text_and_bytes.py.

This lesson uses `import` before Chapter 6 formally teaches modules. That is
a deliberate, bounded preview: `import name` makes the standard-library
module `name` available under that name, and `from module import thing`
brings just `thing` into this file. The full mechanics of modules, the
import system, and packages are taught in the Modules and Files chapter;
here, only "this makes Decimal/Fraction/math available" matters.

Read this file top to bottom, predict each output, then run it:

    python lessons/02_text_and_numbers/04_numeric_representations.py
"""

import math
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

# Step 1: float is fast, approximate binary floating point. Most decimal
# fractions, including 0.1, cannot be stored exactly in that binary format.
float_total = 0.1 + 0.2
print("0.1 + 0.2 as float:", float_total)
print("equal to 0.3:", float_total == 0.3)
print("close to 0.3:", math.isclose(float_total, 0.3))
assert float_total != 0.3
assert math.isclose(float_total, 0.3)

# Step 2: Decimal offers configurable decimal arithmetic. Construct it from
# text when the source is decimal text -- constructing it from a float
# instead preserves that float's existing binary approximation, not the
# human-written decimal value.
decimal_tenth = Decimal("0.1")
decimal_total = decimal_tenth + decimal_tenth + decimal_tenth
decimal_from_float = Decimal(0.1)
print("\nDecimal sum:", decimal_total)
print(
    "Decimal from float equals Decimal from text:", decimal_from_float == decimal_tenth
)
assert decimal_total == Decimal("0.3")
assert decimal_from_float != decimal_tenth

# Monetary code must still choose an explicit rounding rule -- Decimal does
# not supply one universal policy. Context-managed precision is intentionally
# deferred until the course teaches context managers.
taxed_price = Decimal("19.99") * Decimal("1.20")
display_price = taxed_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print("price rounded to cents:", display_price)
assert display_price == Decimal("23.99")

# Step 3: Fraction stores exact rational values -- useful for ratios and
# probabilities. Building it from a float instead of an int/string captures
# that float's approximation, not the "nice" fraction a human might expect.
one_third = Fraction(1, 3)
fraction_total = one_third + one_third + one_third
fraction_from_text = Fraction("0.1")
fraction_from_float = Fraction(0.1)
print("\nthree exact thirds:", fraction_total)
print("Fraction from text:", fraction_from_text)
print("Fraction from float:", fraction_from_float)
assert fraction_total == 1
assert fraction_from_text == Fraction(1, 10)
assert fraction_from_float != Fraction(1, 10)

# Step 4: complex models real and imaginary components as floats, so it
# inherits float's precision limits. It has equality but no natural
# ordering.
impedance = 3 + 4j
print("\ncomplex value:", impedance)
print("magnitude:", abs(impedance))
assert abs(impedance) == 5.0

# `impedance < 5 + 0j` would raise TypeError because complex numbers have no
# natural ordering. The expression remains commented until exception handling
# is taught.

# --- One-variable experiment -------------------------------------------
# Change `one_third` to Fraction(1, 4) and predict fraction_total (the sum
# of three of them) before rerunning -- it will no longer equal exactly 1.
