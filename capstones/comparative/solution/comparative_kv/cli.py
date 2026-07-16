"""Exact command grammar, validation precedence, and JSON envelopes."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from contextlib import closing
from typing import NoReturn, cast

from .domain import (
    parse_delete_expectation,
    parse_json_value,
    parse_set_expectation,
    validate_key,
)
from .errors import KvError
from .models import (
    DeleteExpectation,
    DeleteResult,
    Entry,
    JsonValue,
    ListResult,
    SetExpectation,
    SetResult,
)
from .store import open_store


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise KvError("usage", {"reason": "invalid_cli"}, 2)


def build_parser() -> argparse.ArgumentParser:
    """Build the four documented parser shapes for Python callers."""

    parser = _ArgumentParser(
        prog="comparative-kv",
        description="A versioned SQLite key/value configuration store",
        allow_abbrev=False,
        add_help=False,
    )
    parser.add_argument("--db", required=True, metavar="PATH")
    commands = parser.add_subparsers(dest="command", required=True)

    set_parser = commands.add_parser("set", allow_abbrev=False, add_help=False)
    set_parser.add_argument("key", metavar="KEY")
    set_parser.add_argument("--value-json", required=True, dest="value_json")
    set_parser.add_argument("--expect", default="any")

    get_parser = commands.add_parser("get", allow_abbrev=False, add_help=False)
    get_parser.add_argument("key", metavar="KEY")

    delete_parser = commands.add_parser("delete", allow_abbrev=False, add_help=False)
    delete_parser.add_argument("key", metavar="KEY")
    delete_parser.add_argument("--expect", default="any")

    commands.add_parser("list", allow_abbrev=False, add_help=False)
    return parser


def _parse_exact(arguments: Sequence[str]) -> argparse.Namespace:
    if len(arguments) < 3 or arguments[0] != "--db":
        raise KvError("usage", {"reason": "invalid_cli"}, 2)
    database = arguments[1]
    command = arguments[2]
    if command == "list" and len(arguments) == 3:
        return argparse.Namespace(db=database, command=command)
    if command == "get" and len(arguments) == 4:
        return argparse.Namespace(db=database, command=command, key=arguments[3])
    if command == "delete" and len(arguments) == 4:
        return argparse.Namespace(
            db=database,
            command=command,
            key=arguments[3],
            expect="any",
        )
    if command == "delete" and len(arguments) == 6 and arguments[4] == "--expect":
        return argparse.Namespace(
            db=database,
            command=command,
            key=arguments[3],
            expect=arguments[5],
        )
    if command == "set" and len(arguments) == 6 and arguments[4] == "--value-json":
        return argparse.Namespace(
            db=database,
            command=command,
            key=arguments[3],
            value_json=arguments[5],
            expect="any",
        )
    if (
        command == "set"
        and len(arguments) == 8
        and arguments[4] == "--value-json"
        and arguments[6] == "--expect"
    ):
        return argparse.Namespace(
            db=database,
            command=command,
            key=arguments[3],
            value_json=arguments[5],
            expect=arguments[7],
        )
    raise KvError("usage", {"reason": "invalid_cli"}, 2)


def _validate_database_path(path: str) -> None:
    if path == "":
        raise KvError(
            "invalid_argument",
            {"field": "db", "reason": "empty"},
            2,
        )
    if path == ":memory:" or path.startswith("file:"):
        raise KvError(
            "invalid_argument",
            {"field": "db", "reason": "unsupported_form"},
            2,
        )


def run(arguments: argparse.Namespace) -> int:
    """Validate and execute one parsed command."""

    _validate_database_path(cast(str, arguments.db))
    command = cast(str, arguments.command)
    key: str | None = None
    set_expectation: SetExpectation = "any"
    delete_expectation: DeleteExpectation = "any"
    value: JsonValue = None
    if command in ("set", "get", "delete"):
        key = validate_key(cast(str, arguments.key))
    if command == "set":
        set_expectation = parse_set_expectation(cast(str, arguments.expect))
        value = parse_json_value(cast(str, arguments.value_json))
    elif command == "delete":
        delete_expectation = parse_delete_expectation(cast(str, arguments.expect))

    with closing(open_store(cast(str, arguments.db))) as store:
        if command == "set":
            assert key is not None
            result = _set_result(store.set(key, value, set_expectation))
        elif command == "get":
            assert key is not None
            result = _entry(store.get(key))
        elif command == "delete":
            assert key is not None
            result = _delete_result(store.delete(key, delete_expectation))
        else:
            result = _list_result(store.list_entries())
    _write({"ok": True, "result": result})
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Always emit one compact JSON line and return its normative exit code."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        return run(_parse_exact(arguments))
    except KvError as error:
        _write(error.envelope())
        return error.exit_code
    except Exception:
        unexpected_error = KvError(
            "storage_error",
            {"operation": "open", "reason": "storage_failure"},
            5,
        )
        _write(unexpected_error.envelope())
        return unexpected_error.exit_code


def _entry(entry: Entry) -> dict[str, object]:
    return {
        "key": entry.key,
        "value": entry.value,
        "revision": entry.revision,
    }


def _set_result(result: SetResult) -> dict[str, object]:
    return {**_entry(result.entry), "created": result.created}


def _delete_result(result: DeleteResult) -> dict[str, object]:
    return {
        "key": result.key,
        "deleted_revision": result.deleted_revision,
        "revision": result.revision,
    }


def _list_result(result: ListResult) -> dict[str, object]:
    return {
        "entries": [_entry(entry) for entry in result.entries],
        "global_revision": result.global_revision,
    }


def _write(envelope: dict[str, object]) -> None:
    sys.stdout.write(
        json.dumps(envelope, ensure_ascii=True, separators=(",", ":")) + "\n"
    )
