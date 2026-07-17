"""Injectable boundaries for the idiomatic capstone.

Keep these protocols structural and minimal: tests provide one-shot sources,
fixed clocks, fake repositories/fetchers, and observable executor factories.
Strict typing should describe capabilities without forcing callers to inherit
from concrete adapters.
"""

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
    """Yield source records once in deterministic source order.

    Implementations own their file handles. Consumers must preserve one-pass
    iteration and explicitly close a partially consumed closeable iterator.
    """

    def records(self) -> Iterator[RawRecord]: ...


class EventRepository(Protocol):
    """Persist one streaming import and answer deterministic reports.

    ``import_records`` owns the transaction while pulling the iterable: accepted
    events, rejects, counts, failed pages, and metadata succeed or roll back
    together.  ``report`` combines inclusive filters and returns explicitly
    ordered groups.
    """

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
    """Fetch one untrusted JSON mapping through an injectable transport boundary.

    The concrete adapter validates transport and body bounds. The coordinator
    validates page metadata/items and owns pagination order, worker bounds, and
    cancellation.
    """

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]: ...


# The coordinator owns every executor returned here, including its cleanup after
# strict failure or cancellation; injection does not control thread scheduling.
ExecutorFactory = Callable[[int], Executor]
