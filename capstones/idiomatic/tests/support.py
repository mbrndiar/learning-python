"""Shared deterministic paths and fakes for milestone tests."""

import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

TEST_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TEST_ROOT.parents[2]
FIXTURES = TEST_ROOT / "fixtures"
FIXED_TIME = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)


@contextmanager
def test_directory() -> Iterator[Path]:
    """Create cleaned test storage below the repository, never in system temp."""

    with TemporaryDirectory(prefix=".idiomatic-test-", dir=TEST_ROOT) as directory:
        yield Path(directory)


class FixedClock:
    def now(self) -> datetime:
        return FIXED_TIME


class FixturePageFetcher:
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
