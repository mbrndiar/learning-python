"""Loopback HTTP paging with bounded, deterministic concurrency."""

import json
from collections.abc import Mapping
from concurrent.futures import (
    FIRST_COMPLETED,
    Executor,
    Future,
    ThreadPoolExecutor,
    wait,
)
from dataclasses import dataclass
from email.message import Message
from http.client import HTTPResponse
from typing import IO, cast
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .errors import ApplicationError
from .models import RawRecord
from .protocols import ExecutorFactory, PageFetcher

MAX_RESPONSE_BYTES = 1024 * 1024
MAX_ITEMS = 1000
MAX_PAGES = 100


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: Message,
        newurl: str,
    ) -> Request | None:
        return None


class _JSONObject(dict[str, object]):
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


def _has_duplicates(value: object) -> bool:
    if isinstance(value, _JSONObject):
        return value.duplicate_members or any(
            _has_duplicates(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_has_duplicates(item) for item in value)
    return False


def validate_loopback_url(base_url: str) -> None:
    """Reject non-HTTP or non-loopback URLs before opening a connection."""

    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "::1", "localhost"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ApplicationError(
            "invalid_argument",
            "HTTP source URL must be an unauthenticated loopback http:// URL",
            2,
            {"field": "url"},
        )


class URLPageFetcher:
    """Fetch one bounded JSON page with the standard library."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._opener = build_opener(_NoRedirects())

    @staticmethod
    def _page_url(base_url: str, page: int) -> str:
        parsed = urlsplit(base_url)
        query = [
            (key, value) for key, value in parse_qsl(parsed.query) if key != "page"
        ]
        query.append(("page", str(page)))
        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                urlencode(query),
                parsed.fragment,
            )
        )

    def fetch_page(self, base_url: str, page: int) -> Mapping[str, object]:
        validate_loopback_url(base_url)
        request = Request(
            self._page_url(base_url, page),
            method="GET",
            headers={"Accept": "application/json"},
        )
        try:
            response = cast(
                HTTPResponse,
                self._opener.open(request, timeout=self.timeout),
            )
            with response:
                content_length = response.headers.get("Content-Length")
                if content_length is not None:
                    try:
                        declared_length = int(content_length)
                    except ValueError as error:
                        raise ApplicationError(
                            "invalid_page",
                            f"page {page} has an invalid Content-Length",
                            3,
                            {"page": page},
                        ) from error
                    if declared_length > MAX_RESPONSE_BYTES:
                        raise ApplicationError(
                            "invalid_page",
                            f"page {page} exceeds the 1 MiB response limit",
                            3,
                            {"page": page},
                        )
                body = response.read(MAX_RESPONSE_BYTES + 1)
        except ApplicationError:
            raise
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise ApplicationError(
                "page_fetch_failed",
                f"could not fetch page {page}: {error}",
                4,
                {"page": page},
            ) from error
        if len(body) > MAX_RESPONSE_BYTES:
            raise ApplicationError(
                "invalid_page",
                f"page {page} exceeds the 1 MiB response limit",
                3,
                {"page": page},
            )
        try:
            value: object = json.loads(
                body.decode("utf-8"),
                object_pairs_hook=_JSONObject,
                parse_constant=_reject_json_constant,
            )
        except (UnicodeError, ValueError) as error:
            raise ApplicationError(
                "invalid_page",
                f"page {page} is not valid UTF-8 JSON",
                3,
                {"page": page},
            ) from error
        if _has_duplicates(value) or not isinstance(value, Mapping):
            raise ApplicationError(
                "invalid_page",
                f"page {page} must be a JSON object with unique member names",
                3,
                {"page": page},
            )
        return cast(Mapping[str, object], value)


@dataclass(frozen=True, slots=True)
class HTTPFetchResult:
    """Successful records and failed pages collected in page order."""

    records: tuple[RawRecord, ...]
    failed_pages: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class _ValidatedPage:
    page: int
    page_count: int
    items: tuple[RawRecord, ...]


def _validate_page(
    payload: Mapping[str, object],
    expected_page: int,
    expected_page_count: int | None,
    source_name: str,
) -> _ValidatedPage:
    if set(payload) != {"page", "page_count", "items"}:
        raise ApplicationError(
            "invalid_page",
            f"page {expected_page} must contain exactly page, page_count, and items",
            3,
            {"page": expected_page},
        )
    page = payload["page"]
    page_count = payload["page_count"]
    items = payload["items"]
    if isinstance(page, bool) or not isinstance(page, int) or page != expected_page:
        raise ApplicationError(
            "invalid_page",
            f"page response does not match requested page {expected_page}",
            3,
            {"page": expected_page},
        )
    if (
        isinstance(page_count, bool)
        or not isinstance(page_count, int)
        or not 1 <= page_count <= MAX_PAGES
        or (expected_page_count is not None and page_count != expected_page_count)
    ):
        raise ApplicationError(
            "invalid_page",
            f"page {expected_page} has an invalid page_count",
            3,
            {"page": expected_page},
        )
    if not isinstance(items, list) or len(items) > MAX_ITEMS:
        raise ApplicationError(
            "invalid_page",
            f"page {expected_page} must contain at most 1000 items",
            3,
            {"page": expected_page},
        )
    records: list[RawRecord] = []
    for position, item in enumerate(items, start=1):
        if not isinstance(item, Mapping):
            records.append(
                RawRecord(
                    source_name,
                    position,
                    {},
                    "http",
                    "HTTP page item must be an object",
                )
            )
        elif not all(isinstance(key, str) for key in item):
            records.append(
                RawRecord(
                    source_name,
                    position,
                    {},
                    "http",
                    "HTTP page item member names must be strings",
                )
            )
        else:
            records.append(
                RawRecord(
                    source_name,
                    position,
                    cast(Mapping[str, object], item),
                    "http",
                )
            )
    return _ValidatedPage(page, page_count, tuple(records))


def default_executor_factory(max_workers: int) -> Executor:
    """Create the owned worker pool through an injectable seam."""

    return ThreadPoolExecutor(max_workers=max_workers)


def fetch_http_records(
    base_url: str,
    fetcher: PageFetcher,
    workers: int,
    allow_partial: bool,
    executor_factory: ExecutorFactory = default_executor_factory,
) -> HTTPFetchResult:
    """Fetch pages with bounded scheduling and deterministic page collection."""

    if not 1 <= workers <= 16:
        raise ApplicationError(
            "invalid_argument",
            "workers must be from 1 through 16",
            2,
            {"field": "workers"},
        )
    first = _validate_page(fetcher.fetch_page(base_url, 1), 1, None, base_url)
    pages: dict[int, _ValidatedPage] = {1: first}
    failures: list[int] = []
    if first.page_count == 1:
        return HTTPFetchResult(first.items, ())

    executor = executor_factory(workers)
    pending: dict[Future[Mapping[str, object]], int] = {}
    next_page = 2
    try:
        while next_page <= first.page_count and len(pending) < workers:
            future = executor.submit(fetcher.fetch_page, base_url, next_page)
            pending[future] = next_page
            next_page += 1
        while pending:
            completed, _ = wait(tuple(pending), return_when=FIRST_COMPLETED)
            for future in sorted(completed, key=lambda item: pending[item]):
                page_number = pending.pop(future)
                try:
                    payload = future.result()
                    pages[page_number] = _validate_page(
                        payload,
                        page_number,
                        first.page_count,
                        base_url,
                    )
                except ApplicationError:
                    if not allow_partial:
                        for unfinished in pending:
                            unfinished.cancel()
                        raise
                    failures.append(page_number)
                except Exception as error:
                    if not allow_partial:
                        for unfinished in pending:
                            unfinished.cancel()
                        raise ApplicationError(
                            "page_fetch_failed",
                            f"could not fetch page {page_number}: {error}",
                            4,
                            {"page": page_number},
                        ) from error
                    failures.append(page_number)
            while next_page <= first.page_count and len(pending) < workers:
                future = executor.submit(fetcher.fetch_page, base_url, next_page)
                pending[future] = next_page
                next_page += 1
    finally:
        for future in pending:
            future.cancel()
        executor.shutdown(wait=True, cancel_futures=True)

    ordered_records = tuple(
        record for page_number in sorted(pages) for record in pages[page_number].items
    )
    return HTTPFetchResult(ordered_records, tuple(sorted(failures)))
