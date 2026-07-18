"""
Lesson 5.7: Dates and Times

Use ``date`` for calendar dates, ``time`` for a time of day, ``datetime`` for
an instant or wall-clock reading, and ``timedelta`` for differences. Fixed
values keep this lesson's output deterministic.
"""

# Python 3.11's datetime.UTC is an alias for timezone.utc. This lesson uses the
# longer spelling intentionally so both the class and its UTC singleton are clear.
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


def measure_duration(operation) -> float:
    """Measure elapsed seconds with the monotonic clock."""
    started = system_time.monotonic()
    operation()
    return system_time.monotonic() - started


if __name__ == "__main__":
    calendar_date = date(2024, 2, 29)
    time_of_day = time(14, 30, 15)
    interval = timedelta(days=2, hours=3, minutes=4)
    print("Date:", calendar_date.isoformat())
    print("Time:", time_of_day.isoformat())
    print("Two days later:", (calendar_date + timedelta(days=2)).isoformat())
    print("Interval seconds:", interval.total_seconds())

    naive = datetime(2024, 7, 18, 10, 30)
    aware_utc = datetime(2024, 7, 18, 10, 30, tzinfo=timezone.utc)
    print("\nNaive datetime is aware:", is_aware(naive))
    print("UTC datetime is aware:", is_aware(aware_utc))

    # Naive values contain no offset, so Python cannot know which instant they
    # represent. replace(tzinfo=...) labels fields; it does not perform a
    # conversion. Attach a zone only when the fields are known to use that zone.
    try:
        to_utc(naive)
    except ValueError as error:
        print("Naive normalization rejected:", error)

    # datetime.fromisoformat() accepts ISO 8601 forms, including "Z" on Python
    # 3.11. RFC 3339 is a narrower Internet timestamp profile that requires an
    # offset. isoformat() emits "+00:00", a valid RFC 3339 UTC representation.
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

    # Unix timestamps are elapsed seconds from 1970-01-01T00:00:00Z (ignoring
    # leap seconds). Always state the unit: other systems often use milliseconds.
    epoch_example = datetime(2024, 1, 1, tzinfo=timezone.utc)
    timestamp_seconds = epoch_example.timestamp()
    restored = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    print("\nUnix timestamp (seconds):", int(timestamp_seconds))
    print("Timestamp restored in UTC:", restored.isoformat())

    # time.time() is a wall clock suitable for timestamps and can be adjusted.
    # time.monotonic() has no calendar meaning and cannot be converted to a
    # datetime, but differences between readings are reliable for durations.
    sample_monotonic_start = 100.25
    sample_monotonic_end = 100.90
    print(
        "Illustrative monotonic duration:",
        round(sample_monotonic_end - sample_monotonic_start, 2),
        "seconds",
    )

    zone_key = "America/New_York"
    try:
        eastern = ZoneInfo(zone_key)
    except ZoneInfoNotFoundError as error:
        # zoneinfo reads the operating system's IANA database (or the optional
        # tzdata package). Report missing data explicitly rather than silently
        # substituting a fixed offset, which would give incorrect DST behavior.
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

        first_0130 = datetime(2024, 11, 3, 1, 30, tzinfo=eastern, fold=0)
        second_0130 = first_0130.replace(fold=1)
        print("Repeated wall time, first:", first_0130.isoformat())
        print("Repeated wall time, second:", second_0130.isoformat())

        # timedelta has fixed day/second fields; it has no "month" unit. Local
        # wall-clock arithmetic across DST can represent 23 or 25 elapsed hours,
        # as above. ZoneInfo also does not reject nonexistent local wall times;
        # fold distinguishes repeated times. Define whether an application needs
        # elapsed-time arithmetic or calendar/wall-clock rules before calculating.
