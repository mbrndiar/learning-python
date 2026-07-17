"""Milestones 3-5 storage boundary.

Progress in observable layers: open/configure a literal local path; classify
and initialize, migrate, or validate storage; add atomic reads and mutations;
then prove the same rules under independent-process contention.  The spec fixes
outcomes and invariants, not helper layout or SQL construction strategy.
"""

from pathlib import Path
from typing import Protocol

from .errors import incomplete
from .models import (
    DeleteExpectation,
    DeleteResult,
    Entry,
    JsonValue,
    ListResult,
    SetExpectation,
    SetResult,
)


class Store(Protocol):
    """Operations required by the command boundary.

    Implementations own their connection and return frozen public records.
    Freezing is shallow for nested JSON containers. Callers must close the store
    on every success and failure path.
    """

    # Set CAS and revision allocation must occur under the same write reservation.
    # Even a semantically unchanged value consumes one revision after commit.
    def set(
        self,
        key: str,
        value: JsonValue,
        expectation: SetExpectation = "any",
    ) -> SetResult: ...

    def get(self, key: str) -> Entry: ...

    # Missing delete is not_found before exact-expectation or exhaustion checks;
    # success consumes one global revision and leaves no tombstone.
    def delete(
        self,
        key: str,
        expectation: DeleteExpectation = "any",
    ) -> DeleteResult: ...

    # Return one coherent snapshot in ascending SQLite BINARY key order.
    def list_entries(self) -> ListResult: ...

    def close(self) -> None: ...


def open_store(path: str | Path) -> Store:
    """Open one conforming store while preserving all existing-data invariants.

    The milestone 3-5 specification and tests define observable initialization,
    migration, mutation, contention, failure, and cleanup outcomes. Choose an
    internal design that never repairs unknown state or exposes partial results.
    """

    incomplete(f"comparative SQLite storage for {Path(path)}")
