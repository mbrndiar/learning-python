# 🌐 Module 11: REST APIs and HTTP Clients

HTTP is a request/response protocol. A client sends a method, target, headers,
and optional bytes; a server returns a status, headers, and optional bytes.
REST APIs apply that protocol to resources such as tasks. This module keeps the
Task domain behind small boundaries while comparing Python's standard library,
Flask, FastAPI, `urllib`, `requests`, and `httpx`.

## 🎯 Learning objectives

After this module, you should be able to:

- distinguish methods, routes, path values, query values, headers, statuses,
  bytes, UTF-8 text, and JSON values;
- keep HTTP parsing and framework objects outside domain and repository code;
- construct Flask dependencies with an application factory and test routes
  without starting a server;
- use Pydantic request and response models at a FastAPI boundary;
- inject a service, repository, provider, or client transport rather than
  hiding it in global state;
- map validation, not-found, protocol, malformed-response, and connection
  failures deliberately;
- set a positive finite timeout on every outbound request; and
- compare generated framework OpenAPI with a checked-in behavioral contract.

## 🧱 One domain, several adapters

The examples follow one dependency direction:

```text
HTTP request -> route/boundary model -> Task service -> repository
HTTP client  -> narrow transport     -> HTTP library
```

Routes decode HTTP input and select HTTP output. The service owns Task rules.
Repositories own storage. Client transports own library-specific request and
response objects. Dependencies point inward, so a framework test client or
in-memory fake can replace a real process or public network.

The bounded Task behavior comes from the applied project's
[human-readable specification](../../projects/tasks/docs/SPEC.md) and
[OpenAPI document](../../projects/tasks/docs/openapi.yaml). Generated FastAPI
OpenAPI is useful for inspecting what the framework inferred, but it does not
replace that checked-in, framework-neutral contract.

## 📚 Lesson files

1. **`01_http_fundamentals.py`** — methods, routes, queries, headers, statuses,
   bytes, UTF-8, JSON, finite timeouts, and a minimal standard-library boundary.
2. **`02_flask_api.py`** — a Flask application factory, thin routes, injected
   repository/service, centralized errors, and the Flask test client.
3. **`03_fastapi_api.py`** — Pydantic boundary models, a dependency provider,
   response models, exception mapping, generated OpenAPI, and `TestClient`.
4. **`04_http_clients.py`** — `urllib`, `requests`, and `httpx` transport
   patterns behind one narrow interface, with status-first response validation.

## ▶️ Run the lessons

The framework and client runtime dependencies are already declared in
[`projects/tasks/requirements.txt`](../../projects/tasks/requirements.txt).
Course-wide installation and CI wiring are intentionally handled elsewhere.

From the repository root:

```bash
python lessons/11_rest_apis_and_clients/01_http_fundamentals.py
python lessons/11_rest_apis_and_clients/02_flask_api.py
python lessons/11_rest_apis_and_clients/03_fastapi_api.py
python lessons/11_rest_apis_and_clients/04_http_clients.py
python exercises/11_rest_apis_and_clients/solutions.py
```

Every demonstration is deterministic and offline. The framework lessons use
in-process test clients. The client lesson injects fake transports. Importing or
running a lesson never starts a persistent server.

## 🛡️ Boundary rules

- Treat request bodies and response bodies as untrusted bytes.
- Decode text explicitly as UTF-8, then parse JSON, then validate its shape.
- Do not confuse JSON Booleans with Python integers: `True` is an `int`
  subclass, but the wire contract requires a real Boolean.
- Check an HTTP status before trusting a success body.
- Validate both successful and error response shapes.
- Encode query values with a URL encoder instead of string concatenation.
- Use finite timeouts and translate library exceptions at the transport edge.
- Do not retry mutations automatically unless a larger design defines safe
  idempotency and retry policy.
- Do not return tracebacks or raw storage exceptions to API callers.

## ⚠️ Common mistakes

- Putting validation, storage calls, and response formatting in one route.
- Opening a real database or constructing a service inside every request.
- Running a development server when a module is imported.
- Assuming a framework's default validation or error body matches the contract.
- Accepting `true`, `1`, `yes`, and any other truthy spelling as equivalent.
- Calling `.json()` before checking status and content type.
- Catching every exception as a connection failure.
- Omitting a timeout because local requests usually finish quickly.

## ❓ Review questions

1. Which parts of an HTTP exchange are bytes, and where does UTF-8 apply?
2. Why is a query value different from a path segment or JSON field?
3. What makes a Flask application factory easier to test?
4. Why should Pydantic models remain at the HTTP boundary?
5. Why does generated OpenAPI need review against the checked-in contract?
6. Why should a client inspect status before validating a success payload?
7. Which failures belong to API, malformed-response, and connection categories?
8. What capability should a narrow injected transport expose?

Concurrency still occupies its existing `11_concurrency/` directory until the
separate renumbering change moves it. In the learning sequence, complete this
REST/HTTP module before concurrency.
