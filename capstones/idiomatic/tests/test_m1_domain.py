"""Milestone 1: frozen values, validation, normalization, and deduplication."""

import unittest
from dataclasses import FrozenInstanceError

from implementation import IMPLEMENTATION
from ingest_report.models import Event, RawRecord, RejectedRecord
from ingest_report.validation import (
    deduplicate_events,
    normalize_record,
    normalize_records,
)

VALID = {
    "id": "evt-001",
    "occurred_at": "2026-07-16T08:00:00Z",
    "source": "checkout",
    "category": "request",
    "duration_ms": 125,
    "status": "success",
}


def normalized(**changes: object) -> Event | RejectedRecord:
    raw = dict(VALID)
    raw.update(changes)
    return normalize_record(RawRecord("fixture", 1, raw))


class _OneShot:
    # Re-iteration fails loudly and makes multiple passes observable. This alone
    # does not detect eager materialization performed during one pass.
    def __init__(self, records: list[RawRecord]):
        self.records = records
        self.iterations = 0

    def __iter__(self):
        self.iterations += 1
        if self.iterations > 1:
            raise AssertionError("source was iterated more than once")
        yield from self.records


class DomainTests(unittest.TestCase):
    def test_selected_implementation_and_immutable_normalized_event(self):
        # Milestone 1 owns the domain boundary: raw scalar values become a
        # canonical, frozen scalar-only Event or a diagnostic RejectedRecord.
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        event = normalized(source=" checkout ", category=" request ")
        self.assertEqual(
            event,
            Event(
                "evt-001",
                "2026-07-16T08:00:00.000Z",
                "checkout",
                "request",
                125,
                "success",
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            event.id = "changed"  # type: ignore[misc,union-attr]

    def test_timestamp_offsets_boundaries_and_fraction_truncation(self):
        cases = {
            "2026-07-16T08:00:00+02:30": "2026-07-16T05:30:00.000Z",
            "2026-07-16T08:00:00.9999999Z": "2026-07-16T08:00:00.999Z",
            "2024-02-29T23:59:59-01:00": "2024-03-01T00:59:59.000Z",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                event = normalized(occurred_at=value)
                self.assertIsInstance(event, Event)
                self.assertEqual(event.occurred_at, expected)

        for value in (
            "2026-07-16T08:00:00",
            "2026-07-16 08:00:00Z",
            "2026-07-16T08:00:60Z",
            123,
        ):
            with self.subTest(value=value):
                reject = normalized(occurred_at=value)
                self.assertIsInstance(reject, RejectedRecord)
                self.assertEqual(reject.code, "invalid_timestamp")

    def test_every_scalar_field_accepts_boundaries_and_rejects_bad_values(self):
        valid_cases = (
            {"id": "a"},
            {"id": "a" * 64},
            {"source": "x"},
            {"source": "界" * 64},
            {"category": "x"},
            {"duration_ms": 0},
            {"duration_ms": 86_400_000},
            {"status": "warning"},
            {"status": "failure"},
        )
        for changes in valid_cases:
            with self.subTest(changes=changes):
                self.assertIsInstance(normalized(**changes), Event)

        invalid_cases = (
            ({"id": ""}, "invalid_id"),
            ({"id": "a" * 65}, "invalid_id"),
            ({"id": "-bad"}, "invalid_id"),
            ({"source": ""}, "invalid_text"),
            ({"source": "x\x00"}, "invalid_text"),
            ({"category": "\ud800"}, "invalid_text"),
            ({"duration_ms": True}, "invalid_duration"),
            ({"duration_ms": 1.5}, "invalid_duration"),
            ({"duration_ms": -1}, "invalid_duration"),
            ({"duration_ms": 86_400_001}, "invalid_duration"),
            ({"status": "ok"}, "invalid_status"),
        )
        for changes, code in invalid_cases:
            with self.subTest(changes=changes):
                reject = normalized(**changes)
                self.assertIsInstance(reject, RejectedRecord)
                self.assertEqual(reject.code, code)

    def test_csv_integer_rules_are_distinct_from_json_number_rules(self):
        for value in ("0", "001", "86400000"):
            record = RawRecord(
                "fixture.csv",
                1,
                {**VALID, "duration_ms": value},
                "csv",
            )
            self.assertIsInstance(normalize_record(record), Event)
        for value in ("+1", "1.0", "1e2", " 1"):
            record = RawRecord(
                "fixture.csv",
                1,
                {**VALID, "duration_ms": value},
                "csv",
            )
            self.assertEqual(normalize_record(record).code, "invalid_duration")
        self.assertEqual(
            normalize_record(
                RawRecord("fixture.jsonl", 1, {**VALID, "duration_ms": "1"})
            ).code,
            "invalid_duration",
        )

    def test_shape_errors_have_stable_priority_and_diagnostics(self):
        # Stable error precedence gives callers one reproducible diagnosis when
        # a record violates more than one shape rule.
        missing = normalize_record(
            RawRecord("fixture", 4, {"id": "x", "unknown": "value"})
        )
        self.assertEqual((missing.code, missing.field), ("missing_field", "category"))

        unknown_raw = {**VALID, "extra": 1}
        unknown = normalize_record(RawRecord("fixture", 5, unknown_raw))
        self.assertEqual((unknown.code, unknown.field), ("unknown_field", "extra"))
        self.assertEqual(unknown.raw, unknown_raw)

        shape = normalize_record(
            RawRecord("fixture", 6, {}, shape_error="members are duplicated")
        )
        self.assertEqual(
            (shape.code, shape.message), ("invalid_shape", "members are duplicated")
        )

    def test_normalization_and_deduplication_are_single_pass_and_stable(self):
        # The one-shot input proves the pipeline consumes its source once.
        # Output order also establishes first-seen identity: the first event is
        # retained, a later matching ID is reported separately, and rejects stay
        # in their original stream position.
        source = _OneShot(
            [
                RawRecord("fixture", 1, VALID),
                RawRecord("fixture", 2, {**VALID, "duration_ms": 999}),
                RawRecord("fixture", 3, {**VALID, "id": "evt-002"}),
                RawRecord("fixture", 4, {**VALID, "status": "bad"}),
            ]
        )
        duplicates: list[Event] = []
        output = list(
            deduplicate_events(
                normalize_records(source),
                duplicates.append,
            )
        )
        self.assertEqual(source.iterations, 1)
        self.assertEqual(
            [item.id for item in output if isinstance(item, Event)],
            ["evt-001", "evt-002"],
        )
        self.assertEqual(len(duplicates), 1)
        self.assertIsInstance(output[-1], RejectedRecord)


if __name__ == "__main__":
    unittest.main(verbosity=2)
