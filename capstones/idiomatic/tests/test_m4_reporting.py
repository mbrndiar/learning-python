"""Milestone 4: complete filters, aggregates, stable ordering, and renderers."""

import json
import unittest

from implementation import IMPLEMENTATION
from ingest_report.errors import ApplicationError
from ingest_report.models import Event, ReportFilters
from ingest_report.reporting import render_json, render_text, report_dict
from ingest_report.repository import SQLiteEventRepository
from ingest_report.sources import CSVSource
from ingest_report.validation import normalize_records
from support import FIXED_TIME, FIXTURES, test_directory


class ReportingTests(unittest.TestCase):
    def _populated_repository(self, database):
        # A shared fixed corpus makes renderer, aggregate, and filter expectations
        # describe one reporting contract rather than independent examples.
        repository = SQLiteEventRepository(database)
        repository.import_records(
            import_id="valid",
            source_kind="csv",
            source_name="valid.csv",
            started_at=FIXED_TIME,
            records=normalize_records(
                CSVSource(FIXTURES / "events-valid.csv").records()
            ),
        )
        repository.import_records(
            import_id="mixed",
            source_kind="csv",
            source_name="mixed.csv",
            started_at=FIXED_TIME,
            records=normalize_records(
                CSVSource(FIXTURES / "events-mixed.csv").records()
            ),
        )
        return repository

    def test_json_and_text_match_golden_fixtures(self):
        # Milestone 4 owns deterministic presentation. The JSON golden pins the
        # semantic shape, values, and ordered arrays; the text golden additionally
        # pins exact ordering, whitespace, markers, and the final newline.
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        with test_directory() as directory:
            report = self._populated_repository(directory / "events.db").report(
                ReportFilters()
            )
            expected_json = json.loads(
                (FIXTURES / "report-expected.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                json.loads(render_json(report_dict(report))), expected_json
            )
            self.assertEqual(
                render_text(report),
                (FIXTURES / "report-expected.txt").read_text(encoding="utf-8"),
            )

    def test_filters_combine_with_and_and_use_inclusive_time_bounds(self):
        # The selected edge timestamps remain included while all supplied
        # dimensions narrow the same event set; rejects remain import-level data.
        with test_directory() as directory:
            repository = self._populated_repository(directory / "events.db")
            report = repository.report(
                ReportFilters(
                    from_timestamp="2026-07-16T08:00:00.000Z",
                    to_timestamp="2026-07-16T08:03:00.000Z",
                    category="request",
                    status="success",
                )
            )
            self.assertEqual(
                (
                    report.totals.events,
                    report.totals.duration_ms,
                    report.totals.rejected,
                ),
                (2, 125, 3),
            )
            self.assertEqual(
                [item.category for item in report.by_category], ["request"]
            )
            self.assertEqual([item.status for item in report.by_status], ["success"])
            with self.assertRaises(ApplicationError) as invalid:
                repository.report(
                    ReportFilters(
                        from_timestamp="2026-07-17T00:00:00.000Z",
                        to_timestamp="2026-07-16T00:00:00.000Z",
                    )
                )
            self.assertEqual(invalid.exception.code, "invalid_filter")

    def test_empty_report_has_zero_totals_empty_arrays_and_text_markers(self):
        with test_directory() as directory:
            report = SQLiteEventRepository(directory / "events.db").report(
                ReportFilters()
            )
            self.assertEqual(
                (
                    report.totals.events,
                    report.totals.duration_ms,
                    report.totals.rejected,
                ),
                (0, 0, 0),
            )
            self.assertEqual(
                (report.by_category, report.by_status, report.rejects_by_code),
                ((), (), ()),
            )
            self.assertEqual(render_text(report).count("  (none)"), 3)

    def test_group_order_is_unicode_stable_regardless_of_insertion_order(self):
        # Reversed insertion separates output ordering from database row order.
        # Python's code-point sort is the expected locale-independent contract.
        with test_directory() as directory:
            repository = SQLiteEventRepository(directory / "events.db")
            categories = ["zebra", "Éclair", "alpha", "Ωmega"]
            repository.import_records(
                import_id="order",
                source_kind="jsonl",
                source_name="fake",
                started_at=FIXED_TIME,
                records=[
                    Event(
                        f"id-{index}",
                        "2026-07-16T00:00:00.000Z",
                        "source",
                        category,
                        index,
                        "success",
                    )
                    for index, category in enumerate(reversed(categories), start=1)
                ],
            )
            report = repository.report(ReportFilters())
            self.assertEqual(
                [item.category for item in report.by_category],
                sorted(categories),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
