"""Immutable public values for ingestion and reporting."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, TypeAlias

Status: TypeAlias = Literal["success", "warning", "failure"]
SourceKind: TypeAlias = Literal["csv", "jsonl", "http"]
ImportState: TypeAlias = Literal["complete", "partial"]


@dataclass(frozen=True, slots=True)
class Event:
    """One validated and normalized operational event."""

    id: str
    occurred_at: str
    source: str
    category: str
    duration_ms: int
    status: Status


@dataclass(frozen=True, slots=True)
class RawRecord:
    """One source record with its stable diagnostic position."""

    source_name: str
    record_number: int
    raw: Mapping[str, object]
    source_kind: SourceKind | None = None
    shape_error: str | None = None


@dataclass(frozen=True, slots=True)
class RejectedRecord:
    """One invalid record retained for deterministic reporting."""

    source_name: str
    record_number: int
    code: str
    field: str | None
    message: str
    raw: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw", MappingProxyType(dict(self.raw)))


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Summary of one committed complete or partial import."""

    import_id: str
    state: ImportState
    accepted: int
    duplicates: int
    rejected: int
    failed_pages: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ReportFilters:
    """Inclusive event filters used by report queries."""

    from_timestamp: str | None = None
    to_timestamp: str | None = None
    category: str | None = None
    status: Status | None = None


@dataclass(frozen=True, slots=True)
class ReportTotals:
    """Top-level event, duration, and reject totals."""

    events: int
    duration_ms: int
    rejected: int


@dataclass(frozen=True, slots=True)
class CategorySummary:
    """Aggregate values for one category."""

    category: str
    events: int
    duration_ms: int


@dataclass(frozen=True, slots=True)
class StatusSummary:
    """Aggregate values for one status."""

    status: Status
    events: int
    duration_ms: int


@dataclass(frozen=True, slots=True)
class RejectSummary:
    """Count of stored rejects sharing one code."""

    code: str
    count: int


@dataclass(frozen=True, slots=True)
class Report:
    """Deterministically ordered report data before rendering."""

    filters: ReportFilters
    totals: ReportTotals
    by_category: tuple[CategorySummary, ...]
    by_status: tuple[StatusSummary, ...]
    rejects_by_code: tuple[RejectSummary, ...]
