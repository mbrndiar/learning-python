"""Curated public boundary; implementation-only normalization helpers stay private."""

from .cli import build_parser, main
from .domain import (
    MAX_CONTAINER_DEPTH,
    MAX_SAFE_INTEGER,
    MAX_VALUE_BYTES,
    normalized_json,
    parse_delete_expectation,
    parse_json_value,
    parse_set_expectation,
    validate_key,
)
from .errors import IncompleteImplementationError, KvError
from .models import (
    DeleteExpectation,
    DeleteResult,
    Entry,
    JsonValue,
    ListResult,
    SetExpectation,
    SetResult,
)
from .store import Store, open_store

__all__ = [
    "DeleteExpectation",
    "DeleteResult",
    "Entry",
    "IncompleteImplementationError",
    "JsonValue",
    "KvError",
    "ListResult",
    "MAX_CONTAINER_DEPTH",
    "MAX_SAFE_INTEGER",
    "MAX_VALUE_BYTES",
    "SetExpectation",
    "SetResult",
    "Store",
    "build_parser",
    "main",
    "normalized_json",
    "open_store",
    "parse_delete_expectation",
    "parse_json_value",
    "parse_set_expectation",
    "validate_key",
]
