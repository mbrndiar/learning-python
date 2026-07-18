"""
Lesson 1.6: Numeric Types and Explicit Conversions

Python's numeric types make different trade-offs. ``float`` is fast,
approximate binary floating point; ``Decimal`` offers controlled decimal
arithmetic; ``Fraction`` stores exact rational values; and ``complex`` models
numbers with real and imaginary components. Choosing a type should follow the
problem's accuracy and interoperability requirements, not just its syntax.
"""

import cmath
import math
from decimal import ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction

# Most decimal fractions cannot be stored exactly as finite binary fractions.
# float is still appropriate for measurements, simulations, graphics, and
# other work where small representation errors are acceptable.
float_total = 0.1 + 0.2
print("0.1 + 0.2 as float:", repr(float_total))
print("equal to 0.3:", float_total == 0.3)
print("close to 0.3:", math.isclose(float_total, 0.3))
assert float_total != 0.3
assert math.isclose(float_total, 0.3)

numerator, denominator = (0.1).as_integer_ratio()
print("exact ratio stored for 0.1:", numerator, "/", denominator)
assert numerator / denominator == 0.1

# Construct Decimal from text when the source value is decimal text. Passing a
# float preserves that float's exact binary approximation rather than the
# human-written decimal value that originally produced it.
decimal_tenth = Decimal("0.1")
decimal_total = decimal_tenth + decimal_tenth + decimal_tenth
decimal_from_float = Decimal(0.1)

print("Decimal sum:", decimal_total)
print(
    "Decimal from float equals Decimal from text:",
    decimal_from_float == decimal_tenth,
)
assert decimal_total == Decimal("0.3")
assert decimal_from_float != decimal_tenth

# Decimal arithmetic has a configurable finite context, so operations such as
# division can still round. Monetary code must also choose an explicit scale
# and rounding rule rather than assuming Decimal supplies a universal policy.
with localcontext() as context:
    context.prec = 6
    rounded_seventh = Decimal(1) / Decimal(7)

taxed_price = Decimal("19.99") * Decimal("1.20")
display_price = taxed_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print("1 / 7 with Decimal precision 6:", rounded_seventh)
print("price rounded to cents:", display_price)
assert rounded_seventh == Decimal("0.142857")
assert display_price == Decimal("23.99")

# Fraction is exact for rational quantities such as ratios and probabilities.
# Build it from integers, decimal text, or another exact value. Constructing it
# from a float instead captures the float approximation, and large numerators
# and denominators can make repeated rational arithmetic expensive.
one_third = Fraction(1, 3)
fraction_total = one_third + one_third + one_third
fraction_from_text = Fraction("0.1")
fraction_from_float = Fraction(0.1)

print("three exact thirds:", fraction_total)
print("Fraction from text:", fraction_from_text)
print("Fraction from float:", fraction_from_float)
assert fraction_total == 1
assert fraction_from_text == Fraction(1, 10)
assert fraction_from_float != Fraction(1, 10)

# complex is useful for electrical, signal-processing, and mathematical work.
# Its real and imaginary parts are floats, so it inherits float's precision
# limits. Complex values have equality but no natural ordering; use cmath for
# functions whose inputs or results may be complex.
impedance = 3 + 4j
print("complex value:", impedance)
print("magnitude:", abs(impedance))
print("square root of -1:", cmath.sqrt(-1))
assert abs(impedance) == 5.0
assert cmath.sqrt(-1) == 1j

try:
    impedance < 5 + 0j
except TypeError as error:
    print("complex ordering:", type(error).__name__)

# Constructors make conversions explicit. int() truncates a float toward zero,
# while bool() tests truthiness rather than parsing words: every non-empty str,
# including "False", is true.
whole_number = int("42")
measurement = float("3.5")
label = str(123)
truncated = int(-3.9)

print("converted values:", whole_number, measurement, label, truncated)
print("truth values:", bool("False"), bool(""))
assert (whole_number, measurement, label, truncated) == (42, 3.5, "123", -3)
assert bool("False") is True
assert bool("") is False

# Numeric text must match the constructor's grammar. Conversion failures raise
# ValueError, so validate input or handle that exception at an input boundary.
for converter, value in ((int, "3.5"), (float, "not-a-number")):
    try:
        converter(value)
    except ValueError as error:
        print(f"{converter.__name__}({value!r}):", type(error).__name__)
