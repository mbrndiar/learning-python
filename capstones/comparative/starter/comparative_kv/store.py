"""Storage boundary for the comparative key/value store."""

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
    """Operations required by the command boundary."""

    def set(
        self,
        key: str,
        value: JsonValue,
        expectation: SetExpectation = "any",
    ) -> SetResult: ...

    def get(self, key: str) -> Entry: ...

    def delete(
        self,
        key: str,
        expectation: DeleteExpectation = "any",
    ) -> DeleteResult: ...

    def list_entries(self) -> ListResult: ...


def open_store(path: str | Path) -> Store:
    """Open the selected SQLite store once persistence is implemented."""

    incomplete(f"comparative SQLite storage for {Path(path)}")
