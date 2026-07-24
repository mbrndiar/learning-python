# 🧪 Exercises: Chapter 18 — HTTP clients and transports

Build one HTTP client boundary across three libraries — `urllib`, Requests, and
HTTPX — behind a single transport contract. No live server and no network.

## 🧩 What you will implement

1. **Raw query parsing and URL encoding** — `parse_raw_query()` (preserve
   repeated values) and `build_url()` (encode a query exactly once).
2. **Case-insensitive headers and strict decoding** — `header_value()` and
   `decode_task()` (status-first, UTF-8 JSON, exact shape, strict values). Every
   malformed body, malformed JSON, malformed error envelope, or unexpected
   status becomes `MalformedResponse` — never a raw `UnicodeDecodeError` or
   `JSONDecodeError`.
3. **urllib transport** — `UrllibTransport.send()` that encodes `params` into the
   URL, serializes a JSON `json_body` with a `Content-Type` header, owns and
   closes the response, returns an `HTTPError` as a response (closing its body
   stream), and translates `URLError`.
4. **Requests and HTTPX transports** — `RequestsTransport` and `HttpxTransport`
   that use `params`/`json` helpers, pass an explicit redirect policy, copy and
   close each response (even if the copy fails), never call `raise_for_status()`,
   and classify each library's exception families.
5. **One common contract** — `validate_timeout()` and a `TaskClient` that runs
   identically over all three transports and rejects bad ids.

The evaluator injects fake openers, sessions, and clients. It never opens a
socket, binds a port, or reaches the network.

## 📥 Inputs and 📤 outputs

- Transports accept `(base_url, backend, timeout)` and expose
  `send(method, path, *, params=None, json_body=None) -> TransportResponse` plus
  `close()` and the context-manager protocol.
- A common `Transport(Protocol)` declares `send` and `close`; `TaskClient` is
  typed against it, not `object`.
- `TransportResponse` carries an `int` status, a header mapping, and raw `bytes`.
- `decode_task()` returns a frozen `Task(id, title, completed)`.

## 📋 Contract and constraints

- `parse_raw_query("")` is `{}`; repeated keys become lists; blank values are
  kept.
- `build_url()` requires a leading `/` on `path` and adds no `?` for an empty
  query.
- Header lookups are case-insensitive.
- Decode **status first**: a 4xx/5xx becomes `ApiError`; a non-JSON content type,
  malformed body, malformed error envelope, or unexpected status becomes
  `MalformedResponse`.
- `id` must be a positive `int` and **not** a `bool` (bool is an int subclass);
  `title` must be a non-empty `str`; `completed` must be a real `bool`.
- Never call `raise_for_status()`: a non-2xx status stays an ordinary response
  with its exact status and body preserved.
- **Ownership is transferred.** Each transport owns its injected backend:
  `close()` closes the opener/session/client exactly once (idempotently), the
  context manager closes it on exit, and a `send()` after close raises
  `TransportError`.
- Copy each response's status/headers/raw bytes, then close it — even if the
  copy or body read fails.
- Pass an explicit finite timeout to every backend; `validate_timeout()` rejects
  `bool`, non-numbers, non-finite, and non-positive values.
- `TaskClient.get_task()` rejects `bool`, non-`int`, and non-positive ids before
  sending.
- There are **no automatic retries**: one `send()` is one attempt, on both the
  success and every exception path.

## 🧨 Edge cases the checks exercise

- `HTTPError` preserved as a 404 response with its exact body, and its body
  stream closed.
- `URLError` timeout reason → `TransportTimeout`; other reason →
  `ConnectionFailure`.
- Requests `Timeout`/`ConnectionError`/other → the three transport exceptions.
- HTTPX `TimeoutException`/`NetworkError`/other → the three transport exceptions.
- A body-read failure still closes the response and is classified, not leaked.
- Non-2xx Requests/HTTPX responses pass through verbatim (no `raise_for_status`).
- Malformed UTF-8, malformed JSON, malformed envelopes, and unexpected statuses
  all become `MalformedResponse`.
- Resource ownership: openers, sessions, and clients are all closed exactly once.
- Timeout propagation, `params`/`json` routing, exact urllib request bytes and
  headers, the redirect policy, and per-call attempt counts are all asserted by
  observing the injected fakes.

## ▶️ Run the exercise

From the repository root:

```bash
python exercises/18_http_clients_and_transports/exercises.py
```

The untouched starter fails first in the **query parsing and URL encoding**
group. Implement the `TODO` blocks until all five groups pass.

The reference solution stays locked until you have attempted the exercise.
