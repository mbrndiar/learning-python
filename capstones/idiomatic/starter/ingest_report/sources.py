"""Milestone 2 starter: streaming CSV and JSON Lines sources."""

from collections.abc import Iterator
from pathlib import Path

from .errors import incomplete
from .models import RawRecord


class CSVSource:
    """Own and stream the exact documented UTF-8 CSV dialect."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        """Yield one-based data rows and close the file on every exit."""

        # TODO(m2): validate the exact header and translate I/O/content failures.
        incomplete("milestone 2 CSV source")


class JSONLinesSource:
    """Own and stream non-blank physical UTF-8 JSON Lines records."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        """Yield physical line numbers and detect duplicate object members."""

        # TODO(m2): use object_pairs_hook so duplicate JSON names remain visible.
        incomplete("milestone 2 JSON Lines source")
