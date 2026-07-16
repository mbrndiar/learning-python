"""Immutable public values for the comparative key/value store."""

from dataclasses import dataclass
from typing import Literal, TypeAlias

JsonScalar: TypeAlias = None | bool | int | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
SetExpectation: TypeAlias = Literal["any", "absent"] | int
DeleteExpectation: TypeAlias = Literal["any"] | int


@dataclass(frozen=True, slots=True)
class Entry:
    """One normalized live entry."""

    key: str
    value: JsonValue
    revision: int


@dataclass(frozen=True, slots=True)
class SetResult:
    """Result returned after a committed set operation."""

    entry: Entry
    created: bool


@dataclass(frozen=True, slots=True)
class DeleteResult:
    """Result returned after a committed delete operation."""

    key: str
    deleted_revision: int
    revision: int


@dataclass(frozen=True, slots=True)
class ListResult:
    """Ordered entries and the current global revision."""

    entries: tuple[Entry, ...]
    global_revision: int
