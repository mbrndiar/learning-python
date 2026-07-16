"""HTTPX transport boundary for milestone five."""

from types import TracebackType

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class HttpxTransport:
    """Task transport that will own one synchronous ``httpx.Client``.

    Keep Client construction and cleanup in the adapter so the shared command
    application remains independent of HTTPX and can use the same lifecycle.
    """

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        # TODO(milestone 5): send with params/json, capture status/body, and
        # translate timeout, connection, and other HTTPX request failures to the
        # shared categories without retrying.
        incomplete(
            "milestone 5 httpx call "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """TODO: idempotently close the owned ``httpx.Client``."""

    def __enter__(self) -> "HttpxTransport":
        # Returning self lets tests or callers use the same explicit owner with
        # `with`; __exit__ funnels cleanup through the idempotent close method.
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
