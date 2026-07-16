"""HTTPX transport boundary for milestone five."""

from types import TracebackType

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class HttpxTransport:
    """Task transport that will own an ``httpx.Client``."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        # TODO(milestone 5): send with params/json, capture status/body, and
        # translate HTTPX timeout and HTTP errors without retrying.
        incomplete(
            "milestone 5 httpx call "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """TODO: idempotently close the owned ``httpx.Client``."""

    def __enter__(self) -> "HttpxTransport":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exception_type, exception, traceback
        self.close()


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create the guided HTTPX transport for one CLI invocation."""

    return HttpxTransport(base_url, timeout)


__all__ = ["HttpxTransport", "create_transport"]
