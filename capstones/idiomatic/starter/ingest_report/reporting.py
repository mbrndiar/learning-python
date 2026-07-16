"""Milestone 4 starter: deterministic JSON and text rendering."""

from .errors import incomplete
from .models import ImportResult, Report


def import_result_dict(result: ImportResult) -> dict[str, object]:
    """Build the documented import JSON object."""

    incomplete(f"milestone 4 import rendering for {result.import_id}")


def report_dict(report: Report) -> dict[str, object]:
    """Build the documented semantic report JSON object."""

    incomplete(f"milestone 4 report rendering for {report.filters}")


def render_json(value: object) -> str:
    """Render one JSON value with a trailing newline."""

    incomplete(f"milestone 4 JSON rendering for {type(value).__name__}")


def render_text(report: Report) -> str:
    """Render totals and stable grouped headings, including empty groups."""

    incomplete(f"milestone 4 text rendering for {report.filters}")
