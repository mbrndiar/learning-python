"""Shared deterministic paths and fakes for milestone tests."""

import json
import os
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

TEST_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TEST_ROOT.parents[2]
FIXTURES = TEST_ROOT / "fixtures"
FIXED_TIME = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)


def cli_program() -> list[str]:
    """Return the public CLI command, optionally measured in subprocesses."""

    if os.environ.get("CAPSTONE_SUBPROCESS_COVERAGE") == "1":
        return [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--parallel-mode",
            "-m",
            "ingest_report",
        ]
    return [sys.executable, "-m", "ingest_report"]


@contextmanager
def test_directory() -> Iterator[Path]:
    """Create cleaned test storage below the repository, never in system temp."""

    # Keeping transient databases inside the test tree constrains their location
    # while TemporaryDirectory still provides unique paths and per-test cleanup.
    with TemporaryDirectory(prefix=".idiomatic-test-", dir=TEST_ROOT) as directory:
        yield Path(directory)


class FixedClock:
    # Ingestion metadata must be reproducible without coupling tests to wall time.
    def now(self) -> datetime:
        return FIXED_TIME


class FixturePageFetcher:
    # This fake controls page payloads and failures without exercising networking;
    # the loopback tests cover the concrete HTTP adapter separately.
    def __init__(self, failures: Mapping[int, Exception] | None = None):
        self.failures = dict(failures or {})
        self.calls: list[int] = []

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
        self.calls.append(page)
        failure = self.failures.get(page)
        if failure is not None:
            raise failure
        value: object = json.loads(
            (FIXTURES / "http" / f"page-{page}.json").read_text(encoding="utf-8")
        )
        assert isinstance(value, dict)
        return value
