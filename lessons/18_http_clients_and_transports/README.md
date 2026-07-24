# 🚚 Chapter 18: HTTP clients and transports

Chapters 16 and 17 built the *server* side of one HTTP exchange. This chapter
crosses to the *client* side: how a Python program sends a request and safely
interprets the response. We climb one layer at a time — the standard library
`urllib.request` first, then Requests, then HTTPX — and only compose a shared
abstraction once every concrete lifecycle is understood.

## 🧭 Where this chapter fits

You already know:

- bytes and UTF-8 (Chapter 2), exceptions and the `with` statement (Chapter 7),
  and JSON (Chapter 8);
- the custom context-manager protocol, `__enter__`/`__exit__` (Chapter 10);
- URL components, query parsing, and case-insensitive headers (Chapter 16);
- Protocols, dataclasses, and dependency injection (Chapters 9, 11); and
- deterministic tests and caller-owned resources (Chapters 12, 15).

This chapter uses those tools to talk to a small task API. It does **not**
require a public network or a running server. Every lesson injects an offline
fake opener, adapter, or mock transport, so results are deterministic and no
socket is ever opened. Asynchronous clients are **out of scope** — `async`/`await`
arrive in Chapter 19.

## 🎯 Learning objectives

After this chapter you should be able to:

- build a URL and encode a query with `urllib.parse` and construct a
  `urllib.request.Request`;
- open a request through an *opener* with a finite timeout and own the response
  lifetime with a context manager;
- branch on status first, read the content type case-insensitively, decode UTF-8
  JSON, and validate a response shape and values strictly;
- treat `HTTPError` as a response-bearing object and `URLError` as *no response*,
  distinguishing a timeout from other connection failures;
- own a `requests.Session` and an `httpx.Client`, use their `params`/`json`
  helpers, read raw response bytes, set an explicit timeout, and classify their
  exception families; and
- define one small transport `Protocol` and a client policy that validates the
  timeout and performs exactly one attempt per call.

## 🧠 1. Mental model: a client is a translator plus an owner

A client does two jobs:

1. **Translate** a Python intent (method, path, query, JSON) into wire bytes, and
   translate the wire response back into Python values.
2. **Own** a scarce resource — an open connection or a pool of them — that must
   be released.

Every library in this chapter does both jobs; they differ only in *how*. The
recurring picture is:

```text
intent -> [client encodes] -> request bytes
                                   |
                              (network)
                                   |
response bytes -> [client decodes] -> status + headers + body
                                   |
                          [you validate, then close]
```

We keep the decoded result in one neutral value so the three libraries become
interchangeable data:

```python
@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes
```

Two rules apply to *every* client below:

- **Status first.** A valid JSON body does not mean success; a `404` can carry
  JSON too. Branch on the numeric status before trusting the body.
- **Timeouts are mandatory.** A client with no timeout can block forever. We
  always pass a finite, positive timeout.

## 🧱 2. Layer one: `urllib.request` (standard library)

`urllib` ships with Python, so it is the baseline every environment has.

### URL and Request construction (Lesson 1)

Build the query yourself so values are percent-encoded exactly once, then bundle
everything into a `Request`:

```python
url = f"{base}/tasks?{urlencode({'completed': 'false'})}"
request = Request(url, data=body, headers={"Accept": "application/json"}, method="GET")
```

Constructing a `Request` opens no connection — it is cheap to inspect and test.

### Opener lifecycle and finite timeout (Lesson 1)

An *opener* performs the exchange. Each `open()` returns one response you must
close, and the timeout is always finite:

```python
with opener.open(request, timeout=2.5) as response:
    return TransportResponse(response.status, dict(response.headers), response.read())
```

The `with` block guarantees the network handle closes even if `read()` raises.

### The two failure shapes (Lesson 3)

This is the part people get wrong. urllib splits failures in two:

| Exception | Meaning | What it carries |
| --- | --- | --- |
| `HTTPError` | a response arrived with a non-2xx status | **status, headers, and a readable body** |
| `URLError` | no HTTP response arrived at all | a `reason` (e.g. a `TimeoutError`) |

`HTTPError` **is** a response. Do not discard it — read its body and close it
just like a success:

```python
except HTTPError as error:
    with error:
        return TransportResponse(error.code, dict(error.headers), error.read())
```

`HTTPError` is a subclass of `URLError`, so catch it **first**. For `URLError`,
inspect `reason` to separate a finite-timeout expiry from any other connection
failure:

```python
except URLError as error:
    if isinstance(error.reason, TimeoutError):
        raise TransportTimeout(...) from error
    raise ConnectionFailure(...) from error
```

Catch only the transport exceptions you understand. Wrapping an unrelated
`ValueError` in a connection category would hide a real bug.

