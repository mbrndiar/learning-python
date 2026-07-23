"""
Solutions: Chapter 8 - Structured Data and Time

Reference solutions for exercises/08_structured_data_and_time/exercises.py.

Run this file directly:

    python exercises/08_structured_data_and_time/solutions.py
"""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, sort_keys=True, indent=2)
        handle.write("\n")


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def validate_record(data):
    if not isinstance(data, dict):
        raise ValueError(f"expected a dict, got {type(data).__name__}")
    if set(data.keys()) != {"title", "done"}:
        raise ValueError(
            f"expected exactly 'title' and 'done' keys, got {sorted(data)}"
        )
    if not isinstance(data["title"], str) or not data["title"]:
        raise ValueError("'title' must be a non-empty string")
    if not isinstance(data["done"], bool):
        raise ValueError("'done' must be a bool")
    return data


def parse_timestamp_to_utc(text):
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp has no UTC offset: {text!r}")
    return parsed.astimezone(UTC)


def seconds_since(started_at, clock=lambda: datetime.now(UTC)):
    return int((clock() - started_at).total_seconds())


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
