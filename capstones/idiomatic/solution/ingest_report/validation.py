"""Pure event validation and normalization."""

import re
from collections.abc import Callable, Iterable, Iterator
from datetime import UTC, datetime
from typing import cast

from .errors import ApplicationError
from .models import Event, RawRecord, RejectedRecord, Status

FIELDS = (
    "id",
    "occurred_at",
    "source",
    "category",
    "duration_ms",
    "status",
)
FIELD_SET = frozenset(FIELDS)
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")
IMPORT_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z"
)
CSV_INTEGER_PATTERN = re.compile(r"-?\d+\Z")
VALID_STATUSES = frozenset(("success", "warning", "failure"))


def _reject(
    record: RawRecord,
    code: str,
    field: str | None,
    message: str,
) -> RejectedRecord:
    return RejectedRecord(
        source_name=record.source_name,
        record_number=record.record_number,
        code=code,
        field=field,
        message=message,
        raw=record.raw,
    )


def normalize_timestamp(value: object) -> str | None:
    """Normalize one strict RFC 3339 timestamp, or return ``None``."""

    if not isinstance(value, str) or not TIMESTAMP_PATTERN.fullmatch(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    utc_value = parsed.astimezone(UTC)
    return utc_value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def normalize_filter_timestamp(value: str, option: str) -> str:
    """Normalize a CLI report bound or raise a stable input error."""

    normalized = normalize_timestamp(value)
    if normalized is None:
        raise ApplicationError(
            "invalid_filter",
            f"{option} must be an RFC 3339 timestamp with an explicit offset",
            2,
            {"field": option},
        )
    return normalized


def validate_import_id(import_id: str) -> None:
    """Validate the unique import identifier."""

    if not IMPORT_ID_PATTERN.fullmatch(import_id):
        raise ApplicationError(
            "invalid_import_id",
            "import_id must match [A-Za-z0-9][A-Za-z0-9._-]{0,63}",
            2,
            {"field": "import_id"},
        )


def _valid_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    if any(
        ord(character) < 32
        or 127 <= ord(character) <= 159
        or 0xD800 <= ord(character) <= 0xDFFF
        for character in value
    ):
        return None
    normalized = value.strip()
    if not 1 <= len(normalized) <= 64:
        return None
    return normalized


def _duration(record: RawRecord, value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        duration = value
    elif (
        record.source_kind == "csv"
        and isinstance(value, str)
        and CSV_INTEGER_PATTERN.fullmatch(value)
    ):
        duration = int(value)
    else:
        return None
    return duration if 0 <= duration <= 86_400_000 else None


def normalize_record(record: RawRecord) -> Event | RejectedRecord:
    """Validate and normalize one raw record without side effects."""

    if record.shape_error is not None:
        return _reject(record, "invalid_shape", None, record.shape_error)
    if not all(isinstance(key, str) for key in record.raw):
        return _reject(
            record,
            "invalid_shape",
            None,
            "record must be an object with unique string member names",
        )

    keys = set(record.raw)
    missing = sorted(FIELD_SET - keys)
    if missing:
        field = missing[0]
        return _reject(
            record,
            "missing_field",
            field,
            f"missing required field: {field}",
        )
    unknown = sorted(keys - FIELD_SET)
    if unknown:
        field = unknown[0]
        return _reject(
            record,
            "unknown_field",
            field,
            f"unknown field: {field}",
        )

    event_id = record.raw["id"]
    if not isinstance(event_id, str) or not ID_PATTERN.fullmatch(event_id):
        return _reject(
            record,
            "invalid_id",
            "id",
            "id must match [A-Za-z0-9][A-Za-z0-9._:-]{0,63}",
        )

    occurred_at = normalize_timestamp(record.raw["occurred_at"])
    if occurred_at is None:
        return _reject(
            record,
            "invalid_timestamp",
            "occurred_at",
            "occurred_at must be an RFC 3339 timestamp with an explicit offset",
        )

    source = _valid_text(record.raw["source"])
    if source is None:
        return _reject(
            record,
            "invalid_text",
            "source",
            "source must be a trimmed string of 1 through 64 Unicode scalar values "
            "without control characters",
        )
    category = _valid_text(record.raw["category"])
    if category is None:
        return _reject(
            record,
            "invalid_text",
            "category",
            "category must be a trimmed string of 1 through 64 Unicode scalar values "
            "without control characters",
        )

    duration_ms = _duration(record, record.raw["duration_ms"])
    if duration_ms is None:
        return _reject(
            record,
            "invalid_duration",
            "duration_ms",
            "duration_ms must be an integer from 0 through 86400000",
        )

    status_value = record.raw["status"]
    if not isinstance(status_value, str) or status_value not in VALID_STATUSES:
        return _reject(
            record,
            "invalid_status",
            "status",
            "status must be exactly success, warning, or failure",
        )
    status = cast(Status, status_value)
    return Event(
        id=event_id,
        occurred_at=occurred_at,
        source=source,
        category=category,
        duration_ms=duration_ms,
        status=status,
    )


def normalize_records(records: Iterable[RawRecord]) -> Iterator[Event | RejectedRecord]:
    """Normalize a source lazily and close a closeable iterator on every exit."""

    iterator = iter(records)
    try:
        for record in iterator:
            yield normalize_record(record)
    finally:
        close = getattr(iterator, "close", None)
        if callable(close):
            close()


def deduplicate_events(
    records: Iterable[Event | RejectedRecord],
    on_duplicate: Callable[[Event], None] | None = None,
) -> Iterator[Event | RejectedRecord]:
    """Yield first occurrences and rejects in stable, single-pass order."""

    seen: set[tuple[str, str]] = set()
    for record in records:
        if isinstance(record, RejectedRecord):
            yield record
            continue
        identity = (record.source, record.id)
        if identity in seen:
            if on_duplicate is not None:
                on_duplicate(record)
            continue
        seen.add(identity)
        yield record
