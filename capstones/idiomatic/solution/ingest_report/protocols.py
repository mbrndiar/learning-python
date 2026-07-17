"""Structural DI boundaries that keep orchestration independent of adapters."""

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
    """Create a single-pass iterator in deterministic source order.

    Consumers must not count and then replay the returned iterator. The iterator
    may also own a file or other resource until it is exhausted or closed.
    """

    def records(self) -> Iterator[RawRecord]: ...


class EventRepository(Protocol):
    """Persist one streaming import and answer deterministic reports.

    Accepting ``Iterable`` avoids coupling storage to a concrete generator type,
    but ``records`` may still be lazy and single-pass. Implementations consume it
    synchronously inside the import operation rather than retaining or rewinding it.
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
    """Inject import time so orchestration need not read ambient wall-clock state."""

    def now(self) -> datetime: ...


class PageFetcher(Protocol):
    """Fetch one untrusted page through an injectable transport boundary.

    The seam substitutes transport in tests; callers still validate the returned
    mapping because dependency injection is not a trust boundary.
    """

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]: ...


# Injecting construction lets tests control or observe executor choice and
# lifecycle; it does not make thread scheduling deterministic. The component
# calling the factory owns shutdown of the returned executor.
ExecutorFactory = Callable[[int], Executor]
