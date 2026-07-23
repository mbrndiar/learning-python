"""
Chapter 8, Lesson 2: Datetimes, Timezones, and Clocks

Purpose: distinguish naive from aware datetimes, normalize to UTC, parse
and format timestamps, measure elapsed time with a monotonic clock, and
inject a clock as a dependency instead of calling `datetime.now()` deep
inside application code.

Prerequisites: Lesson 1 (JSON boundaries) and Chapter 7. Python 3.11's
`datetime.UTC` is an alias for `timezone.utc`; this lesson uses the longer
spelling so both the class and its UTC singleton stay visible.
"""

# ruff: noqa: UP017

import time as system_time
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def is_aware(value: datetime) -> bool:
    """Return whether *value* has a usable UTC offset."""
    return value.tzinfo is not None and value.utcoffset() is not None


def to_utc(value: datetime) -> datetime:
    """Normalize an aware datetime to UTC, rejecting ambiguous naive input."""
    if not is_aware(value):
        raise ValueError("a UTC offset or time zone is required")
    return value.astimezone(timezone.utc)


# Step 1: date/time/timedelta basics -- a calendar date, a time of day, and
# a difference between two points in time are three distinct types.
calendar_date = date(2024, 2, 29)
time_of_day = time(14, 30, 15)
interval = timedelta(days=2, hours=3, minutes=4)
print("Date:", calendar_date.isoformat())
print("Time:", time_of_day.isoformat())
print("Two days later:", (calendar_date + timedelta(days=2)).isoformat())
print("Interval seconds:", interval.total_seconds())

# Step 2: naive versus aware. A naive datetime carries no UTC offset, so
# Python cannot know which real-world instant it represents. `replace
# (tzinfo=...)` only *labels* the existing fields with an offset -- it does
# not shift them -- so attach a zone only when the fields are already
# known to be in that zone.
naive = datetime(2024, 7, 18, 10, 30)
aware_utc = datetime(2024, 7, 18, 10, 30, tzinfo=timezone.utc)
print("\nNaive datetime is aware:", is_aware(naive))
print("UTC datetime is aware:", is_aware(aware_utc))

try:
    to_utc(naive)
except ValueError as error:
    print("Naive normalization rejected:", error)

# Step 3: parsing and formatting. fromisoformat() accepts ISO 8601 forms,
# including a trailing "Z" (Python 3.11+). RFC 3339 is a narrower Internet
# timestamp profile that requires an explicit offset; isoformat() emits
# "+00:00" for UTC, which is a valid RFC 3339 UTC representation.
timestamp_text = "2024-07-18T10:30:45+02:00"
parsed = datetime.fromisoformat(timestamp_text)
normalized = to_utc(parsed)
parsed_z = datetime.fromisoformat("2024-07-18T08:30:45Z")
print("\nParsed ISO 8601:", parsed.isoformat())
print("Normalized RFC 3339 UTC:", normalized.isoformat())
print("Parsed Z as UTC:", parsed_z.isoformat())

formatted_text = "2024/12/31 23:45:00 +0000"
formatted = datetime.strptime(formatted_text, "%Y/%m/%d %H:%M:%S %z")
print("strptime result:", formatted.isoformat())
print("strftime result:", formatted.strftime("%Y-%m-%d %H:%M:%S %z"))

epoch_example = datetime(2024, 1, 1, tzinfo=timezone.utc)
timestamp_seconds = epoch_example.timestamp()
restored = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
print("\nUnix timestamp (seconds):", int(timestamp_seconds))
print("Timestamp restored in UTC:", restored.isoformat())


# Step 4: elapsed-time clocks. time.time() is a wall clock, suitable for
# timestamps, and can jump (NTP sync, manual change). time.monotonic() has
# no calendar meaning at all and cannot become a datetime, but the
# *difference* between two readings is reliable for measuring a duration.
def measure_duration(operation) -> float:
    """Measure elapsed seconds with the monotonic clock."""
    started = system_time.monotonic()
    operation()
    return system_time.monotonic() - started


elapsed = measure_duration(lambda: sum(range(200_000)))
print("\nmeasure_duration ran and returned a non-negative float:", elapsed >= 0)
# The actual duration varies by machine load, so only its type and sign are
# asserted above -- the printed value itself is illustrative, not fixed.


# Step 5: injected clocks. A function that calls datetime.now() (or
# time.time()) directly is hard to test deterministically -- its result
# depends on when the test happens to run. Accepting a clock as a
# parameter, defaulting to the real one, keeps production code simple
# while letting a caller substitute a fixed value.
def utc_now(clock=lambda: datetime.now(timezone.utc)) -> datetime:
    """Return the current UTC instant, or a caller-supplied stand-in."""
    return clock()


def describe_age(created_at: datetime, clock=lambda: datetime.now(timezone.utc)) -> str:
    """Describe how long ago `created_at` was, using an injectable clock."""
    now = clock()
    age = now - created_at
    return f"{age.total_seconds():.0f} seconds old"


fixed_instant = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
fixed_clock = lambda: datetime(2024, 1, 1, 12, 0, 30, tzinfo=timezone.utc)  # noqa: E731
print(
    "\nDescribe age with an injected fixed clock:",
    describe_age(fixed_instant, fixed_clock),
)
assert describe_age(fixed_instant, fixed_clock) == "30 seconds old"
print("Real utc_now() is a datetime:", isinstance(utc_now(), datetime))

# Step 6: time zones. zoneinfo reads the operating system's IANA time zone
# database (or the optional tzdata package). Report a missing zone
# explicitly instead of silently substituting a fixed offset, which would
# give incorrect results across daylight-saving transitions.
zone_key = "America/New_York"
try:
    eastern = ZoneInfo(zone_key)
except ZoneInfoNotFoundError as error:
    print(f"\n{zone_key} unavailable: {type(error).__name__}")
else:
    winter = datetime(2024, 1, 15, 12, tzinfo=eastern)
    summer = datetime(2024, 7, 15, 12, tzinfo=eastern)
    print("\nWinter local to UTC:", to_utc(winter).isoformat())
    print("Summer local to UTC:", to_utc(summer).isoformat())

    before_dst = datetime(2024, 3, 9, 12, tzinfo=eastern)
    same_wall_time_next_day = before_dst + timedelta(days=1)
    elapsed_seconds = same_wall_time_next_day.timestamp() - before_dst.timestamp()
    print("Next wall-clock day:", same_wall_time_next_day.isoformat())
    print("Actual elapsed seconds across DST:", int(elapsed_seconds))
    # timedelta has fixed day/second fields, no "month" unit; local
    # wall-clock arithmetic across a DST boundary can represent 23 or 25
    # elapsed hours, as shown above.

# --- One-variable experiment -------------------------------------------
# Replace `fixed_clock` with a lambda returning a time 90 seconds later
# instead of 30, and predict describe_age's new returned string. The
# function's logic did not change -- only the injected clock's value did,
# which is exactly the point of injecting it.
