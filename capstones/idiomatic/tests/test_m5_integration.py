"""Milestone 5: HTTP protocol, bounded concurrency, partials, and subprocess CLI."""

import json
import os
import sqlite3
import subprocess
import sys
import threading
import unittest
from collections.abc import Iterator, Mapping
from contextlib import closing, contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from implementation import IMPLEMENTATION, SOURCE_ROOT
from ingest_report.application import ingest_http
from ingest_report.errors import ApplicationError, PartialImportError
from ingest_report.http_source import (
    MAX_RESPONSE_BYTES,
    URLPageFetcher,
    default_executor_factory,
    fetch_http_records,
    validate_loopback_url,
)
from ingest_report.models import ReportFilters
from ingest_report.repository import SQLiteEventRepository
from support import (
    FIXTURES,
    REPOSITORY_ROOT,
    FixedClock,
    FixturePageFetcher,
    test_directory,
)


class _HTTPHandler(BaseHTTPRequestHandler):
    bodies: dict[int, bytes] = {}
    statuses: dict[int, int] = {}

    def do_GET(self) -> None:
        values = parse_qs(urlsplit(self.path).query)
        page = int(values.get("page", ["0"])[0])
        body = self.bodies.get(page, b"missing")
        status = self.statuses.get(page, 200)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def loopback_server(
    bodies: Mapping[int, bytes],
    statuses: Mapping[int, int] | None = None,
) -> Iterator[str]:
    handler = type(
        "ConfiguredHTTPHandler",
        (_HTTPHandler,),
        {"bodies": dict(bodies), "statuses": dict(statuses or {})},
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/events"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


class _ControlledFetcher:
    # Pages 2 and 3 rendezvous so at least two fetches must overlap. Page 2 waits
    # for page 3, allowing completion to differ from page order without relying
    # on the operating system to choose or prove one particular completion order.
    def __init__(self):
        self.lock = threading.Lock()
        self.active = 0
        self.maximum_active = 0
        self.page_three_started = threading.Event()

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
        with self.lock:
            self.active += 1
            self.maximum_active = max(self.maximum_active, self.active)
        try:
            if page == 2:
                if not self.page_three_started.wait(timeout=2):
                    raise AssertionError("page 3 did not start concurrently")
            elif page == 3:
                self.page_three_started.set()
            value: object = json.loads(
                (FIXTURES / "http" / f"page-{page}.json").read_text(encoding="utf-8")
            )
            assert isinstance(value, dict)
            return value
        finally:
            with self.lock:
                self.active -= 1


class _CancellingFetcher:
    # With one worker, the call log exposes which fetches begin execution. It does
    # not observe Executor.submit calls or cancellation of queued futures.
    def __init__(self):
        self.calls: list[int] = []

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
        self.calls.append(page)
        if page == 1:
            return {"page": 1, "page_count": 5, "items": []}
        raise KeyboardInterrupt


class IntegrationTests(unittest.TestCase):
    def test_bounded_fetch_is_deterministic_despite_completion_order(self):
        # Milestone 5 owns bounded concurrent retrieval and ordered assembly.
        # maximum_active measures in-flight fetch_page calls: it must reach two
        # but never exceed workers. Records must still be emitted in page order.
        # The rendezvous proves overlap, not deterministic thread scheduling.
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        fetcher = _ControlledFetcher()
        fetched = fetch_http_records(
            "http://127.0.0.1/events",
            fetcher,
            workers=2,
            allow_partial=False,
        )
        self.assertLessEqual(fetcher.maximum_active, 2)
        self.assertGreaterEqual(fetcher.maximum_active, 2)
        self.assertEqual(
            [record.raw["id"] for record in fetched.records],
            ["http-001", "http-002", "http-003"],
        )

    def test_cancellation_stops_scheduling_and_owned_workers_join(self):
        # KeyboardInterrupt must escape. With one worker, the call log proves pages
        # 3-5 never begin execution; it does not independently prove submission,
        # cancellation of queued futures, executor shutdown, or thread joining.
        fetcher = _CancellingFetcher()
        with self.assertRaises(KeyboardInterrupt):
            fetch_http_records(
                "http://127.0.0.1/events",
                fetcher,
                workers=1,
                allow_partial=False,
            )
        self.assertEqual(fetcher.calls, [1, 2])

    def test_strict_failure_rolls_back_and_partial_failure_commits(self):
        # Strict mode treats any page failure as an atomic import failure. Partial
        # mode commits successful pages in one explicitly marked import and then
        # raises a result-bearing error so the CLI can report incomplete success.
        failure = ApplicationError(
            "page_fetch_failed",
            "injected page failure",
            4,
            {"page": 2},
        )
        with test_directory() as directory:
            strict_database = directory / "strict.db"
            strict_repository = SQLiteEventRepository(strict_database)
            with self.assertRaises(ApplicationError):
                ingest_http(
                    repository=strict_repository,
                    import_id="strict",
                    base_url="http://127.0.0.1/events",
                    clock=FixedClock(),
                    fetcher=FixturePageFetcher({2: failure}),
                    workers=2,
                    allow_partial=False,
                    executor_factory=default_executor_factory,
                )
            self.assertEqual(
                strict_repository.report(ReportFilters()).totals.events,
                0,
            )
            with closing(sqlite3.connect(strict_database)) as connection:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM imports").fetchone()[0],
                    0,
                )

            partial_repository = SQLiteEventRepository(directory / "partial.db")
            with self.assertRaises(PartialImportError) as caught:
                ingest_http(
                    repository=partial_repository,
                    import_id="partial",
                    base_url="http://127.0.0.1/events",
                    clock=FixedClock(),
                    fetcher=FixturePageFetcher({2: failure}),
                    workers=2,
                    allow_partial=True,
                    executor_factory=default_executor_factory,
                )
            result = caught.exception.result
            self.assertEqual(
                (
                    result.state,
                    result.accepted,
                    result.failed_pages,
                    partial_repository.report(ReportFilters()).totals.events,
                ),
                ("partial", 2, (2,), 2),
            )

    def test_loopback_adapter_covers_valid_malformed_and_body_bound_pages(self):
        # A loopback server exercises the concrete URL fetcher while keeping all
        # responses controlled: valid JSON, malformed JSON, and the byte ceiling.
        pages = {
            page: (FIXTURES / "http" / f"page-{page}.json").read_bytes()
            for page in range(1, 4)
        }
        with loopback_server(pages) as base_url:
            payload = URLPageFetcher().fetch_page(base_url, 1)
            self.assertEqual(payload["page"], 1)

        with loopback_server({1: b"{broken"}) as base_url:
            with self.assertRaises(ApplicationError) as malformed:
                URLPageFetcher().fetch_page(base_url, 1)
            self.assertEqual(malformed.exception.code, "invalid_page")

        with loopback_server({1: b"x" * (MAX_RESPONSE_BYTES + 1)}) as base_url:
            with self.assertRaises(ApplicationError) as oversized:
                URLPageFetcher().fetch_page(base_url, 1)
            self.assertEqual(oversized.exception.code, "invalid_page")

        with self.assertRaises(ApplicationError):
            validate_loopback_url("https://example.com/events")

    def test_page_protocol_validation_and_partial_collection(self):
        # Cross-page metadata is part of the protocol, not trusted payload data.
        # Strict mode aborts on mismatch; partial mode records that page as failed
        # and preserves successful records in ascending page order.
        class MismatchedFetcher(FixturePageFetcher):
            def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
                payload = dict(super().fetch_page(base_url, page))
                if page == 2:
                    payload["page_count"] = 99
                return payload

        with self.assertRaises(ApplicationError) as strict:
            fetch_http_records(
                "http://127.0.0.1/events",
                MismatchedFetcher(),
                workers=2,
                allow_partial=False,
            )
        self.assertEqual(strict.exception.code, "invalid_page")
        partial = fetch_http_records(
            "http://127.0.0.1/events",
            MismatchedFetcher(),
            workers=2,
            allow_partial=True,
        )
        self.assertEqual(partial.failed_pages, (2,))
        self.assertEqual(
            [record.raw["id"] for record in partial.records],
            ["http-001", "http-003"],
        )

    def test_cli_partial_import_outputs_result_and_source_io_exit(self):
        pages = {
            page: (FIXTURES / "http" / f"page-{page}.json").read_bytes()
            for page in range(1, 4)
        }
        with (
            test_directory() as directory,
            loopback_server(pages, {2: 500}) as base_url,
        ):
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ingest_report",
                    "--json-errors",
                    "--db",
                    str(directory / "events.db"),
                    "ingest",
                    "--import-id",
                    "partial-cli",
                    "--format",
                    "http",
                    "--url",
                    base_url,
                    "--allow-partial",
                ],
                cwd=REPOSITORY_ROOT,
                env={**os.environ, "PYTHONPATH": str(SOURCE_ROOT)},
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(process.returncode, 4)
        result = json.loads(process.stdout)
        self.assertEqual(
            (result["state"], result["accepted"], result["failed_pages"]),
            ("partial", 2, [2]),
        )
        self.assertEqual(
            json.loads(process.stderr)["error"]["code"],
            "partial_import",
        )

    def test_subprocess_cli_ingest_report_and_failure_envelope(self):
        with test_directory() as directory:
            database = directory / "events.db"
            environment = {
                **os.environ,
                "PYTHONPATH": str(SOURCE_ROOT),
            }
            ingest = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ingest_report",
                    "--db",
                    str(database),
                    "ingest",
                    "--import-id",
                    "subprocess",
                    "--format",
                    "csv",
                    "--input",
                    str(FIXTURES / "events-valid.csv"),
                ],
                cwd=REPOSITORY_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(ingest.returncode, 0, ingest.stderr)
            self.assertEqual(json.loads(ingest.stdout)["accepted"], 4)
            self.assertEqual(ingest.stderr, "")

            report = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ingest_report",
                    "--db",
                    str(database),
                    "report",
                    "--output",
                    "json",
                ],
                cwd=REPOSITORY_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertEqual(json.loads(report.stdout)["totals"]["events"], 4)

            duplicate = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ingest_report",
                    "--json-errors",
                    "--db",
                    str(database),
                    "ingest",
                    "--import-id",
                    "subprocess",
                    "--format",
                    "csv",
                    "--input",
                    str(FIXTURES / "events-valid.csv"),
                ],
                cwd=REPOSITORY_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(duplicate.returncode, 5)
            self.assertEqual(
                json.loads(duplicate.stderr)["error"]["code"], "import_exists"
            )
            self.assertNotIn("Traceback", duplicate.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
