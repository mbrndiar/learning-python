"""Low-level ``urllib`` transport boundary for milestone three."""

from tasks_core.errors import incomplete

from tasks_cli.transport import TaskTransport, TransportRequest, TransportResponse


class UrllibTransport:
    """Task transport implemented with the Python standard library.

    This milestone makes encoding, Request construction, response ownership and
    exception translation visible before higher-level clients hide those steps.
    """

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def send(self, request: TransportRequest) -> TransportResponse:
        # TODO(milestone 3): build the encoded URL, serialize strict UTF-8 JSON,
        # set headers, and build an opener with ``ProxyHandler({})`` plus a
        # no-redirect handler. Read and close the response, preserve HTTPError as
        # an ordinary response, and translate failures without retrying.
        incomplete(
            "milestone 3 urllib request "
            f"{request.method} {request.path}, "
            f"query={request.query!r}, json={request.json_body!r}"
        )

    def close(self) -> None:
        """Release transport resources once milestone three owns some.

        A plain urllib implementation need not keep a session, but the shared
        protocol still gives every adapter the same explicit cleanup boundary.
        """


def create_transport(base_url: str, timeout: float) -> TaskTransport:
    """Create one standard-library transport."""

    return UrllibTransport(base_url, timeout)


__all__ = ["UrllibTransport", "create_transport"]
