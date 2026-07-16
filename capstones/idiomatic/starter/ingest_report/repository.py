"""Milestone 3 starter: versioned, transactional SQLite persistence."""

from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path

from .errors import incomplete
from .models import (
    Event,
    ImportResult,
    RejectedRecord,
    Report,
    ReportFilters,
    SourceKind,
)


class SQLiteEventRepository:
    """Persist imports without destructive recovery or mutable event commands."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        # TODO(m3): initialize only a genuinely empty database; validate all others.

    def import_records(
        self,
        *,
        import_id: str,
        source_kind: SourceKind,
        source_name: str,
        started_at: datetime,
        records: Iterable[Event | RejectedRecord],
        failed_pages: Sequence[int] = (),
    ) -> ImportResult:
        """Commit accepted events, rejects, counts, and metadata atomically."""

        # TODO(m3): stream records inside one rollback-safe transaction.
        incomplete(f"milestone 3 import into {self.database_path}")

    def report(self, filters: ReportFilters) -> Report:
        """Return deterministic parameterized aggregate queries."""

        # TODO(m3): combine optional filters with AND and inclusive bounds.
        incomplete(f"milestone 3 report from {self.database_path}")
