"""Command parser and process-safe execution boundary."""

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import NoReturn, cast

from .application import ingest_http, ingest_source
from .errors import ApplicationError, PartialImportError
from .http_source import URLPageFetcher, default_executor_factory, validate_loopback_url
from .models import ReportFilters, SourceKind, Status
from .reporting import import_result_dict, render_json, render_text, report_dict
from .repository import SQLiteEventRepository
from .sources import CSVSource, JSONLinesSource
from .validation import (
    normalize_filter_timestamp,
    validate_import_id,
)


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ApplicationError("invalid_argument", message, 2)


class SystemClock:
    """Supply current UTC time at the injectable application boundary."""

    def now(self) -> datetime:
        return datetime.now(UTC)


def build_parser() -> argparse.ArgumentParser:
    """Build every documented ingest/report command shape."""

    parser = _ArgumentParser(
        prog="ingest-report",
        description="Ingest operational events and produce reports",
        allow_abbrev=False,
    )
    parser.add_argument("--db", required=True, metavar="PATH")
    parser.add_argument("--json-errors", action="store_true")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="command", required=True)

    ingest_parser = commands.add_parser("ingest", allow_abbrev=False)
    ingest_parser.add_argument("--import-id", required=True)
    ingest_parser.add_argument(
        "--format",
        choices=("csv", "jsonl", "http"),
        required=True,
    )
    ingest_parser.add_argument("--input")
    ingest_parser.add_argument("--url")
    ingest_parser.add_argument("--workers", type=int, default=4)
    ingest_parser.add_argument("--allow-partial", action="store_true")

    report_parser = commands.add_parser("report", allow_abbrev=False)
    report_parser.add_argument("--from", dest="from_timestamp")
    report_parser.add_argument("--to", dest="to_timestamp")
    report_parser.add_argument("--category")
    report_parser.add_argument("--status", choices=("success", "warning", "failure"))
    report_parser.add_argument("--output", choices=("json", "text"), default="text")
    return parser


def _report_filters(arguments: argparse.Namespace) -> ReportFilters:
    from_timestamp = (
        normalize_filter_timestamp(arguments.from_timestamp, "from")
        if arguments.from_timestamp is not None
        else None
    )
    to_timestamp = (
        normalize_filter_timestamp(arguments.to_timestamp, "to")
        if arguments.to_timestamp is not None
        else None
    )
    if (
        from_timestamp is not None
        and to_timestamp is not None
        and from_timestamp > to_timestamp
    ):
        raise ApplicationError(
            "invalid_filter",
            "from timestamp must not be later than to timestamp",
            2,
        )
    category = arguments.category
    if category is not None:
        category = category.strip()
        if not category:
            raise ApplicationError(
                "invalid_filter",
                "category filter must not be blank",
                2,
                {"field": "category"},
            )
    return ReportFilters(
        from_timestamp,
        to_timestamp,
        category,
        cast(Status | None, arguments.status),
    )


def run(arguments: argparse.Namespace) -> int:
    """Execute parsed arguments and write successful data to stdout only."""

    if arguments.command == "report":
        filters = _report_filters(arguments)
        report = SQLiteEventRepository(Path(arguments.db)).report(filters)
        if arguments.output == "json":
            sys.stdout.write(render_json(report_dict(report)))
        else:
            sys.stdout.write(render_text(report))
        return 0

    source_format = cast(str, arguments.format)
    validate_import_id(arguments.import_id)
    if not 1 <= arguments.workers <= 16:
        raise ApplicationError(
            "invalid_argument",
            "workers must be from 1 through 16",
            2,
            {"field": "workers"},
        )
    if source_format == "http":
        if arguments.url is None or arguments.input is not None:
            raise ApplicationError(
                "invalid_argument",
                "HTTP imports require --url and do not accept --input",
                2,
            )
        validate_loopback_url(arguments.url)
        repository = SQLiteEventRepository(Path(arguments.db))
        result = ingest_http(
            repository=repository,
            import_id=arguments.import_id,
            base_url=arguments.url,
            clock=SystemClock(),
            fetcher=URLPageFetcher(),
            workers=arguments.workers,
            allow_partial=arguments.allow_partial,
            executor_factory=default_executor_factory,
        )
    else:
        if (
            arguments.input is None
            or arguments.url is not None
            or arguments.allow_partial
        ):
            raise ApplicationError(
                "invalid_argument",
                "file imports require --input and do not accept HTTP-only options",
                2,
            )
        source = (
            CSVSource(arguments.input)
            if source_format == "csv"
            else JSONLinesSource(arguments.input)
        )
        repository = SQLiteEventRepository(Path(arguments.db))
        result = ingest_source(
            repository=repository,
            source=source,
            import_id=arguments.import_id,
            source_kind=cast(SourceKind, source_format),
            source_name=str(arguments.input),
            clock=SystemClock(),
        )
    sys.stdout.write(render_json(import_result_dict(result)))
    return 0


def _write_error(error: ApplicationError, json_errors: bool) -> None:
    if json_errors:
        sys.stderr.write(render_json(error.envelope()))
    else:
        sys.stderr.write(f"error[{error.code}]: {error.message}\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Return a stable exit code and suppress unexpected tracebacks by default."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    json_errors = "--json-errors" in arguments
    debug = "--debug" in arguments
    try:
        parsed = build_parser().parse_args(arguments)
        return run(parsed)
    except PartialImportError as error:
        sys.stdout.write(render_json(import_result_dict(error.result)))
        _write_error(error, json_errors)
        return error.exit_code
    except ApplicationError as error:
        _write_error(error, json_errors)
        return error.exit_code
    except KeyboardInterrupt:
        cancelled = ApplicationError("cancelled", "operation cancelled", 130)
        _write_error(cancelled, json_errors)
        return cancelled.exit_code
    except SystemExit as error:
        return int(error.code or 0)
    except Exception as error:
        if debug:
            raise
        unexpected = ApplicationError(
            "unexpected_error",
            "unexpected error",
            5,
            {"type": type(error).__name__},
        )
        _write_error(unexpected, json_errors)
        return unexpected.exit_code
