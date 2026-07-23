"""
Exercises: Chapter 8 - Structured Data and Time

Implement each function below, then run this file directly to check your
work.

    python exercises/08_structured_data_and_time/exercises.py

Each starter raises NotImplementedError until you implement it.
"""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def save_json(path, data):
    """Write `data` to `path` as deterministic, human-readable JSON.

    Use a trailing newline, sorted keys, and 2-space indentation so the
    file's text is stable across runs regardless of dict insertion order.
    """
    # TODO: implement this function
    raise NotImplementedError


def load_json(path):
    """Return the Python value stored as JSON at `path`."""
    # TODO: implement this function
    raise NotImplementedError


def validate_record(data):
    """Validate that `data` is a well-formed task record.

    A valid record is a dict with exactly the keys "title" (a non-empty
    str) and "done" (a bool). Raise ValueError, with a message describing
    the problem, for anything else -- wrong type, missing key, extra key,
    wrong value type, or an empty title. Return `data` unchanged when it
    is valid.
    """
    # TODO: implement this function
    raise NotImplementedError


def parse_timestamp_to_utc(text):
    """Parse an ISO 8601 timestamp and return it normalized to UTC.

    Accept a trailing "Z" or an explicit numeric offset. Raise ValueError
    (letting the original json/datetime error chain naturally, no need
    for `raise ... from`) if `text` has no offset at all -- a naive
    timestamp is not safe to normalize.
    """
    # TODO: implement this function
    raise NotImplementedError


def seconds_since(started_at, clock=lambda: datetime.now(UTC)):
    """Return the whole number of seconds between `started_at` and `clock()`.

    `clock` defaults to the real current UTC time but can be replaced with
    a fixed stand-in so this function is deterministic to test.
    """
    # TODO: implement this function
    raise NotImplementedError


with tempfile.TemporaryDirectory(prefix="json_exercise_") as directory:
    json_path = Path(directory) / "payload.json"
    save_json(json_path, {"b": 2, "a": 1})
    first_text = json_path.read_text(encoding="utf-8")
    save_json(json_path, {"a": 1, "b": 2})
    second_text = json_path.read_text(encoding="utf-8")
    assert first_text == second_text, "Task: output must not depend on key order"
    assert load_json(json_path) == {"a": 1, "b": 2}
print("save_json/load_json: OK")

assert validate_record({"title": "Write tests", "done": False}) == {
    "title": "Write tests",
    "done": False,
}
for bad_record in [
    {"title": "Write tests"},
    {"title": "", "done": False},
    {"title": "Write tests", "done": "no"},
    {"title": "Write tests", "done": False, "extra": 1},
    ["Write tests", False],
]:
    try:
        validate_record(bad_record)
        raise AssertionError(f"expected ValueError for {bad_record!r}")
    except ValueError:
        pass
print("validate_record: OK")

assert parse_timestamp_to_utc("2024-07-18T08:30:00Z") == datetime(
    2024, 7, 18, 8, 30, tzinfo=UTC
)
assert parse_timestamp_to_utc("2024-07-18T10:30:00+02:00") == datetime(
    2024, 7, 18, 8, 30, tzinfo=UTC
)
try:
    parse_timestamp_to_utc("2024-07-18T08:30:00")
    raise AssertionError("expected ValueError for a naive (offset-less) timestamp")
except ValueError:
    pass
print("parse_timestamp_to_utc: OK")

fixed_start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
fixed_clock = lambda: datetime(2024, 1, 1, 12, 0, 45, tzinfo=UTC)  # noqa: E731
assert seconds_since(fixed_start, fixed_clock) == 45
print("seconds_since: OK")

print("\nAll checks passed!")
