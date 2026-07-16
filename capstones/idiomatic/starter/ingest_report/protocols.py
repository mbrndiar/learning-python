"""Injectable boundaries for the idiomatic capstone."""

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from concurrent.futures import Executor
from datetime import datetime
from typing import Protocol

from .models import (
    Event,
    ImportResult,
    RawRecord,
    RejectedRecord,
    Report,
    ReportFilters,
    SourceKind,
)


class RecordSource(Protocol):
    """Yield source records once in deterministic source order."""

    def records(self) -> Iterator[RawRecord]: ...


class EventRepository(Protocol):
    """Persist one streaming import and answer deterministic reports."""

    def import_records(
        self,
        *,
        import_id: str,
        source_kind: SourceKind,
        source_name: str,
        started_at: datetime,
        records: Iterable[Event | RejectedRecord],
        failed_pages: Sequence[int] = (),
    ) -> ImportResult: ...

    def report(self, filters: ReportFilters) -> Report: ...


class Clock(Protocol):
    """Supply timestamps without coupling tests to wall-clock time."""

    def now(self) -> datetime: ...


class PageFetcher(Protocol):
    """Fetch one HTTP page through an injectable transport boundary."""

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]: ...


ExecutorFactory = Callable[[int], Executor]
