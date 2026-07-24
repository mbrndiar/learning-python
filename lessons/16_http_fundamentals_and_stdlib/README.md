# 🌐 Chapter 16: HTTP fundamentals and the standard library

HTTP is a protocol for exchanging one **request** for one **response**. This
chapter starts below every framework: first with plain Python values, then with
URL parsing and routing, and only then with `http.server`. That order makes the
framework chapters easier to understand because Flask and FastAPI automate the
same boundary work rather than replacing HTTP itself.

## 🧭 Where this chapter fits

You already know:

- bytes, UTF-8, JSON, exceptions, and context managers from Chapters 2, 7, and 8;
- dataclasses, protocols, and dependency injection from Chapters 9 and 11;
- deterministic tests and CLI boundaries from Chapters 12 and 13; and
- repositories and caller-owned resources from Chapter 15.

This chapter uses those tools to model a small task API. It does **not** require
a public network, a persistent server, Flask, FastAPI, Requests, or HTTPX.

## 🎯 Learning objectives

After this chapter, you should be able to:

- identify the method, request target, headers, body bytes, status, and response
  headers in one HTTP exchange;
- distinguish URL paths, path segments, query strings, and fragments;
- parse query values without treating them as path or JSON values;
- route a request by method and path and return deliberate `200`, `400`, `404`,
  and `405` responses;
- construct UTF-8 JSON responses with accurate `Content-Type` and
  `Content-Length` headers;
- explain how `BaseHTTPRequestHandler` dispatches to `do_GET()` and exposes
  `command`, `path`, `headers`, `rfile`, and `wfile`; and
- keep protocol mapping separate from domain behavior and server ownership.

## 🧠 1. One exchange, two messages

A simplified request looks like this:

```text
GET /tasks?completed=false HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json

```

Its important parts are:

1. **Method** — `GET` describes the requested operation.
2. **Request target** — `/tasks?completed=false` contains a path and query.
3. **Protocol version** — here `HTTP/1.1`.
4. **Headers** — metadata represented on the wire as text fields.
5. **Body** — optional bytes after the blank line.

A response follows the same header/body boundary:

```text
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 48

[{"id":1,"title":"Read HTTP","completed":false}]
```

The status code describes the result before the body is interpreted. Headers
describe the representation. The body is bytes; JSON is a convention applied
after decoding those bytes as UTF-8.

### Status categories

| Range | Meaning | Examples used here |
| --- | --- | --- |
| `2xx` | successful request | `200 OK`, `201 Created` |
| `4xx` | request cannot be fulfilled as sent | `400 Bad Request`, `404 Not Found`, `405 Method Not Allowed` |
| `5xx` | server failed to complete a valid request | `500 Internal Server Error` |

Do not infer success from valid JSON. An error response can also contain JSON,
and a successful status can still carry a malformed body.

## 🧱 2. Model the protocol before adapting a server

The first lesson uses frozen dataclasses:

```python
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
```

These are teaching values, not a replacement HTTP framework. They make the
boundary observable:

```text
HttpRequest -> dispatch_request() -> HttpResponse
```

`json_response()` performs one explicit lifecycle:

1. serialize a Python value with `json.dumps()`;
2. encode the resulting text with UTF-8;
3. set `Content-Type` to JSON;
4. compute `Content-Length` from the encoded bytes, not from text characters;
5. attach the chosen status.

That last distinction matters for non-ASCII text:

```python
text = "café"
len(text)  # 4 characters
len(text.encode("utf-8"))  # 5 bytes
```

HTTP field names are case-insensitive. A plain Python dictionary is
case-sensitive, so a framework-neutral helper must compare normalized names
instead of assuming only `Content-Type` capitalization.

## 🔗 3. Split a request target into URL components

For an origin server, `BaseHTTPRequestHandler.path` contains the path plus the
query:

```text
/tasks/7?verbose=true
```

`urllib.parse.urlsplit()` separates components without decoding percent escapes:

```python
parts = urlsplit("/tasks/7?verbose=true")
parts.path  # "/tasks/7"
parts.query  # "verbose=true"
```

Use `parse_qs()` when repeated values matter:

```python
parse_qs("tag=python&tag=http", keep_blank_values=True)
# {"tag": ["python", "http"]}
```

The list is significant. `?completed=true&completed=false` is not the same as
one completion filter and should not silently choose a winner.

### Path segments are not query values

For `/tasks/7`:

- `tasks` identifies a collection;
- `7` is one path segment identifying a resource;
- `completed=false` would be a query filter on a collection;
- a JSON field named `completed` would be part of a request body.

They can contain similar text but have different protocol roles and validation
rules.

`urlsplit()` does not validate every URL and does not percent-decode path text.
Use `urllib.parse.unquote()` only on the component you intend to decode. Never
decode an entire target before splitting it, because escaped delimiters can
change its apparent structure.

## 🧭 4. Route by path, then enforce the method

A small router can return a semantic route value:

```python
@dataclass(frozen=True)
class Route:
    name: str
    task_id: int | None = None
```

The routing sequence is:

1. split the target;
2. match the path shape;
3. validate any path value;
4. parse allowed query fields;
5. dispatch by method;
6. return `404` when no path exists;
7. return `405` with `Allow` when the path exists but the method does not.

`404` and `405` answer different questions:

- `404 Not Found`: “No route has this path.”
- `405 Method Not Allowed`: “The path exists, but not for this method.”

For `405`, the `Allow` response header lists supported methods. A framework may
construct that header automatically; a standard-library adapter must do so
deliberately.

## 🖥️ 5. Adapt the pure boundary with `http.server`

`HTTPServer` owns a listening socket and creates one handler instance per
request. `BaseHTTPRequestHandler` parses the request and dispatches by method
name:

```text
GET  -> do_GET()
POST -> do_POST()
```

