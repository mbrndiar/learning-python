"""Milestone 1 starter: pure validation, normalization, and deduplication."""

from collections.abc import Callable, Iterable, Iterator

from .errors import incomplete
from .models import Event, RawRecord, RejectedRecord


def normalize_record(record: RawRecord) -> Event | RejectedRecord:
    """Validate one record and return either an immutable event or reject."""

    # TODO(m1): implement every field, shape, and timestamp normalization rule.
    incomplete(f"milestone 1 record {record.record_number} validation")


def normalize_records(records: Iterable[RawRecord]) -> Iterator[Event | RejectedRecord]:
    """Normalize lazily and close the source iterator in a ``finally`` block."""

    # TODO(m1): keep this single-pass; do not turn the iterable into a list.
    incomplete("milestone 1 streaming normalization")


def deduplicate_events(
    records: Iterable[Event | RejectedRecord],
    on_duplicate: Callable[[Event], None] | None = None,
) -> Iterator[Event | RejectedRecord]:
    """Yield first ``(source, id)`` occurrences in stable order."""

    # TODO(m1): preserve rejects and notify the optional duplicate callback.
    incomplete("milestone 1 stable deduplication")
