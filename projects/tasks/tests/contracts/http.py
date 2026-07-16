"""Transport-neutral HTTP response assertions shared by all server adapters.

Every framework must emit the same JSON media type, status, and common success
or error envelope.  Exact comparisons are deliberate: a status/error-code
mismatch is an API compatibility bug even when a framework's default payload
would otherwise look reasonable.
"""

import json
from collections.abc import Mapping

from support import HttpResponse


def decode_json(response: HttpResponse) -> object:
    """Decode JSON only after enforcing the common response media type."""

    content_type = response.header("Content-Type")
    assert content_type is not None
    assert content_type.split(";", 1)[0].strip().casefold() == "application/json"
    return json.loads(response.body.decode("utf-8"))


def assert_json_response(
    response: HttpResponse,
    status: int,
    payload: object,
) -> None:
    """Assert status/payload parity without framework response helpers."""

    assert response.status == status
    assert decode_json(response) == payload


def assert_error_response(
    response: HttpResponse,
    status: int,
    code: str,
    message: str,
    *,
    details: Mapping[str, object] | None = None,
) -> None:
    """Assert the status, stable code, message, and optional error details."""

    error: dict[str, object] = {"code": code, "message": message}
    if details is not None:
        error["details"] = dict(details)
    assert_json_response(response, status, {"error": error})


__all__ = ["assert_error_response", "assert_json_response", "decode_json"]
