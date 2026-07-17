"""Milestone 3 starter: versioned, transactional SQLite persistence.

The repository owns schema validation, transaction lifetime, first-event
identity, and deterministic aggregate queries.  Initialize only a genuinely
empty database and fail closed on newer, incomplete, or corrupt state; recovery
must never destroy user data.
"""

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
    """Persist imports without destructive recovery or mutable event commands.

    Treat ``(source, id)`` as an insert-once identity across every import.
    Reopening the same database must preserve that first event and all schema
    checks.
    """

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        # TODO(m3): distinguish a genuinely empty database from unsupported or
        # corrupt state; the schema/version tests require non-destructive failure.

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
        """Commit accepted events, rejects, counts, and metadata atomically.

        Own one transaction around incremental iterable consumption.  A reused
        import id or any mid-stream exception must leave no rows from that
        attempt; duplicate event identities increment metadata but never mutate
        the first stored event.  Keep all untrusted values parameterized.
        """

        # TODO(m3): let the transaction encompass stream consumption and final
        # metadata so rollback covers events, rejects, and counts together.
        incomplete(f"milestone 3 import into {self.database_path}")

    def report(self, filters: ReportFilters) -> Report:
        """Return deterministic parameterized aggregate queries.

        Combine optional event predicates with AND and inclusive time bounds.
        Reject summaries remain unfiltered, invalid ranges fail before querying,
        and every grouped result has explicit Unicode-stable ordering independent
        of insertion order.
        """

        # TODO(m3): use the filter, empty-report, hostile-value, and ordering tests
        # as separate invariants rather than one happy-path report.
        incomplete(f"milestone 3 report from {self.database_path}")
