"""Milestone 5 starter: loopback HTTP and bounded page concurrency."""

from collections.abc import Mapping
from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass

from .errors import incomplete
from .models import RawRecord
from .protocols import ExecutorFactory, PageFetcher


class URLPageFetcher:
    """Fetch one bounded page without redirects, cookies, or authentication."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
        """Request ``page=N`` and validate UTF-8 JSON response bounds."""

        incomplete(f"milestone 5 HTTP page {page} from {base_url}")


@dataclass(frozen=True, slots=True)
class HTTPFetchResult:
    """Successful records and failed pages collected in page order."""

    records: tuple[RawRecord, ...]
    failed_pages: tuple[int, ...]


def default_executor_factory(max_workers: int) -> Executor:
    """Create the worker pool through the required injection seam."""

    return ThreadPoolExecutor(max_workers=max_workers)


def fetch_http_records(
    base_url: str,
    fetcher: PageFetcher,
    workers: int,
    allow_partial: bool,
    executor_factory: ExecutorFactory = default_executor_factory,
) -> HTTPFetchResult:
    """Fetch page 1 first, then own bounded scheduling and deterministic cleanup."""

    # TODO(m5): stop scheduling on strict failure/cancellation and always join.
    incomplete(
        f"milestone 5 HTTP paging for {base_url} "
        f"(workers={workers}, partial={allow_partial}, "
        f"factory={executor_factory}, fetcher={fetcher})"
    )
