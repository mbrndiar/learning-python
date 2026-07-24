"""
Chapter 18, Lesson 2: Status, Content Type, and JSON Validation

Purpose: interpret a captured response safely. Branch on the numeric status
first, read the content type case-insensitively, decode the body as UTF-8 JSON,
and validate its shape and values strictly before trusting any field.

Prerequisite: Lesson 1's captured `TransportResponse`, Chapter 8's JSON handling,
and Chapter 7's exception handling. This lesson is library-neutral: it works on
the same response value regardless of which client produced it.

Key subtlety: in Python, `bool` is a subclass of `int`. `isinstance(True, int)`
is `True`, so a strict integer field must also reject booleans.

Run from the repository root:

    python lessons/18_http_clients_and_transports/02_status_content_type_and_json_validation.py
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


class MalformedResponse(Exception):
    """The server replied, but not with the documented representation."""


class ApiError(Exception):
    """A structured error the server reported with a 4xx or 5xx status."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(f"API error {status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


# Step 1: HTTP field names are case-insensitive, so never index headers with a
# fixed capitalization. Read the media type only, discarding any parameters such
# as "; charset=utf-8", and compare with casefold().
def media_type(headers: Mapping[str, str]) -> str:
    value = next(
        (
            header_value
            for name, header_value in headers.items()
            if name.casefold() == "content-type"
        ),
        "",
    )
    return value.split(";", 1)[0].strip().casefold()


# Step 2: a JSON body is bytes on the wire. Decode as UTF-8 explicitly and treat
# both decode and parse failures as one malformed-response category. Valid JSON
# does not imply a valid domain object; that is Step 4.
def decode_json(response: TransportResponse) -> object:
    if media_type(response.headers) != "application/json":
        raise MalformedResponse("Content-Type was not application/json")
    try:
        return json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MalformedResponse("body was not UTF-8 JSON") from error


# Step 3: decode a documented error envelope so 4xx/5xx responses become a
# specific exception rather than a generic failure.
def decode_api_error(response: TransportResponse) -> ApiError:
    value = decode_json(response)
    if not isinstance(value, dict) or set(value) != {"error"}:
        raise MalformedResponse("error envelope was malformed")
    error = value["error"]
    if not isinstance(error, dict):
        raise MalformedResponse("error details were malformed")
    code = error.get("code")
    message = error.get("message")
    if not isinstance(code, str) or not isinstance(message, str):
        raise MalformedResponse("error code or message was malformed")
    return ApiError(response.status, code, message)


# Step 4: status-first handling. A 2xx status is required before the body is
# read as a success. Note the explicit `isinstance(..., bool)` guards: because
# bool is an int subclass, they are the only way to keep True/False out of an
# integer id and to require a real boolean for `completed`.
def decode_task(response: TransportResponse, *, expected_status: int = 200) -> Task:
    if response.status != expected_status:
        if 400 <= response.status <= 599:
            raise decode_api_error(response)
        raise MalformedResponse(f"unexpected status: {response.status}")

    value = decode_json(response)
    if not isinstance(value, dict) or set(value) != {"id", "title", "completed"}:
        raise MalformedResponse("task fields were malformed")

    task_id = value["id"]
    title = value["title"]
    completed = value["completed"]
    if (
        not isinstance(task_id, int)
        or isinstance(task_id, bool)
        or task_id <= 0
        or not isinstance(title, str)
        or not title
        or not isinstance(completed, bool)
    ):
        raise MalformedResponse("task values were malformed")
    return Task(task_id, title, completed)


def _json_response(status: int, body: bytes) -> TransportResponse:
    return TransportResponse(
        status,
        {"content-type": "application/json; charset=utf-8"},
        body,
    )


if __name__ == "__main__":
    ok = decode_task(
        _json_response(200, b'{"id":1,"title":"Read HTTP","completed":false}')
    )
    assert ok == Task(1, "Read HTTP", False)

    # A non-2xx status is data, not a valid Task: it becomes an ApiError.
    error_body = b'{"error":{"code":"not_found","message":"task 9 was not found"}}'
    try:
        decode_task(_json_response(404, error_body))
    except ApiError as error:
        assert (error.status, error.code) == (404, "not_found")
    else:
        raise AssertionError("a 404 must not decode as a Task")

    # bool is an int subclass, so {"id": true} must be rejected as malformed.
    try:
        decode_task(_json_response(200, b'{"id":true,"title":"x","completed":false}'))
    except MalformedResponse:
        pass
    else:
        raise AssertionError("a boolean id must be rejected")

    # A non-JSON content type is malformed even if the bytes happen to be JSON.
    try:
        decode_task(TransportResponse(200, {"Content-Type": "text/plain"}, b'{"id":1}'))
    except MalformedResponse:
        pass
    else:
        raise AssertionError("non-JSON content type must be rejected")

    print("decoded task:", ok)
    print(
        "media_type is case-insensitive:",
        media_type({"CONTENT-TYPE": "APPLICATION/JSON"}),
    )
    print("status-first and strict validation checks passed")
