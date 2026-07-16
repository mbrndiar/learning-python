"""Deterministic JSON and text report rendering."""

import json

from .models import ImportResult, Report


def import_result_dict(result: ImportResult) -> dict[str, object]:
    """Convert an import result to its stable JSON shape."""

    return {
        "import_id": result.import_id,
        "state": result.state,
        "accepted": result.accepted,
        "duplicates": result.duplicates,
        "rejected": result.rejected,
        "failed_pages": list(result.failed_pages),
    }


def report_dict(report: Report) -> dict[str, object]:
    """Convert a report to the documented semantic JSON shape."""

    return {
        "filters": {
            "from": report.filters.from_timestamp,
            "to": report.filters.to_timestamp,
            "category": report.filters.category,
            "status": report.filters.status,
        },
        "totals": {
            "events": report.totals.events,
            "duration_ms": report.totals.duration_ms,
            "rejected": report.totals.rejected,
        },
        "by_category": [
            {
                "category": item.category,
                "events": item.events,
                "duration_ms": item.duration_ms,
            }
            for item in report.by_category
        ],
        "by_status": [
            {
                "status": item.status,
                "events": item.events,
                "duration_ms": item.duration_ms,
            }
            for item in report.by_status
        ],
        "rejects_by_code": [
            {"code": item.code, "count": item.count} for item in report.rejects_by_code
        ],
    }


def render_json(value: object) -> str:
    """Render compact UTF-8-friendly JSON with a trailing newline."""

    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"


def render_text(report: Report) -> str:
    """Render the documented human-readable report headings."""

    def shown(value: str | None) -> str:
        return value if value is not None else "all"

    lines = [
        "Filters",
        f"  from: {shown(report.filters.from_timestamp)}",
        f"  to: {shown(report.filters.to_timestamp)}",
        f"  category: {shown(report.filters.category)}",
        f"  status: {shown(report.filters.status)}",
        "Totals",
        f"  events: {report.totals.events}",
        f"  duration_ms: {report.totals.duration_ms}",
        f"  rejected: {report.totals.rejected}",
        "By category",
    ]
    lines.extend(
        f"  {item.category}: events={item.events} duration_ms={item.duration_ms}"
        for item in report.by_category
    )
    if not report.by_category:
        lines.append("  (none)")
    lines.append("By status")
    lines.extend(
        f"  {item.status}: events={item.events} duration_ms={item.duration_ms}"
        for item in report.by_status
    )
    if not report.by_status:
        lines.append("  (none)")
    lines.append("Rejects by code")
    lines.extend(
        f"  {item.code}: count={item.count}" for item in report.rejects_by_code
    )
    if not report.rejects_by_code:
        lines.append("  (none)")
    return "\n".join(lines) + "\n"
