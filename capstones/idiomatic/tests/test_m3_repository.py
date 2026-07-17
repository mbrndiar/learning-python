"""Milestone 3: schema checks, atomic imports, identities, and reopen behavior."""

import sqlite3
import unittest
from collections.abc import Iterator
from contextlib import closing

from implementation import IMPLEMENTATION
from ingest_report.errors import ApplicationError
from ingest_report.models import Event, RejectedRecord, ReportFilters
from ingest_report.repository import APPLICATION_ID, SQLiteEventRepository
from ingest_report.sources import CSVSource
from ingest_report.validation import normalize_records
from support import FIXED_TIME, FIXTURES, test_directory


class RepositoryTests(unittest.TestCase):
    def test_schema_creation_reopen_round_trip_and_duplicate_identity(self):
        # Milestone 3 owns persistent identity and schema compatibility. Reopening
        # the file must preserve data and markers; duplicate identity is the
        # (source, event ID) pair, so later conflicting fields cannot replace the
        # first stored event.
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        with test_directory() as directory:
            database = directory / "events.db"
            repository = SQLiteEventRepository(database)
            first = repository.import_records(
                import_id="first",
                source_kind="csv",
                source_name="valid.csv",
                started_at=FIXED_TIME,
                records=normalize_records(
                    CSVSource(FIXTURES / "events-valid.csv").records()
                ),
            )
            self.assertEqual(
                (first.accepted, first.duplicates, first.rejected), (4, 0, 0)
            )

            changed_duplicate = Event(
                "evt-001",
                "2026-07-17T00:00:00.000Z",
                "checkout",
                "changed",
                999,
                "failure",
            )
            second = SQLiteEventRepository(database).import_records(
                import_id="second",
                source_kind="jsonl",
                source_name="fake",
                started_at=FIXED_TIME,
                records=[changed_duplicate],
            )
            self.assertEqual((second.accepted, second.duplicates), (0, 1))
            report = SQLiteEventRepository(database).report(ReportFilters())
            self.assertEqual(
                (report.totals.events, report.totals.duration_ms), (4, 400)
            )

            with closing(sqlite3.connect(database)) as connection:
                self.assertEqual(
                    connection.execute("PRAGMA user_version").fetchone()[0], 1
                )
                self.assertEqual(
                    connection.execute("PRAGMA application_id").fetchone()[0],
                    APPLICATION_ID,
                )

    def test_reused_import_id_does_not_mutate_data(self):
        # Import IDs are repository identities, not merely labels. Rejecting a
        # reuse before consuming new data prevents a second import from leaking
        # events into the first import's history.
        with test_directory() as directory:
            repository = SQLiteEventRepository(directory / "events.db")
            repository.import_records(
                import_id="same",
                source_kind="csv",
                source_name="one",
                started_at=FIXED_TIME,
                records=[],
            )
            with self.assertRaises(ApplicationError) as caught:
                repository.import_records(
                    import_id="same",
                    source_kind="csv",
                    source_name="two",
                    started_at=FIXED_TIME,
                    records=[
                        Event(
                            "new",
                            "2026-07-16T00:00:00.000Z",
                            "source",
                            "category",
                            1,
                            "success",
                        )
                    ],
                )
            self.assertEqual(caught.exception.code, "import_exists")
            self.assertEqual(repository.report(ReportFilters()).totals.events, 0)

    def test_mid_import_failure_rolls_back_events_rejects_and_metadata(self):
        # A failure after both accepted and rejected rows have been yielded must
        # roll back the whole logical import, including its metadata. This proves
        # transaction atomicity for this execution, not durability after a crash.
        with test_directory() as directory:
            database = directory / "events.db"
            repository = SQLiteEventRepository(database)

            def failing_records() -> Iterator[Event | RejectedRecord]:
                yield Event(
                    "one",
                    "2026-07-16T00:00:00.000Z",
                    "source",
                    "category",
                    1,
                    "success",
                )
                yield RejectedRecord(
                    "fixture", 2, "invalid_id", "id", "bad", {"id": ""}
                )
                raise RuntimeError("injected failure")

            with self.assertRaisesRegex(RuntimeError, "injected"):
                repository.import_records(
                    import_id="rollback",
                    source_kind="jsonl",
                    source_name="fixture",
                    started_at=FIXED_TIME,
                    records=failing_records(),
                )
            self.assertEqual(repository.report(ReportFilters()).totals.events, 0)
            with closing(sqlite3.connect(database)) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM imports").fetchone()[0], 0
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM rejects").fetchone()[0], 0
                )

    def test_newer_incomplete_and_corrupt_schemas_fail_closed(self):
        # Existing files are never silently adopted or rewritten when their
        # version, application shape, or SQLite contents are not recognized.
        with test_directory() as directory:
            newer = directory / "newer.db"
            with closing(sqlite3.connect(newer)) as connection:
                connection.execute("PRAGMA user_version = 2")
            with self.assertRaises(ApplicationError) as version_error:
                SQLiteEventRepository(newer)
            self.assertEqual(version_error.exception.code, "unsupported_schema")

            incomplete = directory / "incomplete.db"
            with closing(sqlite3.connect(incomplete)) as connection:
                connection.execute("CREATE TABLE user_data (value TEXT)")
                connection.commit()
            with self.assertRaises(ApplicationError) as incomplete_error:
                SQLiteEventRepository(incomplete)
            self.assertEqual(incomplete_error.exception.code, "unsupported_schema")
            with closing(sqlite3.connect(incomplete)) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM user_data").fetchone()[0],
                    0,
                )

            corrupt = directory / "corrupt.db"
            corrupt.write_bytes(b"not a sqlite database")
            with self.assertRaises(ApplicationError) as corrupt_error:
                SQLiteEventRepository(corrupt)
            self.assertEqual(corrupt_error.exception.code, "database_error")
            self.assertEqual(corrupt.read_bytes(), b"not a sqlite database")

    def test_values_are_parameterized_not_interpreted_as_sql(self):
        with test_directory() as directory:
            repository = SQLiteEventRepository(directory / "events.db")
            hostile = "x' OR 1=1 --"
            repository.import_records(
                import_id="sql",
                source_kind="jsonl",
                source_name="fixture",
                started_at=FIXED_TIME,
                records=[
                    Event(
                        "id",
                        "2026-07-16T00:00:00.000Z",
                        "source",
                        hostile,
                        1,
                        "success",
                    )
                ],
            )
            self.assertEqual(
                repository.report(ReportFilters(category=hostile)).totals.events, 1
            )
            self.assertEqual(
                repository.report(ReportFilters(category="missing")).totals.events, 0
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
