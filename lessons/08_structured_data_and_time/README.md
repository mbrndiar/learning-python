# 🧱 Chapter 8: Structured Data and Time

**Semantic ID:** `module.structured-data-and-time` · **Prerequisites:**
`module.exceptions-files-and-paths`

## 📍 Where this fits

Chapter 7 gave you exceptions and files. This chapter uses both at once,
at a boundary every real program eventually crosses: exchanging data with
something that is not a live Python object -- a JSON file, an API payload,
a timestamp string from another system. JSON only understands a handful
of value shapes, and a clock only understands instants, not "now" in the
abstract. This chapter treats both as boundaries to validate deliberately,
not as APIs that always hand back exactly what you expect.

## 🎯 Learning objectives

After this chapter, you should be able to:

- explain which Python values JSON can represent directly, and which ones
  (tuples, sets, non-string dict keys) it silently reshapes or rejects;
- use `json.dump`/`json.load` for files and `json.dumps`/`json.loads` for
  text, and produce deterministic output with `sort_keys=True`;
- distinguish malformed JSON syntax (`json.JSONDecodeError`) from
  well-formed JSON with the wrong shape (a validation `ValueError` you
  raise yourself);
- explain why a naive `datetime` has no fixed meaning, and normalize an
  aware datetime to UTC with `astimezone(timezone.utc)`;
- parse and format timestamps with `fromisoformat`/`strptime` and
  `isoformat`/`strftime`, including the RFC 3339 offset form;
- measure elapsed time with `time.monotonic()` instead of a wall clock;
- inject a clock as a parameter so time-dependent code can be tested with
  a fixed, predictable instant instead of the real current time.

## 🧠 Motivation and mental model

Two different failure modes hide in "just read the data": the data can be
syntactically broken (not valid JSON at all), or it can be syntactically
fine but shaped wrong (valid JSON that is not the record you expected).
Chapter 7 gave you the vocabulary to tell those apart -- a decode error is
one exception type, a shape problem is a different one you raise
yourself. Time has an analogous split: a datetime can be naive (no fixed
meaning, unsafe to compare across sources) or aware (anchored to a UTC
offset, safe to compare and normalize). Treating both JSON and time as
boundaries to validate, rather than data you can trust blindly, is the
mental model this chapter builds.

## 1️⃣ JSON vs. Python values, dump/load, validation, and malformed input

JSON has exactly six value kinds: object, array, string, number, boolean,
and null. Python's richer type system maps onto them, but not one-to-one:

```python
import json

python_value = {
    "name": "Ada",
    "tags": ("core", "admin"),  # tuple -> JSON array
    "score": 9.5,
    "attempts": 3,
    "active": True,
    "notes": None,
}
text = json.dumps(python_value)
decoded = json.loads(text)
print(type(decoded["tags"]).__name__)
```

```text
list
```

A Python tuple becomes a JSON array on the way out and comes back as a
`list` -- JSON has no separate tuple type, so the tuple/list distinction
does not survive the round trip. JSON also has no int/float distinction
the way Python does: a whole-looking JSON number decodes to `int` only
when it has no decimal point or exponent, and dict keys are always
coerced to strings.

### `dumps`/`loads` work on text; `dump`/`load` work on a file

```python
def save_tasks(path, tasks):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, indent=2, sort_keys=True)
        handle.write("\n")
```

The `s`-suffixed functions (`dumps`, `loads`) work on `str`/`bytes` already
in memory; the plain functions (`dump`, `load`) work directly with an open
file object, saving an intermediate string. `indent` only affects textual
layout -- the decoded Python value is identical whether the JSON is compact
or spread across multiple lines.

### `sort_keys=True` makes output deterministic

```python
tasks = [
    {"id": 2, "title": "Validate boundaries", "done": True},
    {"id": 1, "title": "Learn JSON", "done": False},
]
save_tasks(path, tasks)
print(path.read_text(encoding="utf-8"))
```

```text
[
  {
    "done": true,
    "id": 2,
    "title": "Validate boundaries"
  },
  {
    "done": false,
    "id": 1,
    "title": "Learn JSON"
  }
]
```

Each object's keys (`done`, `id`, `title`) print in sorted order regardless
of the input dict's insertion order (`id`, `title`, `done`) -- this
matters for diffs and tests that compare serialized text directly.

### Validate the shape after a successful parse

```python
def validate_task(item):
    if not isinstance(item, dict):
        raise ValueError("each task must be a JSON object")
    task_id = item.get("id")
    title = item.get("title")
    done = item.get("done")
    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)  # bool is a subclass of int
        or not isinstance(title, str)
        or not isinstance(done, bool)
    ):
        raise ValueError("each task needs an integer id, string title, boolean done")
    return item
```

