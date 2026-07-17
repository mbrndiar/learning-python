"""Milestone 1 starter: pure validation, normalization, and deduplication.

Keep per-record validation pure and streaming composition single-pass. Stable
diagnostic priority, UTC millisecond normalization, first-occurrence identity,
and explicit closeable-iterator ownership are separate tested invariants.
"""

from collections.abc import Callable, Iterable, Iterator

from .errors import incomplete
from .models import Event, RawRecord, RejectedRecord


def normalize_record(record: RawRecord) -> Event | RejectedRecord:
    """Validate one record and return either an immutable event or reject.

    Apply shape checks and field rules with deterministic error priority, retain
    the original diagnostic mapping for rejects, and normalize valid timestamps
    to UTC milliseconds by truncation.  CSV-shaped integer rules intentionally
    differ from JSON-number rules.
    """

    # TODO(m1): use the specification's boundary cases and stable reject codes;
    # avoid sharing coercions that would blur CSV and JSON value semantics.
    incomplete(f"milestone 1 record {record.record_number} validation")


def normalize_records(records: Iterable[RawRecord]) -> Iterator[Event | RejectedRecord]:
    """Normalize lazily and close the source iterator when this iterator closes.

    Acquire and consume the input once without preflight or materialization.
    Close on exhaustion, input-side failure, or explicit iterator closure.
    Consumers must close a partially consumed iterator after downstream failure
    or cancellation.
    """

    # TODO(m1): the one-shot and early-close tests are the boundary, not merely
    # the values produced for a list input.
    incomplete("milestone 1 streaming normalization")


def deduplicate_events(
    records: Iterable[Event | RejectedRecord],
    on_duplicate: Callable[[Event], None] | None = None,
) -> Iterator[Event | RejectedRecord]:
    """Yield first ``(source, id)`` occurrences in stable order.

    Track identity only for valid events, pass rejects through unchanged, and
    notify exactly once for each later valid duplicate.  Preserve input order
    and one-pass behavior; repository deduplication still protects identities
    across separate imports.
    """

    # TODO(m1): separate within-stream first occurrence from the repository's
    # cross-import first-event invariant.
    incomplete("milestone 1 stable deduplication")