## 🧩 3. Interpreting a response safely (Lesson 2)

Response interpretation is library-neutral: it works on the `TransportResponse`
regardless of who produced it.

1. **Case-insensitive content type.** HTTP field names are case-insensitive;
   never index headers with a fixed capitalization. Read the media type and drop
   parameters:

   ```python
   media = value.split(";", 1)[0].strip().casefold()  # "application/json"
   ```

2. **UTF-8 JSON.** The body is bytes; decode as UTF-8 explicitly and treat decode
   and parse errors as one malformed-response category.

3. **Strict shape and values.** Require the exact field set, then validate each
   value. Remember the subtle rule:

   ```python
   isinstance(True, int)  # True — bool is a subclass of int!
   ```

   So a strict integer id must also reject booleans:

   ```python
   if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
       raise MalformedResponse(...)
   ```

## 📦 4. Layer two: Requests sessions (Lesson 4)

Requests is the most widely used third-party client. Its key object is the
`Session`.

- **Ownership.** A `Session` holds a connection pool. Create one, reuse it, and
  **close** it — with `with` or an explicit `close()`.
- **Helpers.** Pass `params={...}` and Requests builds the query; pass
  `json={...}` and Requests serializes the body and sets `Content-Type`.
- **Raw bytes.** `response.content` is the raw body as `bytes`.
- **No default timeout.** Requests will wait forever unless you pass `timeout=`.
  Always pass a finite value.
- **No `raise_for_status()`.** A `4xx`/`5xx` must remain an ordinary transport
  response so the status-first validator can classify it.
- **Exception families.** Classify specific-first, because all inherit from
  `requests.RequestException`:

  ```python
  except requests.Timeout: ...          # timed out
  except requests.ConnectionError: ...  # could not connect / transfer
  except requests.RequestException: ... # anything else Requests-level
  ```

The lesson drives a **real** `Session` (so `params`/`json` are genuinely
encoded) but mounts an offline adapter that returns canned bytes.

## 🌐 5. Layer three: HTTPX clients (Lesson 5)

HTTPX offers a modern API that is deliberately close to Requests, so the mental
model transfers. Its key object is `httpx.Client`.

- **Ownership.** Like a `Session`, an `httpx.Client` owns a pool and must be
  closed.
- **`base_url`.** Configure the host once; each call takes a relative path.
- **Helpers and raw bytes.** Same `params=`/`json=`; raw body via
  `response.content`. (HTTPX serializes JSON *compactly*, without spaces, a small
  wire difference from Requests.)
- **Default timeout.** Unlike Requests, HTTPX has a default of **five seconds of
  network inactivity**. Still set it explicitly to make policy visible.
- **Redirects and proxies.** HTTPX does **not** follow redirects unless you set
  `follow_redirects=True`; `trust_env=False` ignores ambient proxy settings.
- **No `raise_for_status()`**, same reason as Requests.
- **Exception families** (all subclass `httpx.HTTPError`, so specific-first):

  ```python
  except httpx.TimeoutException: ...  # connect/read/write/pool timeout
  except httpx.NetworkError: ...      # connection-level failure
  except httpx.HTTPError: ...         # anything else HTTPX-level
  ```

The lesson drives a **real** `httpx.Client` through an `httpx.MockTransport`
handler — fully offline, genuine encoding.

## 🔌 6. Composing one contract (Lesson 6)

Only now — after all three concrete lifecycles — do we unify them. A tiny
`Protocol` is the whole contract. The timeout is an argument to `send()` so the
client's policy value actually reaches the wire:

```python
class Transport(Protocol):
    def send(
        self, method, path, *, params=None, json_body=None, timeout: float
    ) -> TransportResponse:
        """Make exactly one attempt with this timeout and return neutral data."""
```

A `TaskClient` holds the shared **policy** and depends only on the Protocol:

- **Validate the timeout once** — positive, finite, and not a `bool` — then pass
  that same value to every `send()`. Each transport revalidates and hands it to
  its backend, so `TaskClient(timeout=2.5)` makes urllib, Requests, and HTTPX all
  observe `2.5` instead of a hidden hard-coded default:

  ```python
  if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
      raise ValueError(...)
  if not math.isfinite(timeout) or timeout <= 0:
      raise ValueError(...)
  ```

- **No automatic retries.** One `send()` call means exactly one network attempt.
  Retrying a non-idempotent request (POST/PATCH) could duplicate effects, so
  retry policy is deliberately deferred to a later layer.

- **Status-first, still.** The client reuses the full Lesson 2 validation
  (content type, UTF-8 JSON, exact shape, strict values, structured API errors),
  so a raw JSON or Unicode error never leaks out of a transport.

