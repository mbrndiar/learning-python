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

## 🧩 Progressive syntax and mechanism

1. **The JSON value model.** Only `dict`, `list`, `str`, `int`, `float`,
   `bool`, and `None` round-trip through JSON; tuples become lists on the
   way out, and dict keys are always coerced to strings.
2. **`dump`/`load` vs. `dumps`/`loads`.** The `s`-suffixed functions work
   on `str`/`bytes` in memory; the plain functions work on an open file
   object.
3. **Deterministic output.** `json.dumps(..., sort_keys=True)` produces
   the same text every time regardless of the input dict's insertion
   order, which matters for diffs and tests.
4. **Boundary validation.** Catch `json.JSONDecodeError` for syntax
   problems; after a successful parse, check the resulting shape
   yourself and raise `ValueError` (or a subclass) for a well-formed but
   wrong-shaped value.
5. **Naive vs. aware datetimes.** A naive `datetime` has no `tzinfo`; an
   aware one does, and only an aware datetime can be safely normalized or
   compared across sources.
6. **Normalizing to UTC.** `aware_value.astimezone(timezone.utc)`
   converts any aware datetime to the same UTC instant; `replace(tzinfo=
   ...)` relabels fields without shifting them, which is a different
   operation entirely.
7. **Parsing and formatting.** `datetime.fromisoformat`/`strptime` parse
   text into a datetime; `isoformat`/`strftime` do the reverse; Python
   3.11's `fromisoformat` also accepts a trailing `"Z"`.
8. **Wall clocks vs. monotonic clocks.** `time.time()` gives a
   calendar-meaningful timestamp that can jump; `time.monotonic()` has no
   calendar meaning but its differences measure elapsed time reliably.
9. **Injected clocks.** A function that accepts a `clock` callable
   (defaulting to the real `datetime.now`/`time.monotonic`) can be tested
   with a fixed, deterministic value instead of the unpredictable real
   time.

## 📖 Read-predict-run-modify workflow

Work through both lesson files in order, predicting each output before
running:

```bash
python lessons/08_structured_data_and_time/01_json_boundaries.py
python lessons/08_structured_data_and_time/02_datetimes_timezones_and_clocks.py
```

### Expected output highlights

- `01_json_boundaries.py`: the tuple `(1, 2, 3)` round-trips as the list
  `[1, 2, 3]`, not back into a tuple -- JSON has no tuple type. Deterministic
  output is confirmed by re-serializing with a different key order and
  observing the sorted text is identical either way. A malformed-syntax
  string raises `json.JSONDecodeError`; a well-formed but wrong-shaped
  value raises the boundary's own `ValueError` instead.
- `02_datetimes_timezones_and_clocks.py`: normalizing a naive datetime
  raises `ValueError` before anything is compared; `describe_age` with an
  injected fixed clock always prints `30 seconds old`, regardless of when
  the lesson is actually run; the DST-crossing example shows the elapsed
  seconds between two wall-clock-identical times a day apart is not
  exactly 86400.

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
