"""
Solutions: Numeric and Binary Basic Types

Reference implementations for the companion ``exercises.py``. Run this file
directly to execute deterministic checks for every exercise.
"""

from decimal import Decimal
from fractions import Fraction


def convert_values(
    integer_text: str, decimal_text: str, value: object
) -> tuple[int, float, str, bool]:
    """Return explicit int, float, str, and bool conversions."""
    return int(integer_text), float(decimal_text), str(value), bool(value)


def utf8_round_trip(text: str) -> tuple[bytes, str]:
    """Encode text as UTF-8 and decode those bytes back to text."""
    encoded = text.encode("utf-8")
    return encoded, encoded.decode("utf-8")


def mutate_byte(data: bytes, index: int, replacement: int) -> bytes:
    """Return bytes with one byte replaced, leaving ``data`` unchanged."""
    mutable = bytearray(data)
    mutable[index] = replacement
    return bytes(mutable)


def decimal_total(unit_price: str, quantity: int) -> Decimal:
    """Return an exact decimal unit price multiplied by ``quantity``."""
    return Decimal(unit_price) * quantity


def add_fractions(left: str, right: str) -> Fraction:
    """Parse and exactly add two rational strings."""
    return Fraction(left) + Fraction(right)


if __name__ == "__main__":
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
