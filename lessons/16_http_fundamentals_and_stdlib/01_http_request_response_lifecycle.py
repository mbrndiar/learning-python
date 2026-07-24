"""
Chapter 16, Lesson 1: HTTP Request and Response Lifecycle

Purpose: model one HTTP exchange as plain values, then make JSON serialization,
UTF-8 encoding, status selection, header lookup, and byte lengths observable.

Prerequisite: bytes and JSON from Chapters 2 and 8, plus dataclasses from
Chapter 9.

Run from the repository root:

    python lessons/16_http_fundamentals_and_stdlib/01_http_request_response_lifecycle.py
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus


@dataclass(frozen=True)
class HttpRequest:
    method: str
    target: str
    headers: Mapping[str, str]
    body: bytes = b""


@dataclass(frozen=True)
class HttpResponse:
    status: HTTPStatus
    headers: Mapping[str, str]
    body: bytes


# Step 1: HTTP field names are case-insensitive. A plain dict is not, so the
# boundary compares normalized names instead of relying on one capitalization.
def header_value(headers: Mapping[str, str], name: str) -> str | None:
    wanted = name.casefold()
    return next(
        (value for key, value in headers.items() if key.casefold() == wanted),
        None,
    )


# Step 2: serialize a Python value to JSON text, then encode that text to the
# bytes carried by HTTP. Content-Length counts those bytes.
def json_response(status: HTTPStatus, payload: object) -> HttpResponse:
    body = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return HttpResponse(
        status,
        {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body)),
        },
        body,
    )


def error_response(
    status: HTTPStatus,
    code: str,
    message: str,
    *,
    allow: str | None = None,
) -> HttpResponse:
    response = json_response(
        status,
        {"error": {"code": code, "message": message}},
    )
    if allow is None:
        return response
    return HttpResponse(
        response.status,
        {**response.headers, "Allow": allow},
        response.body,
    )


# Step 3: dispatch by path and method. The pure function has no socket, global
# server, or framework object, so every branch is easy to run deterministically.
def dispatch_request(request: HttpRequest) -> HttpResponse:
    method = request.method.upper()

    if request.target == "/health":
        if method != "GET":
            return error_response(
                HTTPStatus.METHOD_NOT_ALLOWED,
                "method_not_allowed",
                "method is not allowed for this path",
                allow="GET",
            )
        return json_response(HTTPStatus.OK, {"status": "ok"})

    if request.target == "/tasks" and method == "POST":
        content_type = header_value(request.headers, "Content-Type")
        if content_type is None or content_type.split(";", 1)[0].strip() != (
            "application/json"
        ):
            return error_response(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "unsupported_media_type",
                "Content-Type must be application/json",
            )
        try:
            payload: object = json.loads(request.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return error_response(
                HTTPStatus.BAD_REQUEST,
                "invalid_json",
                "body must contain UTF-8 JSON",
            )
        return json_response(HTTPStatus.CREATED, payload)

    return error_response(
        HTTPStatus.NOT_FOUND,
        "not_found",
        "route was not found",
    )


if __name__ == "__main__":
    health = dispatch_request(HttpRequest("GET", "/health", {}))
    created = dispatch_request(
        HttpRequest(
            "POST",
            "/tasks",
            {"content-type": "application/json"},
            b'{"title":"Learn caf\xc3\xa9 HTTP"}',
        )
    )
    wrong_method = dispatch_request(HttpRequest("DELETE", "/health", {}))

    assert health.status == HTTPStatus.OK
    assert json.loads(health.body) == {"status": "ok"}
    assert created.status == HTTPStatus.CREATED
    assert created.headers["Content-Length"] == str(len(created.body))
    assert len(created.body) > len(created.body.decode("utf-8"))
    assert wrong_method.status == HTTPStatus.METHOD_NOT_ALLOWED
    assert wrong_method.headers["Allow"] == "GET"

    print("request:", HttpRequest("GET", "/health", {"Accept": "application/json"}))
    print("response status:", created.status)
    print("response bytes:", created.body)
    print("response byte length:", created.headers["Content-Length"])