The handler exposes:

| Attribute/API | Role |
| --- | --- |
| `command` | parsed method such as `"GET"` |
| `path` | request path including the query |
| `headers` | parsed case-insensitive request headers |
| `rfile` | buffered binary request stream |
| `wfile` | buffered binary response stream |
| `send_response(status)` | buffer the status line plus standard headers |
| `send_header(name, value)` | buffer one response header |
| `end_headers()` | finish and flush the header section |

For a body-bearing request, read exactly the validated `Content-Length`:

```python
length = int(handler.headers.get("Content-Length", "0"))
body = handler.rfile.read(length)
```

Then adapt to the pure function:

```text
handler attributes/streams
        -> HttpRequest
        -> dispatch_request()
        -> HttpResponse
        -> send_response/send_header/end_headers/wfile.write
```

The handler should not contain task validation or storage logic. It translates
between `http.server` objects and the already testable request/response values.

### Response write order

The order is part of the API:

```python
handler.send_response(response.status)
for name, value in response.headers.items():
    handler.send_header(name, value)
handler.end_headers()
handler.wfile.write(response.body)
```

If you omit `end_headers()`, the buffered headers are incomplete. If you write
text instead of bytes to `wfile`, Python raises `TypeError`. If you advertise an
incorrect `Content-Length`, persistent clients can misread message boundaries.

## 🔌 6. Server ownership and safe execution

Importing a module must not start a server. The third lesson's default command
constructs a handler in memory and examines its response bytes:

```bash
python lessons/16_http_fundamentals_and_stdlib/03_stdlib_http_server.py
```

The optional live demonstration is explicit:

```bash
python lessons/16_http_fundamentals_and_stdlib/03_stdlib_http_server.py --serve
```

It binds only to `127.0.0.1:8000`. Stop it with `Ctrl+C`; the `HTTPServer`
context closes its socket on exit. Python's documentation warns that
`http.server` is not recommended for production: it implements basic server
behavior, not a hardened deployment boundary.

The course evaluator never starts this server and never uses public networking.

## 🧪 Read, predict, run, modify

### Lesson 1 — request and response lifecycle

Read `01_http_request_response_lifecycle.py`.

Predict:

- the UTF-8 byte length of the JSON body containing `"café"`;
- the status for `DELETE /health`; and
- whether a lowercase `content-type` request header is found.

Run:

```bash
python lessons/16_http_fundamentals_and_stdlib/01_http_request_response_lifecycle.py
```

Then change one response title to an ASCII-only value and predict which length
changes.

### Lesson 2 — URL parsing and routing

Read `02_urls_queries_and_routing.py`.

Predict how these differ:

```text
/tasks/7
/tasks?completed=false
/tasks?completed=true&completed=false
/unknown
```

Run:

```bash
python lessons/16_http_fundamentals_and_stdlib/02_urls_queries_and_routing.py
```

Then add one unknown query field and observe the focused validation response.

### Lesson 3 — standard-library adapter

Read `03_stdlib_http_server.py`, especially `do_GET()`,
`send_http_response()`, and `run_handler_in_memory()`.

Predict which handler attributes become the pure `HttpRequest`, and which calls
write the response.

Run:

```bash
python lessons/16_http_fundamentals_and_stdlib/03_stdlib_http_server.py
```

Then change the in-memory target from `/health` to `/missing` and inspect the
status line and JSON body.

## ⚠️ Common mistakes

- Treating HTTP as “JSON over functions” and ignoring method, status, headers,
  and bytes.
- Computing `Content-Length` from Unicode characters instead of encoded bytes.
- Comparing header names case-sensitively.
- Parsing a query by splitting strings manually.
- Silently accepting repeated scalar query values.
- Returning `404` for every wrong method instead of distinguishing `405`.
- Calling `wfile.write()` with `str`.
- Forgetting `end_headers()`.
- Reading an unbounded request body or trusting an invalid `Content-Length`.
- Starting `serve_forever()` during import or in automated checks.
- Treating the development server as production infrastructure.

## 🧾 Summary

- HTTP exchanges a method/target/headers/body request for a
  status/headers/body response.
- Message bodies are bytes; UTF-8 and JSON are explicit representation choices.
- Paths, path values, query values, and JSON fields are separate boundaries.
- `urlsplit()` separates target components and `parse_qs()` preserves repeated
  values.
- A pure dispatcher makes routing and status behavior deterministic.
- `BaseHTTPRequestHandler` adapts parsed request state and binary streams to
  that dispatcher.
- The code that constructs `HTTPServer` owns its listening socket and lifetime.

## ❓ Review questions (closed notes)

1. Why can `len(text)` differ from the correct HTTP `Content-Length`?
2. Which part of `/tasks/7?verbose=true` is a path value, and which is a query
   value?
3. Why does `parse_qs()` return lists?
4. What is the behavioral difference between `404` and `405`?
5. Which `BaseHTTPRequestHandler` attributes contain request body bytes and
   response body bytes?
6. Why must `end_headers()` occur before writing the body?
7. Which code owns `HTTPServer.close()`, and why should a route not do it?

## 📚 Authoritative references

- [`http` — HTTP modules (Python 3.11)](https://docs.python.org/3.11/library/http.html)
- [`http.server` and `BaseHTTPRequestHandler`](https://docs.python.org/3.11/library/http.server.html)
- [`urllib.parse`](https://docs.python.org/3.11/library/urllib.parse.html)
- [`json`](https://docs.python.org/3.11/library/json.html)
- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)

Next, complete the
[Chapter 16 exercise](../../exercises/16_http_fundamentals_and_stdlib/README.md).
Then continue to
[Chapter 17: Web APIs with Flask and FastAPI](../17_web_apis_with_flask_and_fastapi/README.md).
