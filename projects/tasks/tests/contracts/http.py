"""Shared assertions for every black-box Task HTTP server."""

import json
from collections.abc import Mapping

from support import HttpResponse


def decode_json(response: HttpResponse) -> object:
    """Decode one strict UTF-8 JSON response."""

    content_type = response.header("Content-Type")
    assert content_type is not None
    assert content_type.split(";", 1)[0].strip().casefold() == "application/json"
    return json.loads(response.body.decode("utf-8"))


def assert_json_response(
    response: HttpResponse,
    status: int,
    payload: object,
) -> None:
    """Assert exact status and decoded JSON payload."""

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
    """Assert the exact shared error envelope."""

    error: dict[str, object] = {"code": code, "message": message}
    if details is not None:
        error["details"] = dict(details)
    assert_json_response(response, status, {"error": error})


__all__ = ["assert_error_response", "assert_json_response", "decode_json"]
