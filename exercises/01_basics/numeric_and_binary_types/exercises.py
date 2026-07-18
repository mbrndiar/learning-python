"""
Exercises: Numeric and Binary Basic Types

Implement each function, then compare your work with ``solutions.py``. These
exercises keep text/binary boundaries and exact-number construction explicit.

Compile this starter at any time with:

    python -m py_compile exercises/01_basics/numeric_and_binary_types/exercises.py
"""

from decimal import Decimal
from fractions import Fraction


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