Three concrete transports (urllib, Requests, HTTPX) satisfy the same `Protocol`,
each honoring `params` and `json_body` and passing the client's timeout, and the
identical `TaskClient` produces identical results over all three. That parity is
the payoff of staging the layers.

## 🧪 Read, predict, run, modify

### Lesson 1 — URLs, queries, and `urllib.request`

Predict the encoded form of `{"completed": "false", "q": "read http"}` and
whether building a `Request` opens a connection. Run:

```bash
python lessons/18_http_clients_and_transports/01_urls_queries_and_urllib_request.py
```

Then change the timeout to a negative number and predict the failure.

### Lesson 2 — status, content type, and JSON validation

Predict the outcome of decoding `{"id": true, ...}` and a `text/plain` response
whose bytes are valid JSON. Run:

```bash
python lessons/18_http_clients_and_transports/02_status_content_type_and_json_validation.py
```

Then remove the `isinstance(task_id, bool)` guard and see which check stops
failing.

### Lesson 3 — urllib responses and errors

Predict which outcomes preserve a body (`HTTPError`) and which do not
(`URLError`). Run:

```bash
python lessons/18_http_clients_and_transports/03_urllib_responses_and_errors.py
```

Then reorder the `except HTTPError` clause after `except URLError` and predict
why the 404 body is lost.

### Lesson 4 — Requests sessions

Predict the URL after `params={"completed": "false"}` and the body after
`json_body={"title": "Write bytes"}`. Run:

```bash
python lessons/18_http_clients_and_transports/04_requests_sessions.py
```

Then remove the `timeout=` argument in a real call and note why Requests would
wait forever.

### Lesson 5 — HTTPX clients

Predict the JSON body bytes HTTPX produces versus Requests. Run:

```bash
python lessons/18_http_clients_and_transports/05_httpx_clients.py
```

Then flip `follow_redirects` to `True` and reason about the behavior change.

### Lesson 6 — transport contract and client policy

Predict whether `validate_timeout(True)` is accepted. Run:

```bash
python lessons/18_http_clients_and_transports/06_transport_contract_and_client_policy.py
```

Then add a fourth transport that returns a `404` body and predict the client's
status-first result.

## ⚠️ Common mistakes

- Inferring success from valid JSON instead of branching on status first.
- Discarding an `HTTPError` body instead of reading and closing it.
- Confusing `HTTPError` (a response) with `URLError` (no response).
- Catching `HTTPError` after `URLError` and losing the response.
- Broad-catching unrelated exceptions into a connection category.
- Forgetting that `bool` is an `int` subclass in strict validation.
- Omitting a timeout — fatal with Requests, which has no default.
- Leaking a `Session` or `Client` by never closing it.
- Calling `raise_for_status()` when non-2xx must stay an ordinary response.
- Building a shared abstraction before understanding each concrete client.
- Adding automatic retries that can duplicate non-idempotent effects.

## 🧾 Summary

- A client both translates intents to bytes and owns a connection resource.
- urllib splits failures: `HTTPError` carries a response; `URLError` does not.
- Interpret responses status-first, with case-insensitive headers, UTF-8 JSON,
  and strict shape/value checks (mind `bool`).
- Requests and HTTPX own a `Session`/`Client`, offer `params`/`json` helpers and
  raw `.content`, and need an explicit timeout and deliberate cleanup.
- Requests has no default timeout; HTTPX defaults to 5s of inactivity and does
  not follow redirects unless asked.
- A one-method `Protocol` unifies all three; client policy validates the timeout
  and makes exactly one attempt per call.

## ❓ Review questions (closed notes)

1. Why can a `200` response still be malformed, and why can a `404` still be
   valid data?
2. What does `HTTPError` carry that a caught-and-discarded exception would lose?
3. How do you tell a urllib timeout apart from a connection refusal?
4. Why must strict integer validation also test `isinstance(value, bool)`?
5. What breaks if a Requests call omits `timeout=`?
6. Name one wire-visible difference between Requests and HTTPX JSON bodies.
7. Why does the shared contract come *after* the three concrete lifecycles, and
   why does it make exactly one attempt per call?

## 📚 Authoritative references

- [`urllib.request`](https://docs.python.org/3.11/library/urllib.request.html)
- [`urllib.error`](https://docs.python.org/3.11/library/urllib.error.html)
- [`urllib.parse`](https://docs.python.org/3.11/library/urllib.parse.html)
- [Requests documentation](https://requests.readthedocs.io/en/latest/)
- [HTTPX documentation](https://www.python-httpx.org/)
- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)

Next, complete the
[Chapter 18 exercise](../../exercises/18_http_clients_and_transports/README.md).
Then continue to Chapter 19: Concurrency.
