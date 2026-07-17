"""Validate keys/expectations and normalize restricted JSON without losing lexemes.

The standard decoder builds useful Python values, but normalization also needs
facts that ordinary decoding discards: number spelling, duplicate members, and
insignificant whitespace.  This module therefore preserves lexical evidence
first, then constructs the contract's semantic value.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import cast

from .errors import fail
from .models import DeleteExpectation, JsonValue, SetExpectation

# Python integers are arbitrary precision; this is the conventional binary64
# safe-integer maximum, within which integer values cannot alias another integer.
MAX_SAFE_INTEGER = 9_007_199_254_740_991
MAX_VALUE_BYTES = 65_536
MAX_CONTAINER_DEPTH = 32
_SAFE_INTEGER_DIGITS = len(str(MAX_SAFE_INTEGER))
_EXPONENT_SATURATION = MAX_VALUE_BYTES + _SAFE_INTEGER_DIGITS
KEY_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}\Z")
# Encode the JSON number grammar directly: zero has no leading peers, and a
# present fraction or exponent must contain at least one decimal digit.
NUMBER_PATTERN = re.compile(
    r"(?P<sign>-?)(?P<integer>0|[1-9][0-9]*)"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?:[eE](?P<exponent>[+-]?[0-9]+))?\Z"
)


@dataclass(frozen=True, slots=True)
class _RawNumber:
    """Keep a JSON number token intact until exact-decimal validation."""

    token: str


@dataclass(frozen=True, slots=True)
class _RawObject:
    """Keep source-order pairs because a dict would erase duplicate members."""

    pairs: list[tuple[str, object]]


@dataclass(slots=True)
class _Metadata:
    """Lexical properties that normalized Python values cannot represent."""

    whitespace: bool = False
    duplicate: bool = False
    noncanonical_number: bool = False


def validate_key(value: str) -> str:
    """Validate and return one opaque ASCII key."""

    if KEY_PATTERN.fullmatch(value) is None:
        fail("invalid_argument", {"field": "key", "reason": "format"}, 2)
    return value


def parse_set_expectation(value: str) -> SetExpectation:
    """Parse a set expectation without accepting alternate spellings."""

    if value in ("any", "absent"):
        return cast(SetExpectation, value)
    return _parse_revision(value)


def parse_delete_expectation(value: str) -> DeleteExpectation:
    """Parse a delete expectation without accepting ``absent``."""

    if value == "any":
        return "any"
    return _parse_revision(value)


def _parse_revision(value: str) -> int:
    if re.fullmatch(r"[1-9][0-9]*", value) is None:
        fail("invalid_argument", {"field": "expect", "reason": "format"}, 2)
    try:
        revision = int(value)
    except ValueError:
        fail("invalid_argument", {"field": "expect", "reason": "format"}, 2)
    if revision > MAX_SAFE_INTEGER:
        fail("invalid_argument", {"field": "expect", "reason": "format"}, 2)
    return revision


def parse_json_value(text: str) -> JsonValue:
    """Parse and normalize one command-line restricted JSON value."""

    return _parse_json(text, require_normalized=False)


def parse_stored_json(text: str) -> JsonValue:
    """Parse one stored value and require normalized persistence form."""

    return _parse_json(text, require_normalized=True)


def normalized_json(value: JsonValue) -> str:
    """Serialize a normalized value compactly for SQLite.

    The contract has no canonical object-member order, so keys are intentionally
    not sorted.  Python's retained insertion order nevertheless keeps this
    implementation's traversal deterministic.
    """

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )


def _parse_json(text: str, *, require_normalized: bool) -> JsonValue:
    if len(text.encode("utf-8", errors="surrogatepass")) > MAX_VALUE_BYTES:
        fail("invalid_value", {"reason": "byte_limit"}, 2)

    # This pass records formatting only. Syntax must be established by the JSON
    # decoder before valid-tree checks such as container depth can take effect.
    # Decoder hooks retain number tokens and object pairs instead of prematurely
    # converting or deduplicating them.
    metadata = _Metadata(whitespace=_scan_json(text))
    try:
        raw = json.loads(
            text,
            parse_int=_RawNumber,
            parse_float=_RawNumber,
            parse_constant=_reject_constant,
            object_pairs_hook=_raw_object,
        )
    except json.JSONDecodeError:
        fail("invalid_json", {"reason": "syntax"}, 2)
    except RecursionError:
        fail("invalid_value", {"reason": "depth_limit"}, 2)

    value = _normalize(raw, 0, metadata)
    if require_normalized and (
        metadata.whitespace or metadata.duplicate or metadata.noncanonical_number
    ):
        fail("invalid_value", {"reason": "not_normalized"}, 2)
    return value


def _reject_constant(_token: str) -> object:
    fail("invalid_json", {"reason": "syntax"}, 2)


def _raw_object(pairs: list[tuple[str, object]]) -> _RawObject:
    return _RawObject(pairs)


def _scan_json(text: str) -> bool:
    """Record outside-string whitespace without validating JSON structure.

    It understands only enough string escaping to ignore whitespace inside
    strings; ``json.loads`` remains responsible for the complete RFC 8259 grammar.
    """

    in_string = False
    escaped = False
    whitespace = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character in " \t\r\n":
            whitespace = True
    return whitespace


def _normalize(raw: object, depth: int, metadata: _Metadata) -> JsonValue:
    if raw is None or isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return _normalize_string(raw)
    if isinstance(raw, _RawNumber):
        integer = _normalize_number(raw.token)
        if raw.token != str(integer):
            metadata.noncanonical_number = True
        return integer
    if isinstance(raw, list):
        next_depth = _next_depth(depth)
        return [_normalize(item, next_depth, metadata) for item in raw]
    if isinstance(raw, _RawObject):
        next_depth = _next_depth(depth)
        # Compare names as Unicode scalar sequences before collapsing them.
        # Iterating again in source order leaves each last-winning member at its
        # source position, which also defines deterministic validation order.
        scalar_names = [_scalar_key(name) for name, _ in raw.pairs]
        last_indices: dict[str, int] = {}
        for index, name in enumerate(scalar_names):
            if name in last_indices:
                metadata.duplicate = True
            last_indices[name] = index
        result: dict[str, JsonValue] = {}
        for index, ((name, item), scalar_name) in enumerate(
            zip(raw.pairs, scalar_names, strict=True)
        ):
            if last_indices[scalar_name] != index:
                continue
            normalized_name = _normalize_string(name)
            result[normalized_name] = _normalize(item, next_depth, metadata)
        return result
    fail("invalid_json", {"reason": "syntax"}, 2)


def _next_depth(depth: int) -> int:
    next_depth = depth + 1
    if next_depth > MAX_CONTAINER_DEPTH:
        fail("invalid_value", {"reason": "depth_limit"}, 2)
    return next_depth


def _scalar_key(value: str) -> str:
    """Map UTF-16 surrogate pairs to their supplementary Unicode scalar.

    Some runtimes can expose strings as surrogate code units.  Combining a
    valid high/low pair makes duplicate-name comparison independent of that
    representation; lone units remain visible so validation can reject them.
    No Unicode normalization or case folding is performed.
    """

    output: list[str] = []
    index = 0
    while index < len(value):
        code = ord(value[index])
        if 0xD800 <= code <= 0xDBFF and index + 1 < len(value):
            low = ord(value[index + 1])
            if 0xDC00 <= low <= 0xDFFF:
                scalar = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                output.append(chr(scalar))
                index += 2
                continue
        output.append(value[index])
        index += 1
    return "".join(output)


def _normalize_string(value: str) -> str:
    normalized = _scalar_key(value)
    if any(0xD800 <= ord(character) <= 0xDFFF for character in normalized):
        fail("invalid_value", {"reason": "unpaired_surrogate"}, 2)
    return normalized


def _normalize_number(token: str) -> int:
    # Binary64 conversion is used only for the contract's finiteness check.
    # Exact integrality and magnitude below are derived from decimal digits, so
    # values near the safe-integer boundary never inherit float rounding.
    try:
        binary64 = float(token)
    except ValueError:
        fail("invalid_json", {"reason": "syntax"}, 2)
    if not math.isfinite(binary64):
        fail("invalid_value", {"reason": "non_finite_number"}, 2)

    match = NUMBER_PATTERN.fullmatch(token)
    if match is None:
        fail("invalid_json", {"reason": "syntax"}, 2)
    integer_part = match.group("integer")
    fraction = match.group("fraction") or ""
    digits = integer_part + fraction
    if all(character == "0" for character in digits):
        return 0

    exponent = _saturating_exponent(match.group("exponent") or "0")
    scale = len(fraction) - exponent
    if scale <= 0:
        zero_count = -scale
        magnitude = digits.lstrip("0")
        if len(magnitude) + zero_count > 16:
            fail("invalid_value", {"reason": "number_out_of_range"}, 2)
        integer_digits = digits + ("0" * zero_count)
    else:
        if scale >= len(digits):
            fail("invalid_value", {"reason": "non_integral_number"}, 2)
        suffix = digits[-scale:]
        if any(character != "0" for character in suffix):
            fail("invalid_value", {"reason": "non_integral_number"}, 2)
        integer_digits = digits[:-scale]

    magnitude_text = integer_digits.lstrip("0") or "0"
    # Compare decimal magnitude by length and then lexicographically.  Equal-
    # length digit strings have numeric ordering, and rejecting first avoids
    # constructing a huge Python integer (including its digit-limit concerns).
    if len(magnitude_text) > 16 or (
        len(magnitude_text) == 16 and magnitude_text > "9007199254740991"
    ):
        fail("invalid_value", {"reason": "number_out_of_range"}, 2)
    magnitude = int(magnitude_text)
    return -magnitude if match.group("sign") == "-" else magnitude


def _saturating_exponent(text: str) -> int:
    """Parse an exponent into a bounded magnitude for later scale arithmetic.

    Bounded digit-by-digit parsing avoids constructing an integer from attacker-
    sized exponent text. An accepted token has at most ``MAX_VALUE_BYTES`` decimal
    digits; beyond that count plus the 16 safe-integer digits, any nonzero result
    is already provably out of range or non-integral, so saturation is sufficient.
    """

    negative = text.startswith("-")
    digits = text[1:] if text[:1] in ("+", "-") else text
    value = 0
    for character in digits:
        value = min(
            _EXPONENT_SATURATION,
            value * 10 + ord(character) - ord("0"),
        )
    return -value if negative else value
