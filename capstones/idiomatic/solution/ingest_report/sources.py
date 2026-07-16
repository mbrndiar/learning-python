"""Streaming CSV and JSON Lines record sources."""

import csv
import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import cast

from .errors import ApplicationError
from .models import RawRecord
from .validation import FIELDS


class _Object(dict[str, object]):
    duplicate_members: bool

    def __init__(self, pairs: list[tuple[str, object]]):
        super().__init__()
        self.duplicate_members = False
        for key, value in pairs:
            if key in self:
                self.duplicate_members = True
            self[key] = value


def _reject_json_constant(value: str) -> object:
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
    """Yield rows from the one exact UTF-8 comma-separated dialect."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        try:
            with self.path.open("r", encoding="utf-8", newline="") as file:
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
    """Yield one object per non-blank physical UTF-8 line."""

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
