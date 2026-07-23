# 🧱 Exercises: Chapter 8 - Structured Data and Time

**Prerequisites:** completed
[`lessons/08_structured_data_and_time/`](../../lessons/08_structured_data_and_time/README.md).

## Run commands

```bash
# See the starter fail on the first incomplete task:
python exercises/08_structured_data_and_time/exercises.py

# Compile-check without running:
python -m py_compile exercises/08_structured_data_and_time/exercises.py

# Check the reference solution:
python exercises/08_structured_data_and_time/solutions.py
```

## Tasks

1. **`save_json(path, data)`** / **`load_json(path)`** - write and read a
   JSON file with deterministic text (sorted keys), regardless of the
   input dict's key order.
2. **`validate_record(data)`** - validate that a parsed JSON value has
   exactly the expected shape (a dict with a non-empty string `title` and
   a bool `done`), raising `ValueError` describing the problem for
   anything else.
3. **`parse_timestamp_to_utc(text)`** - parse an ISO 8601 timestamp
   (accepting a trailing `"Z"` or a numeric offset) and normalize it to
   UTC, rejecting a naive (offset-less) timestamp with `ValueError`.
4. **`seconds_since(started_at, clock=...)`** - compute elapsed whole
   seconds using an injectable clock, so the function is deterministic to
   test without waiting on real time.

## Constraints

- Each starter initially raises `NotImplementedError`, so the checks stop
  at the first incomplete task with a focused traceback.
- File-based tasks run inside a `tempfile.TemporaryDirectory`, so the
  checks leave nothing behind regardless of whether they pass.
- No advanced typing or `Protocol` is required here -- `clock` is just an
  ordinary callable parameter with a default value; Chapter 11 covers
  typing those contracts explicitly.

## Edge cases exercised

- `save_json`/`load_json` writes the same dict twice with different key
  insertion order and asserts the two files' text is byte-for-byte
  identical -- deterministic output, not just a correct round-trip.
- `validate_record` is checked against five malformed shapes: a missing
  key, an empty title, a wrong-typed value, an extra key, and a
  non-dict value entirely -- every one must raise `ValueError`.
- `parse_timestamp_to_utc` is checked against a `"Z"`-suffixed timestamp,
  an explicit `+02:00` offset (both normalizing to the same UTC instant),
  and a naive timestamp with no offset at all, which must raise
  `ValueError` rather than guessing a time zone.
- `seconds_since` is checked with a fixed injected clock 45 seconds after
  `started_at`, asserting an exact result rather than a real-time-based
  range.
