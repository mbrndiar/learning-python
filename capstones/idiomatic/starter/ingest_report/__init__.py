"""Public boundary for the idiomatic Python capstone."""

from .cli import build_parser, main
from .errors import ApplicationError, IncompleteImplementationError
from .http_source import URLPageFetcher, fetch_http_records
from .models import (
    CategorySummary,
    Event,
    ImportResult,
    RawRecord,
    RejectedRecord,
    RejectSummary,
    Report,
    ReportFilters,
    ReportTotals,
    StatusSummary,
)
from .protocols import (
    Clock,
    EventRepository,
    ExecutorFactory,
    PageFetcher,
    RecordSource,
)
from .repository import SQLiteEventRepository
from .sources import CSVSource, JSONLinesSource
from .validation import deduplicate_events, normalize_record, normalize_records

__all__ = [
    "ApplicationError",
    "CSVSource",
    "CategorySummary",
    "Clock",
    "Event",
    "EventRepository",
    "ExecutorFactory",
    "ImportResult",
    "IncompleteImplementationError",
    "JSONLinesSource",
    "PageFetcher",
    "RawRecord",
    "RecordSource",
    "RejectedRecord",
    "RejectSummary",
    "Report",
    "ReportFilters",
    "ReportTotals",
    "SQLiteEventRepository",
    "StatusSummary",
    "URLPageFetcher",
    "build_parser",
    "deduplicate_events",
    "fetch_http_records",
    "main",
    "normalize_record",
    "normalize_records",
]
