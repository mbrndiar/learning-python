# 🧪 Exercises: Chapter 16 — HTTP fundamentals and the standard library

Build one deterministic HTTP boundary without a framework or live server.

## 🧩 What you will implement

1. Look up request headers case-insensitively.
2. Serialize UTF-8 JSON responses with accurate byte-based `Content-Length`.
3. Parse `/health`, `/tasks`, and `/tasks/<positive-id>` targets with
   `urlsplit()` and strict scalar query handling.
4. Dispatch methods and routes to deliberate success, validation, `404`, and
   `405` responses.
5. Adapt GET requests through a `BaseHTTPRequestHandler` subclass and write the
   pure response in protocol order.

The evaluator constructs the handler in memory. It does not bind a port, start
`serve_forever()`, or use any network.

## 📋 Contract

- Request and response bodies are bytes.
- JSON uses UTF-8 and compact serialization.
- `Content-Length` counts encoded bytes.
- `completed` may be absent or appear exactly once as lowercase `true` or
  `false`; unknown, blank, or repeated query fields are invalid.
- `/tasks/<id>` accepts one positive decimal path segment.
- Existing routes with unsupported methods return `405` and `Allow`.
- Unknown routes return `404`.
- POST `/tasks` requires `application/json`, valid UTF-8 JSON, and exactly one
  non-empty string `title`.

## ▶️ Run the exercise

From the repository root:

```bash
python exercises/16_http_fundamentals_and_stdlib/exercises.py
```

The untouched starter fails first in the response-lifecycle group. Implement the
`TODO` blocks until all three groups pass.

The reference solution remains locked until you have attempted the exercise.
