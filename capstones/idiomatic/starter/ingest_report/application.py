"""Milestone 2/5 starter: dependency-injected import coordination."""

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
    """Stream normalized file records into the repository."""

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
    """Coordinate milestone 5 HTTP collection and partial commit semantics."""

    incomplete(
        f"milestone 5 HTTP import {import_id} from {base_url} with {repository}, "
        f"{clock}, {fetcher}, workers={workers}, partial={allow_partial}, "
        f"factory={executor_factory}"
    )
