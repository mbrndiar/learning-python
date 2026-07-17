"""Frozen public result records shared by the CLI and storage boundaries.

Keep these frozen, slotted shapes and field names stable: tests import them
through the package root.  ``JsonValue`` containers represent normalized data;
result records must not expose mutable storage rows or connection state.
Freezing is shallow, so nested JSON lists and dictionaries remain mutable.
"""

from dataclasses import dataclass
from typing import Literal, TypeAlias

JsonScalar: TypeAlias = None | bool | int | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
SetExpectation: TypeAlias = Literal["any", "absent"] | int
DeleteExpectation: TypeAlias = Literal["any"] | int


@dataclass(frozen=True, slots=True)
class Entry:
    """One normalized live entry at its most recent successful set revision."""

    key: str
    value: JsonValue
    revision: int


@dataclass(frozen=True, slots=True)
class SetResult:
    """Committed set result; ``created`` reflects pre-mutation key presence."""

    entry: Entry
    created: bool


@dataclass(frozen=True, slots=True)
class DeleteResult:
    """Committed delete result.

    ``deleted_revision`` is the removed entry's last-set revision; ``revision``
    is the new global commit revision.  They are intentionally distinct.
    """

    key: str
    deleted_revision: int
    revision: int


@dataclass(frozen=True, slots=True)
class ListResult:
    """BINARY-key-ordered entries and the store's current global revision.

    The tuple prevents membership replacement while preserving observed order;
    nested JSON values remain mutable. Entry revisions need not be contiguous or
    match list position.
    """

    entries: tuple[Entry, ...]
    global_revision: int
