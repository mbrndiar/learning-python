"""Milestone 5 starter: loopback URL policy and bounded page concurrency.

The transport boundary accepts only the specification's unauthenticated
loopback URLs and bounded page responses.  The coordinator fetches page 1
before parallel work, limits in-flight calls, restores page order, and owns
cancellation plus executor cleanup. Tests inject fetchers; executor creation
remains injectable for independently observable lifecycle tests.
"""

from collections.abc import Mapping
from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass

from .errors import incomplete
from .models import RawRecord
from .protocols import ExecutorFactory, PageFetcher


class URLPageFetcher:
    """Fetch one bounded page without redirects, cookies, or authentication.

    Validate the URL spelling before transport, then validate response status and
    byte/JSON bounds before returning an untrusted mapping. Textual loopback
    validation does not itself prevent ambient proxy routing, so make direct
    transport policy a separate invariant alongside redirect handling. The
    coordinator owns page metadata and item validation.
    """

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
        """Request ``page=N`` and validate the bounded UTF-8 JSON response."""

        incomplete(f"milestone 5 HTTP page {page} from {base_url}")


@dataclass(frozen=True, slots=True)
class HTTPFetchResult:
    """Successful records and failed pages collected in deterministic order.

    Completion order may differ from source order and is never used as output
    order: records use ascending page number then item position, while failed
    page numbers are stable for persistence and rendering.
    """

    records: tuple[RawRecord, ...]
    failed_pages: tuple[int, ...]


def default_executor_factory(max_workers: int) -> Executor:
    """Create the worker pool through the required injection seam.

    The caller owns shutdown and joining; the factory only creates the bounded
    executor so tests can observe lifecycle behavior.
    """

    return ThreadPoolExecutor(max_workers=max_workers)


def fetch_http_records(
    base_url: str,
    fetcher: PageFetcher,
    workers: int,
    allow_partial: bool,
    executor_factory: ExecutorFactory = default_executor_factory,
) -> HTTPFetchResult:
    """Fetch page 1 first, then own bounded scheduling and deterministic cleanup.

    Page 1 establishes the pagination contract before other work exists.  At
    most ``workers`` calls may be active; strict failure or cancellation stops
    further scheduling, cancels what can be cancelled, and joins owned workers.
    Partial mode retains valid pages but applies the same protocol checks.
    """

    # TODO(m5): reason from the bounded-concurrency, ordering, and cancellation
    # tests; do not let future completion order become record order.
    incomplete(
        f"milestone 5 HTTP paging for {base_url} "
        f"(workers={workers}, partial={allow_partial}, "
        f"factory={executor_factory}, fetcher={fetcher})"
    )