`json.loads()`/`json.load()` only guarantee valid JSON **syntax** -- they
say nothing about whether the decoded value has the shape a program
actually needs. `bool` is a subclass of `int` in Python, so
`isinstance(True, int)` is `True`; `validate_task` rejects a boolean `id`
explicitly rather than accepting it by accident.

### Malformed syntax vs. wrong shape raise different exceptions

```python
malformed_path.write_text('{"id": 1, "title": "oops"', encoding="utf-8")  # missing }
try:
    load_tasks_raw(malformed_path)
except json.JSONDecodeError as error:
    print("syntax error:", error)

wrong_shape_path.write_text(
    json.dumps([{"id": "not-a-number", "title": "x", "done": False}]),
    encoding="utf-8",
)
try:
    load_tasks(wrong_shape_path)
except ValueError as error:
    print("shape error:", error)
```

```text
syntax error: Expecting ',' delimiter: line 1 column 26 (char 25)
shape error: each task needs an integer id, string title, boolean done
```

A syntax error -- text that is not valid JSON at all -- raises
`json.JSONDecodeError` (itself a subclass of `ValueError`) from the
parser. A shape error -- well-formed JSON that does not match the expected
record -- raises the plain `ValueError` `validate_task` raises itself.
Both are ordinary exceptions, handled the way Chapter 7 taught.

Run the complete companion:

```bash
python lessons/08_structured_data_and_time/01_json_boundaries.py
```

See [`01_json_boundaries.py`](01_json_boundaries.py) for the full
sequence, run inside a `tempfile.TemporaryDirectory`.

> **Try one change:** change `validate_task`'s `task_id` check to accept a
> string instead of an `int`. Predict which of the two malformed-input
> checks above would then pass instead of raising. Only the shape check
> depends on `validate_task`'s rules; the syntax check depends on json's
> own parser and is unaffected by validation logic.

## 2️⃣ Naive/aware datetimes, UTC, parsing/formatting, and injected clocks

A naive `datetime` carries no UTC offset, so Python cannot know which
real-world instant it represents; an aware one does:

```python
from datetime import datetime, timezone


def is_aware(value):
    return value.tzinfo is not None and value.utcoffset() is not None


naive = datetime(2024, 7, 18, 10, 30)
aware_utc = datetime(2024, 7, 18, 10, 30, tzinfo=timezone.utc)
print(is_aware(naive))
print(is_aware(aware_utc))
```

```text
False
True
```

### Normalizing to UTC vs. relabeling with `replace`

```python
def to_utc(value):
    if not is_aware(value):
        raise ValueError("a UTC offset or time zone is required")
    return value.astimezone(timezone.utc)


try:
    to_utc(naive)
except ValueError as error:
    print("Naive normalization rejected:", error)
```

```text
Naive normalization rejected: a UTC offset or time zone is required
```

`to_utc` rejects the naive datetime outright, before comparing anything --
only an aware datetime can be safely normalized. `aware_value.astimezone
(timezone.utc)` *converts* any aware datetime to the same UTC instant;
`replace(tzinfo=timezone.utc)` (not called here) only *relabels* existing
fields with an offset without shifting them -- a different operation,
correct only when the fields are already known to be in that zone.

### Parsing and formatting timestamps

```python
timestamp_text = "2024-07-18T10:30:45+02:00"
parsed = datetime.fromisoformat(timestamp_text)
normalized = to_utc(parsed)
parsed_z = datetime.fromisoformat("2024-07-18T08:30:45Z")
print(parsed.isoformat())
print(normalized.isoformat())
print(parsed_z.isoformat())
```

```text
2024-07-18T10:30:45+02:00
2024-07-18T08:30:45+00:00
2024-07-18T08:30:45+00:00
```

`datetime.fromisoformat`/`strptime` parse text into a datetime;
`isoformat`/`strftime` do the reverse. Python 3.11's `fromisoformat` also
accepts a trailing `"Z"`, treating it as UTC. RFC 3339 is a narrower
Internet timestamp profile requiring an explicit offset; `isoformat()`'s
`"+00:00"` for UTC is a valid RFC 3339 representation.

### Wall clocks vs. monotonic clocks

```python
import time as system_time


def measure_duration(operation):
    started = system_time.monotonic()
    operation()
    return system_time.monotonic() - started
```

`time.time()` gives a calendar-meaningful wall-clock timestamp that can
jump (an NTP sync, a manual change). `time.monotonic()` has no calendar
meaning at all, but the *difference* between two readings measures
elapsed time reliably -- exactly what `measure_duration` uses it for.

### Injecting a clock makes time-dependent code deterministic to test

```python
def describe_age(created_at, clock=lambda: datetime.now(timezone.utc)):
    now = clock()
    age = now - created_at
    return f"{age.total_seconds():.0f} seconds old"


fixed_instant = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
fixed_clock = lambda: datetime(2024, 1, 1, 12, 0, 30, tzinfo=timezone.utc)
print(describe_age(fixed_instant, fixed_clock))
```

