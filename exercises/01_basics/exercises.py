"""
Exercises: 01 Basics

Implement each function below, then run this file directly to check
your work:

    python exercises/01_basics/exercises.py
"""

from decimal import Decimal
from fractions import Fraction


def celsius_to_fahrenheit(celsius):
    """Convert a Celsius temperature to Fahrenheit.

    Formula: F = C * 9/5 + 32
    """
    # TODO: implement this function
    raise NotImplementedError


def is_palindrome(text):
    """Return True if `text` reads the same forwards and backwards.

    Comparison should be case-insensitive, e.g. "Racecar" -> True.
    """
    # TODO: implement this function
    raise NotImplementedError


def count_vowels(text):
    """Return the number of vowels (a, e, i, o, u) in `text`,
    case-insensitive."""
    # TODO: implement this function
    raise NotImplementedError


def convert_values(
    integer_text: str, decimal_text: str, value: object
) -> tuple[int, float, str, bool]:
    """Return explicit int, float, str, and bool conversions.

    Return ``(int(integer_text), float(decimal_text), str(value), bool(value))``.
    Let invalid numeric text raise ValueError. Remember that bool tests
    truthiness; it does not parse words such as "False".
    """
    # TODO: perform each conversion explicitly.
    raise NotImplementedError


def utf8_round_trip(text: str) -> tuple[bytes, str]:
    """Encode text as UTF-8 and decode those bytes back to text.

    Return the encoded bytes and decoded text as a pair.
    """
    # TODO: use explicit UTF-8 encode and decode operations.
    raise NotImplementedError


def mutate_byte(data: bytes, index: int, replacement: int) -> bytes:
    """Return bytes with one byte replaced, leaving ``data`` unchanged.

    Convert to bytearray, assign ``replacement`` at ``index``, then convert the
    result back to bytes. Normal IndexError and ValueError behavior should be
    preserved for an invalid index or a replacement outside 0..255.
    """
    # TODO: use bytearray for the mutation.
    raise NotImplementedError


def decimal_total(unit_price: str, quantity: int) -> Decimal:
    """Return an exact decimal unit price multiplied by ``quantity``.

    Construct Decimal directly from ``unit_price`` text; do not pass through
    float, which would import a binary floating-point approximation.
    """
    # TODO: construct and multiply a Decimal.
    raise NotImplementedError


def add_fractions(left: str, right: str) -> Fraction:
    """Parse and exactly add two rational strings such as "1/3" and "1/6"."""
    # TODO: construct Fraction values from both strings.
    raise NotImplementedError


if __name__ == "__main__":
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    print("celsius_to_fahrenheit: OK")

    assert is_palindrome("Racecar") is True
    assert is_palindrome("hello") is False
    print("is_palindrome: OK")

    assert count_vowels("Hello World") == 3
    assert count_vowels("PYTHON") == 1
    print("count_vowels: OK")

    assert convert_values("42", "3.5", []) == (42, 3.5, "[]", False)
    assert convert_values("7", "2.25", "False") == (7, 2.25, "False", True)
    try:
        convert_values("3.5", "2.0", None)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid integer text should raise ValueError")
    print("convert_values: OK")

    encoded, decoded = utf8_round_trip("café ☕")
    assert encoded == b"caf\xc3\xa9 \xe2\x98\x95"
    assert decoded == "café ☕"
    print("utf8_round_trip: OK")

    original = b"cat"
    assert mutate_byte(original, 0, ord("h")) == b"hat"
    assert original == b"cat"
    try:
        mutate_byte(b"A", 0, 256)
    except ValueError:
        pass
    else:
        raise AssertionError("a byte value outside 0..255 should raise ValueError")
    print("mutate_byte: OK")

    assert decimal_total("0.10", 3) == Decimal("0.30")
    assert decimal_total("19.99", 2) == Decimal("39.98")
    print("decimal_total: OK")

    assert add_fractions("1/3", "1/6") == Fraction(1, 2)
    assert add_fractions("3/4", "5/8") == Fraction(11, 8)
    print("add_fractions: OK")

    print("\nAll checks passed!")
