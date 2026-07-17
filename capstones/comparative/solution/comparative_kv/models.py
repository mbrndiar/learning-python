"""Frozen domain result records, independent of SQLite rows and JSON envelopes.

The aliases describe the semantic value tree; validation separately narrows
``int`` values to the safe-integer contract.  CLI formatters explicitly map
these models to wire objects so persistence and output representations do not
silently become part of the dataclass API. Freezing is shallow: nested
``JsonValue`` lists and dictionaries remain mutable.
"""

from dataclasses import dataclass
from typing import Literal, TypeAlias

JsonScalar: TypeAlias = None | bool | int | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
SetExpectation: TypeAlias = Literal["any", "absent"] | int
DeleteExpectation: TypeAlias = Literal["any"] | int


@dataclass(frozen=True, slots=True)
class Entry:
    """One normalized live entry returned by the storage boundary."""

    key: str
    value: JsonValue
    revision: int


@dataclass(frozen=True, slots=True)
class SetResult:
    """Committed set outcome, including whether it inserted or replaced."""

    entry: Entry
    created: bool


@dataclass(frozen=True, slots=True)
class DeleteResult:
    """Committed deletion and the global revision consumed by that mutation."""

    key: str
    deleted_revision: int
    revision: int


@dataclass(frozen=True, slots=True)
class ListResult:
    """Deterministically ordered entries plus the current global revision."""

    entries: tuple[Entry, ...]
    global_revision: int
