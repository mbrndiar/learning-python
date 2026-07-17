"""Import coordination independent of concrete CLI transports."""

from datetime import datetime

from .errors import PartialImportError
from .http_source import fetch_http_records
from .models import ImportResult, SourceKind
from .protocols import (
    Clock,
    EventRepository,
    ExecutorFactory,
    PageFetcher,
    RecordSource,
)
from .validation import normalize_records, validate_import_id


def ingest_source(
    *,
    repository: EventRepository,
    source: RecordSource,
    import_id: str,
    source_kind: SourceKind,
    source_name: str,
    clock: Clock,
) -> ImportResult:
    """Normalize a single-pass source inside one repository import operation.

    Validation stays lazy, so the repository is the terminal consumer and can
    preserve streaming/backpressure rather than materializing the whole source.
    """

    validate_import_id(import_id)
    return repository.import_records(
        import_id=import_id,
        source_kind=source_kind,
        source_name=source_name,
        started_at=clock.now(),
        records=normalize_records(source.records()),
    )


def ingest_http(
    *,
    repository: EventRepository,
    import_id: str,
    base_url: str,
    clock: Clock,
    fetcher: PageFetcher,
    workers: int,
    allow_partial: bool,
    executor_factory: ExecutorFactory,
) -> ImportResult:
    """Fetch pages, commit complete/partial data, then signal partial state.

    In strict mode a page failure escapes before the repository is called. With
    ``allow_partial``, successful pages and the failed-page manifest are committed
    together; only after that commit succeeds does :class:`PartialImportError`
    provide a non-zero process outcome. The injected fetcher, clock, and executor
    factory keep transport, time, and scheduling outside this policy function.
    """

    validate_import_id(import_id)
    fetched = fetch_http_records(
        base_url,
        fetcher,
        workers,
        allow_partial,
        executor_factory,
    )
    result = repository.import_records(
        import_id=import_id,
        source_kind="http",
        source_name=base_url,
        started_at=clock.now(),
        records=normalize_records(fetched.records),
        failed_pages=fetched.failed_pages,
    )
    if fetched.failed_pages:
        # This exception reports a committed result; it is not a rollback signal.
        raise PartialImportError(result)
    return result


class FixedClock:
    """Small reusable clock fake for examples and third-party tests."""

    def __init__(self, value: datetime):
        self.value = value

    def now(self) -> datetime:
        return self.value
