"""Public boundary for the idiomatic Python capstone."""

from .cli import build_parser, main
from .errors import IncompleteImplementationError
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
from .protocols import Clock, EventRepository, PageFetcher, RecordSource

__all__ = [
    "CategorySummary",
    "Clock",
    "Event",
    "EventRepository",
    "ImportResult",
    "IncompleteImplementationError",
    "PageFetcher",
    "RawRecord",
    "RecordSource",
    "RejectedRecord",
    "RejectSummary",
    "Report",
    "ReportFilters",
    "ReportTotals",
    "StatusSummary",
    "build_parser",
    "main",
]
