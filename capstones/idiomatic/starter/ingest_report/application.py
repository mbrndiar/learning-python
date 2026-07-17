"""Milestone 2/5 starter: dependency-injected, streaming import coordination.

Keep policy here and resource/transaction ownership in the adapters that create
those resources.  The milestone tests probe incremental consumption, cleanup,
and the observable difference between strict and partial HTTP imports.
"""

from .errors import incomplete
from .models import ImportResult, SourceKind
from .protocols import (
    Clock,
    EventRepository,
    ExecutorFactory,
    PageFetcher,
    RecordSource,
)


def ingest_source(
    *,
    repository: EventRepository,
    source: RecordSource,
    import_id: str,
    source_kind: SourceKind,
    source_name: str,
    clock: Clock,
) -> ImportResult:
    """Stream one normalization pipeline into the repository.

    Preserve the source's single-pass boundary: the repository should pull
    records incrementally, and a closeable iterator must be closed on success,
    failure, or cancellation.  The repository, not this coordinator, owns the
    atomic database transaction while it consumes that stream.
    """

    incomplete(
        f"milestone 2 {source_kind} import {import_id} from {source_name} "
        f"with {repository}, {source}, and {clock}"
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
    """Coordinate HTTP collection and the repository commit boundary.

    In strict mode, a page failure must reach no import transaction.  Partial
    mode commits successful pages in deterministic page/item order, records the
    failed pages, and still exposes the source-I/O failure category to the CLI.
    Keep executor creation injected so bounded work and cancellation cleanup are
    observable without real network access.
    """

    incomplete(
        f"milestone 5 HTTP import {import_id} from {base_url} with {repository}, "
        f"{clock}, {fetcher}, workers={workers}, partial={allow_partial}, "
        f"factory={executor_factory}"
    )