```text
30 seconds old
```

`describe_age` always returns exactly `"30 seconds old"` with this fixed
clock, regardless of when the lesson is actually run. A function that
calls `datetime.now()` directly deep inside its body is hard to test
deterministically, because its result depends on when the test happens to
run; accepting a `clock` callable, defaulting to the real one, keeps
production code simple while letting a caller substitute a fixed value.

### DST crossings show wall-clock arithmetic is not always 24 hours

```python
from datetime import timedelta
from zoneinfo import ZoneInfo

eastern = ZoneInfo("America/New_York")
before_dst = datetime(2024, 3, 9, 12, tzinfo=eastern)
same_wall_time_next_day = before_dst + timedelta(days=1)
elapsed_seconds = same_wall_time_next_day.timestamp() - before_dst.timestamp()
print(int(elapsed_seconds))
```

```text
82800
```

`82800` seconds is 23 hours, not 86400 (24 hours): adding one calendar day
to a wall-clock time that crosses a spring-forward DST transition does not
add exactly 24 elapsed real-world hours. `timedelta` has fixed day/second
fields with no "month" or "DST-aware" unit, so local wall-clock arithmetic
across a DST boundary can represent 23 or 25 elapsed hours depending on
direction.

Run the complete companion:

```bash
python lessons/08_structured_data_and_time/02_datetimes_timezones_and_clocks.py
```

See
[`02_datetimes_timezones_and_clocks.py`](02_datetimes_timezones_and_clocks.py)
for the full sequence, including `date`/`time`/`timedelta` basics and
Unix-timestamp round-tripping.

> **Try one change:** replace `fixed_clock` with a lambda returning a time
> 90 seconds later instead of 30, and predict `describe_age`'s new
> returned string. The function's logic did not change -- only the
> injected clock's value did, which is exactly the point of injecting it.

## 🔁 Transition to Chapter 9

Chapter 8 validated data shaped by an external format; the values inside
that data, though, have so far been plain functions, dicts, and built-in
types. Chapter 9, Objects and Data Models, introduces classes as a way to
bundle data with the behavior that keeps it valid -- so a `Task` or a
`BankAccount` can enforce its own invariants instead of relying on a
caller to validate it correctly every time.

## ⚠️ Common mistakes

- Assuming a tuple serialized to JSON deserializes back into a tuple; it
  comes back as a list every time.
- Comparing or subtracting a naive datetime and an aware one, which
  raises `TypeError` rather than silently picking a time zone.
- Calling `replace(tzinfo=timezone.utc)` on a datetime that was never in
  UTC, which relabels the existing fields instead of converting them.
- Using `time.time()` (or `datetime.now()`) to measure a duration; a wall
  clock can jump backward or forward independent of elapsed real time.
- Calling `datetime.now()` directly inside a function you want to test,
  which makes the function's result depend on when the test happens to
  run.

## 🧾 Summary

- JSON represents a narrow set of value shapes; round-tripping Python data
  through it can silently change types (tuple to list) and always
  coerces dict keys to strings.
- Validate JSON at two levels: syntax (`json.JSONDecodeError`) and shape
  (a `ValueError` you raise after a successful parse).
- Only an aware datetime carries a fixed real-world meaning;
  `astimezone(timezone.utc)` normalizes it, while `replace(tzinfo=...)`
  only relabels existing fields.
- `time.monotonic()` measures elapsed durations reliably; wall clocks are
  for timestamps, not durations.
- Accepting a clock as a parameter makes time-dependent code
  deterministic to test, without changing its production behavior.

## ❓ Review questions (closed notes)

1. What happens to a Python tuple after it round-trips through
   `json.dumps`/`json.loads`?
2. What is the difference between a JSON syntax error and a JSON shape
   error, and which exception type signals each?
3. What distinguishes a naive datetime from an aware one, and why does
   that distinction matter for comparisons?
4. What is the difference between `astimezone(timezone.utc)` and
   `replace(tzinfo=timezone.utc)`?
5. Why is `time.monotonic()` preferred over `time.time()` for measuring
   elapsed duration?
6. Why does accepting a clock as a parameter make a function easier to
   test deterministically?

## 📚 Authoritative references

- [`json` -- JSON encoder and decoder](https://docs.python.org/3/library/json.html)
- [`datetime` -- Basic date and time types](https://docs.python.org/3/library/datetime.html)
- [`zoneinfo` -- IANA time zone support](https://docs.python.org/3/library/zoneinfo.html)
- [`time.monotonic()`](https://docs.python.org/3/library/time.html#time.monotonic)
- [RFC 3339, Date and Time on the Internet](https://www.rfc-editor.org/rfc/rfc3339)

Once you can answer the review questions and have run both lesson files,
continue to
[`exercises/08_structured_data_and_time/`](../../exercises/08_structured_data_and_time/README.md).
