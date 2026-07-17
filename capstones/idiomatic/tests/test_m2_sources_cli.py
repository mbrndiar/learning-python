"""Milestone 2: streaming sources, injected coordination, and CLI categories."""

import io
import json
import unittest
from collections.abc import Iterable, Iterator, Sequence
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime

from implementation import IMPLEMENTATION
from ingest_report.application import ingest_source
from ingest_report.cli import build_parser, main
from ingest_report.errors import ApplicationError
from ingest_report.models import (
    Event,
    ImportResult,
    RawRecord,
    RejectedRecord,
    Report,
    ReportFilters,
    SourceKind,
)
from ingest_report.sources import CSVSource, JSONLinesSource
from ingest_report.validation import normalize_records
from support import FIXTURES, FixedClock, test_directory


class _IncrementalRepository:
    # The repository checks producer progress at each pull. If the application
    # materializes the source first, progress jumps ahead and the fake fails.
    def __init__(self, progress: list[int]):
        self.progress = progress
        self.seen: list[Event | RejectedRecord] = []

    def import_records(
        self,
        *,
        import_id: str,
        source_kind: SourceKind,
        source_name: str,
        started_at: datetime,
        records: Iterable[Event | RejectedRecord],
        failed_pages: Sequence[int] = (),
    ) -> ImportResult:
        for index, record in enumerate(records, start=1):
            self.assert_progress(index)
            self.seen.append(record)
        return ImportResult(import_id, "complete", len(self.seen), 0, 0, ())

    def assert_progress(self, expected: int) -> None:
        if self.progress != list(range(1, expected + 1)):
            raise AssertionError(
                "source was materialized before repository consumption"
            )

    def report(self, filters: ReportFilters) -> Report:
        raise AssertionError("report was not expected")


class _ProgressSource:
    # Each yield records exactly how far the producer has advanced, allowing the
    # repository fake to prove interleaved production and consumption.
    def __init__(self, progress: list[int]):
        self.progress = progress

    def records(self) -> Iterator[RawRecord]:
        for number in range(1, 4):
            self.progress.append(number)
            yield RawRecord(
                "fake",
                number,
                {
                    "id": f"evt-{number}",
                    "occurred_at": "2026-07-16T08:00:00Z",
                    "source": "fake",
                    "category": "request",
                    "duration_ms": number,
                    "status": "success",
                },
            )


class SourceAndCLITests(unittest.TestCase):
    def test_csv_and_jsonl_fixtures_normalize_semantically_equivalent_events(self):
        # Milestone 2 owns adapters and coordination: different source syntaxes
        # must feed the same domain normalization contract.
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        csv_events = list(
            normalize_records(CSVSource(FIXTURES / "events-valid.csv").records())
        )
        json_events = list(
            normalize_records(
                JSONLinesSource(FIXTURES / "events-valid.jsonl").records()
            )
        )
        self.assertEqual(csv_events, json_events)
        self.assertTrue(all(isinstance(item, Event) for item in csv_events))

    def test_mixed_sources_keep_record_numbers_and_shape_rejects(self):
        csv_records = list(CSVSource(FIXTURES / "events-mixed.csv").records())
        csv_results = list(normalize_records(csv_records))
        self.assertEqual(
            [
                item.record_number
                for item in csv_results
                if isinstance(item, RejectedRecord)
            ],
            [3, 4, 5],
        )

        json_results = list(
            normalize_records(
                JSONLinesSource(FIXTURES / "events-mixed.jsonl").records()
            )
        )
        rejects = [item for item in json_results if isinstance(item, RejectedRecord)]
        self.assertEqual([item.record_number for item in rejects], [4, 5, 6])
        self.assertEqual(
            [item.code for item in rejects],
            ["invalid_duration", "invalid_shape", "missing_field"],
        )

    def test_invalid_headers_and_malformed_jsonl_are_source_content_errors(self):
        with test_directory() as directory:
            bad_csv = directory / "bad.csv"
            bad_csv.write_text("id,status\nx,success\n", encoding="utf-8")
            with self.assertRaises(ApplicationError) as csv_error:
                list(CSVSource(bad_csv).records())
            self.assertEqual(
                (csv_error.exception.code, csv_error.exception.exit_code),
                ("invalid_csv_header", 3),
            )

            bad_jsonl = directory / "bad.jsonl"
            bad_jsonl.write_text('{"id":\n', encoding="utf-8")
            with self.assertRaises(ApplicationError) as json_error:
                list(JSONLinesSource(bad_jsonl).records())
            self.assertEqual(
                (json_error.exception.code, json_error.exception.exit_code),
                ("invalid_jsonl", 3),
            )

    def test_application_passes_records_incrementally(self):
        # This proves streaming at the application/repository seam, not a memory
        # bound for either adapter or the database implementation.
        progress: list[int] = []
        repository = _IncrementalRepository(progress)
        result = ingest_source(
            repository=repository,
            source=_ProgressSource(progress),
            import_id="stream-1",
            source_kind="jsonl",
            source_name="fake",
            clock=FixedClock(),
        )
        self.assertEqual((result.accepted, len(repository.seen)), (3, 3))

    def test_source_iterator_closes_when_repository_fails_or_is_cancelled(self):
        # Closing a partially consumed normalization generator must propagate to
        # its source so file/network iterators can release resources. Both an
        # ordinary failure and cancellation take the same cleanup path.
        for failure in (RuntimeError("stop"), KeyboardInterrupt()):
            closed = False

            def records() -> Iterator[RawRecord]:
                nonlocal closed
                try:
                    yield RawRecord("fake", 1, {})
                    yield RawRecord("fake", 2, {})
                finally:
                    closed = True

            iterator = normalize_records(records())
            next(iterator)
            with self.assertRaises(type(failure)):
                try:
                    raise failure
                finally:
                    iterator.close()
            self.assertTrue(closed)

    def test_parser_and_json_error_boundary(self):
        parser = build_parser()
        self.assertEqual(
            parser.parse_args(
                [
                    "--db",
                    "events.db",
                    "ingest",
                    "--import-id",
                    "x",
                    "--format",
                    "http",
                    "--url",
                    "http://127.0.0.1/events",
                ]
            ).workers,
            4,
        )
        with test_directory() as directory:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--json-errors",
                        "--db",
                        str(directory / "events.db"),
                        "ingest",
                        "--import-id",
                        "bad id",
                        "--format",
                        "csv",
                        "--input",
                        str(FIXTURES / "events-valid.csv"),
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            envelope = json.loads(stderr.getvalue())
            self.assertEqual(envelope["error"]["code"], "invalid_import_id")

    def test_unreadable_source_is_exit_four_without_traceback(self):
        with test_directory() as directory:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--db",
                        str(directory / "events.db"),
                        "ingest",
                        "--import-id",
                        "missing",
                        "--format",
                        "jsonl",
                        "--input",
                        str(directory / "missing.jsonl"),
                    ]
                )
            self.assertEqual(exit_code, 4)
            self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
