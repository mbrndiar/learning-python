"""Streaming file adapters with deterministic order and stable error categories."""

import csv
import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import cast

from .errors import ApplicationError
from .models import RawRecord
from .validation import FIELDS


class _Object(dict[str, object]):
    """A decoded object that preserves evidence lost by normal dict decoding."""

    duplicate_members: bool

    def __init__(self, pairs: list[tuple[str, object]]):
        super().__init__()
        self.duplicate_members = False
        for key, value in pairs:
            if key in self:
                # Keep the last value for Mapping compatibility, but retain enough
                # evidence to reject the object instead of silently accepting it.
                self.duplicate_members = True
            self[key] = value


def _reject_json_constant(value: str) -> object:
    # The standard-library decoder otherwise accepts NaN and infinities, which
    # JSON itself does not define and which would make cross-parser behavior vary.
    raise ValueError(f"non-standard JSON constant {value}")


def _contains_duplicate_members(value: object) -> bool:
    if isinstance(value, _Object):
        return value.duplicate_members or any(
            _contains_duplicate_members(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_duplicate_members(item) for item in value)
    return False


class CSVSource:
    """Stream the exact UTF-8 CSV dialect in logical record order.

    Opening is lazy: the returned generator owns the file only while it is being
    advanced, and releasing it promptly still requires exhaustion or closure.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        try:
            with self.path.open("r", encoding="utf-8", newline="") as file:
                # newline="" delegates embedded-newline handling to csv.reader
                # instead of allowing text newline translation to corrupt records.
                reader = csv.reader(file, dialect="excel", strict=True)
                try:
                    header = next(reader)
                except StopIteration as error:
                    raise ApplicationError(
                        "invalid_csv_header",
                        f"{self.path} does not contain the required CSV header",
                        3,
                    ) from error
                if header != list(FIELDS):
                    raise ApplicationError(
                        "invalid_csv_header",
                        f"{self.path} must use the exact documented CSV header",
                        3,
                    )
                for record_number, row in enumerate(reader, start=1):
                    # A valid file can contain an invalid event row. Yielding a
                    # shaped RawRecord keeps that failure in per-record reporting;
                    # malformed CSV syntax remains a source-level exception.
                    if len(row) != len(FIELDS) or not any(row):
                        yield RawRecord(
                            str(self.path),
                            record_number,
                            {},
                            "csv",
                            "CSV record must contain exactly six non-blank fields",
                        )
                        continue
                    yield RawRecord(
                        str(self.path),
                        record_number,
                        dict(zip(FIELDS, row, strict=True)),
                        "csv",
                    )
        except ApplicationError:
            # Preserve deliberate validation codes instead of collapsing them into
            # a generic parser or I/O failure.
            raise
        except (UnicodeError, csv.Error) as error:
            raise ApplicationError(
                "invalid_csv",
                f"{self.path} is not valid UTF-8 CSV: {error}",
                3,
            ) from error
        except OSError as error:
            raise ApplicationError(
                "source_unreadable",
                f"could not read {self.path}: {error}",
                4,
            ) from error


class JSONLinesSource:
    """Stream one object per non-blank physical UTF-8 line, in file order.

    Blank lines do not produce records, but physical line numbers remain the
    diagnostic identity. JSON syntax failures abort the source; object-shape
    failures become rejectable records so later valid lines can still be consumed.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if not line.strip():
                        continue
                    try:
                        value: object = json.loads(
                            line,
                            # object_pairs_hook sees duplicates before dict
                            # construction would erase them, including nested ones.
                            object_pairs_hook=_Object,
                            parse_constant=_reject_json_constant,
                        )
                    except ValueError as error:
                        raise ApplicationError(
                            "invalid_jsonl",
                            f"{self.path} line {line_number} is not valid JSON",
                            3,
                            {"line": line_number},
                        ) from error
                    if not isinstance(value, Mapping):
                        yield RawRecord(
                            str(self.path),
                            line_number,
                            {},
                            "jsonl",
                            "JSON Lines record must be an object",
                        )
                    elif _contains_duplicate_members(value):
                        yield RawRecord(
                            str(self.path),
                            line_number,
                            dict(value),
                            "jsonl",
                            "JSON object member names must be unique",
                        )
                    else:
                        yield RawRecord(
                            str(self.path),
                            line_number,
                            cast(Mapping[str, object], value),
                            "jsonl",
                        )
        except ApplicationError:
            # ApplicationError distinguishes invalid source content from an
            # environmental OSError such as a missing or unreadable path.
            raise
        except UnicodeError as error:
            raise ApplicationError(
                "invalid_jsonl",
                f"{self.path} is not UTF-8 JSON Lines",
                3,
            ) from error
        except OSError as error:
            raise ApplicationError(
                "source_unreadable",
                f"could not read {self.path}: {error}",
                4,
            ) from error
