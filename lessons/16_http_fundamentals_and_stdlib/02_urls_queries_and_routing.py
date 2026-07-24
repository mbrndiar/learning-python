"""
Chapter 16, Lesson 2: URLs, Queries, and Routing

Purpose: split request targets into path and query components, preserve repeated
query values, validate path segments, and distinguish 404 from 405 responses.

Prerequisite: Lesson 1's request/response lifecycle and Chapter 4 collections.

Run from the repository root:

    python lessons/16_http_fundamentals_and_stdlib/02_urls_queries_and_routing.py
"""

import json
from dataclasses import dataclass
from http import HTTPStatus
from urllib.parse import parse_qs, unquote, urlsplit


@dataclass(frozen=True)
class Route:
    name: str
    task_id: int | None = None


@dataclass(frozen=True)
class ParsedTarget:
    route: Route | None
    completed: bool | None


@dataclass(frozen=True)
class RoutedResponse:
    status: HTTPStatus
    headers: dict[str, str]
    body: bytes


# Step 1: urlsplit() separates the target before any percent-decoding. Query
# parsing returns lists so repeated values remain visible to validation.
def parse_completed_query(query_text: str) -> bool | None:
    query = parse_qs(
        query_text,
        keep_blank_values=True,
        strict_parsing=True,
        max_num_fields=4,
    )
    unknown = set(query) - {"completed"}
    if unknown:
        raise ValueError(f"unknown query field: {min(unknown)}")

    values = query.get("completed")
    if values is None:
        return None
    if values == ["true"]:
        return True
    if values == ["false"]:
        return False
    raise ValueError("completed must appear once as true or false")


# Step 2: match path shapes separately from query validation. unquote() is
# applied only to one path segment, never to the whole unsplit target.
def parse_target(target: str) -> ParsedTarget:
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or parts.fragment:
        raise ValueError("request target must be a local path without a fragment")

    if parts.path == "/health":
        if parts.query:
            raise ValueError("health does not accept query fields")
        return ParsedTarget(Route("health"), None)

    if parts.path == "/tasks":
        return ParsedTarget(
            Route("task_collection"), parse_completed_query(parts.query)
        )

    prefix = "/tasks/"
    if parts.path.startswith(prefix) and "/" not in parts.path[len(prefix) :]:
        if parts.query:
            raise ValueError("one task does not accept query fields")
        segment = unquote(parts.path[len(prefix) :])
        if not segment.isdecimal() or int(segment) <= 0:
            raise ValueError("task ID must be a positive integer")
        return ParsedTarget(Route("task_item", int(segment)), None)

    return ParsedTarget(None, None)


def json_response(
    status: HTTPStatus,
    payload: object,
    *,
    allow: str | None = None,
) -> RoutedResponse:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Content-Length": str(len(body)),
    }
    if allow is not None:
        headers["Allow"] = allow
    return RoutedResponse(status, headers, body)


# Step 3: an existing path with the wrong method is 405. A target with no route
# is 404. Keeping this decision explicit makes framework behavior easier to see.
def route_request(method: str, target: str) -> RoutedResponse:
    try:
        parsed = parse_target(target)
    except ValueError as error:
        return json_response(
            HTTPStatus.BAD_REQUEST,
            {"error": {"code": "invalid_target", "message": str(error)}},
        )

    if parsed.route is None:
        return json_response(
            HTTPStatus.NOT_FOUND,
            {"error": {"code": "not_found", "message": "route was not found"}},
        )

    normalized_method = method.upper()
    if parsed.route.name == "health":
        if normalized_method != "GET":
            return json_response(
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"error": {"code": "method_not_allowed"}},
                allow="GET",
            )
        return json_response(HTTPStatus.OK, {"status": "ok"})

    if parsed.route.name == "task_collection":
        if normalized_method != "GET":
            return json_response(
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"error": {"code": "method_not_allowed"}},
                allow="GET, POST",
            )
        return json_response(
            HTTPStatus.OK,
            {"route": "tasks", "completed": parsed.completed},
        )

    if normalized_method != "GET":
        return json_response(
            HTTPStatus.METHOD_NOT_ALLOWED,
            {"error": {"code": "method_not_allowed"}},
            allow="GET",
        )
    return json_response(
        HTTPStatus.OK,
        {"route": "task", "task_id": parsed.route.task_id},
    )


if __name__ == "__main__":
    collection = route_request("GET", "/tasks?completed=false")
    item = route_request("GET", "/tasks/7")
    repeated = route_request(
        "GET",
        "/tasks?completed=true&completed=false",
    )
    wrong_method = route_request("DELETE", "/tasks")
    missing = route_request("GET", "/unknown")

    assert json.loads(collection.body) == {
        "route": "tasks",
        "completed": False,
    }
    assert json.loads(item.body) == {"route": "task", "task_id": 7}
    assert repeated.status == HTTPStatus.BAD_REQUEST
    assert wrong_method.status == HTTPStatus.METHOD_NOT_ALLOWED
    assert wrong_method.headers["Allow"] == "GET, POST"
    assert missing.status == HTTPStatus.NOT_FOUND

    print("collection:", collection.status, collection.body)
    print("item:", item.status, item.body)
    print("repeated query:", repeated.status, repeated.body)
    print("wrong method:", wrong_method.status, wrong_method.headers["Allow"])
