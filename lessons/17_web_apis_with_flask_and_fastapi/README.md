# 🧩 Chapter 17: Web APIs with Flask and FastAPI

Chapter 16 made every HTTP decision explicit. This chapter keeps that mental
model while introducing two frameworks:

- **Flask** provides a small WSGI application, routing decorators, request
  context, response conversion, error handlers, and an in-process test client.
- **FastAPI** combines Starlette's ASGI routing with Pydantic boundary models,
  dependency injection, response validation, and generated OpenAPI.

The frameworks remove repetitive adapter code. They do not own task validation,
repository behavior, or your external API contract.

## 🧭 Where this chapter fits

You already know:

- decorators, context managers, protocols, `Annotated`, and dependency injection
  from Chapters 10–11;
- test isolation and deterministic fakes from Chapter 12;
- repositories and service boundaries from Chapters 11 and 15; and
- HTTP methods, paths, queries, statuses, headers, bytes, JSON, and server
  ownership from Chapter 16.

This chapter uses only synchronous path-operation functions. `async def`,
coroutines, and event loops first appear in Chapter 19.

The examples share one small teaching domain in `_task_domain.py`. Flask and
FastAPI import the same `TaskService` and repository contract, so differences
stay at the web boundary.

## 🎯 Learning objectives

After this chapter, you should be able to:

- create a minimal Flask application and explain `Flask(__name__)`;
- bind paths and methods with Flask decorators and test them without a server;
- explain Flask's `request` proxy and request-context lifetime;
- construct dependencies once in an application factory;
- map domain and Werkzeug exceptions through centralized error handlers;
- define strict Pydantic `BaseModel` boundaries with `ConfigDict`, `Field`,
  `Annotated`, `Literal`, and `model_dump()`;
- inject a service into synchronous FastAPI handlers with `Depends`;
- store application-owned dependencies in `app.state`;
- constrain and filter output with `response_model`;
- override request/domain/HTTP exception handlers deliberately;
- test FastAPI with `TestClient`; and
- inspect generated OpenAPI without treating it as the sole behavioral contract.

## 🧠 1. A framework is an adapter

The dependency direction remains:

```text
HTTP/framework object
        -> boundary mapping
        -> TaskService
        -> TaskRepository protocol
```

The service and repository never import Flask, FastAPI, Starlette, Werkzeug, or
Pydantic. A route may translate an HTTP request into a service call; it should
not quietly become the place where every business and storage rule lives.

The shared domain defines:

```python
@dataclass(frozen=True)
class Task:
    id: int
    title: str
    completed: bool


class TaskRepository(Protocol):
    def create(self, title: str) -> Task: ...
    def list(self, completed: bool | None = None) -> list[Task]: ...
    def get(self, task_id: int) -> Task | None: ...
```

`TaskService` normalizes titles, rejects invalid domain values, and turns a
missing repository value into `NotFoundError`. Both framework adapters call the
same service.

## 🌶️ 2. Start with the smallest Flask application

The first Flask application is intentionally direct:

```python
from flask import Flask

app = Flask(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Step by step:

1. `Flask` is the application class.
2. `Flask(__name__)` creates one WSGI application and tells Flask the module
   location used to find resources.
3. `@app.get("/health")` registers a URL rule and GET method.
4. Flask calls `health()` inside an application and request context.
5. Returning a dictionary produces a JSON response.

The decorator runs at function definition time to register the function. Flask
calls the function later for each matching request.

### The `request` proxy

Inside a route:

```python
from flask import request

payload = request.get_json()
```

`request` is a context-local proxy. It resolves to the current request only
while Flask has pushed a request context. Accessing it outside that context
raises `RuntimeError`.

That is why helpers that do not need framework state should accept ordinary
values instead:

```python
def parse_title(payload: object) -> str: ...
```

The route reads `request`, passes its plain value to `parse_title()`, then calls
the service.

### Test without a live server

```python
with app.test_client() as client:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
```

Flask's test client constructs requests in process. `json=...` serializes a JSON
request and sets its content type. The returned test response exposes
`status_code`, `headers`, `data` bytes, `text`, and parsed JSON helpers.

## 🏭 3. Use an application factory for dependencies

A module-level `app` is enough to learn the first route. A larger application
benefits from a factory:

```python
def create_app(repository: TaskRepository | None = None) -> Flask:
    app = Flask(__name__)
    selected = repository or InMemoryTaskRepository()
    service = TaskService(selected)
    ...
    return app
```

The factory:

- creates a fresh app for each test or process;
- selects default dependencies once;
- accepts an injected fake or alternative adapter;
- registers routes and error handlers over that service; and
- returns a fully configured app without starting a server.

Do not use `repository or default` when a valid repository could be false-like.
Prefer the explicit `is not None` check shown in the lessons.

### Centralized errors

Flask and its Werkzeug routing layer can raise different exception families:

```python
@app.errorhandler(DomainError)
def handle_domain_error(error: DomainError) -> tuple[Response, int]:
    return jsonify(error_body(error)), error.status
```

Register separate mappings for:

- domain validation and not-found failures;
- malformed JSON and unsupported media type;
- a known path with the wrong method (`405`); and
- an unknown route (`404`).

The handler converts an exception to the public envelope. It should not return a
traceback, database path, secret, or raw storage error.

### Framework `404` versus domain `404`

These share a status but not a cause:

- `GET /unknown` never matched a route; Werkzeug raises routing `404`.
- `GET /tasks/99` matched a route, but `TaskService.get()` raises
  `NotFoundError`.

A stable external envelope may map both to code `not_found`, while keeping the
internal source visible in logs or tests.

## ✅ 4. Put untrusted boundary data in Pydantic models

Pydantic models are classes derived from `BaseModel`:

```python
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Title = Annotated[str, Field(min_length=1, max_length=120)]


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    title: Title
```

The pieces have separate roles:

- the annotation `str` declares the resulting field type;
- `Field()` adds length constraints and JSON Schema metadata;
- `str_strip_whitespace=True` normalizes surrounding whitespace before length
  checks;
- `strict=True` rejects coercions such as integer `3` to string `"3"`;
- `extra="forbid"` rejects undeclared properties instead of silently ignoring
  them.

Pydantic guarantees the resulting model fields, not the trustworthiness of the
original input. Domain rules still belong in `TaskService`.

### Input and output models have different jobs

```python
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    title: str
    completed: bool
```

`from_attributes=True` lets validation read a dataclass or ordinary object's
attributes. Keep input and output models separate: an output model documents and
filters what may leave the API, while an input model controls accepted fields.

Useful model APIs:

| API | Purpose |
| --- | --- |
| `CreateTaskRequest.model_validate(value)` | validate a Python object |
| `CreateTaskRequest.model_validate_json(data)` | parse and validate JSON bytes/text |
| `model.model_dump()` | serialize fields to Python values |
| `CreateTaskRequest.model_json_schema()` | inspect generated JSON Schema |

Pydantic's default is coercive and ignores extra fields. Strict and extra policy
must be chosen deliberately for an external contract.

## ⚡ 5. Compose the FastAPI boundary

FastAPI treats a normal `def` function as a synchronous path operation:

```python
@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    payload: CreateTaskRequest,
    service: ServiceDependency,
) -> Task:
    return service.create(payload.title)
```

FastAPI:

1. matches the path and method;
2. parses JSON;
3. validates it as `CreateTaskRequest`;
4. resolves the declared dependency;
5. calls the synchronous function;
6. validates and filters the returned task through `TaskResponse`;
7. serializes the result; and
8. documents the operation in OpenAPI.

### `Depends` receives a callable, not its result

```python
def get_task_service(request: Request) -> TaskService:
    service = request.app.state.task_service
    ...
    return service


ServiceDependency = Annotated[
    TaskService,
    Depends(get_task_service),
]
```

Pass `get_task_service`, not `get_task_service()`. FastAPI calls the provider for
each request and supplies its result to the route.

The application factory stores one service on `app.state`:

```python
app.state.task_service = TaskService(repository)
```

This makes ownership explicit: the app owns the service reference, while the
factory caller can inject the repository.

### Query metadata with `Annotated` and `Literal`

```python
CompletedQuery = Annotated[
    Literal["true", "false"] | None,
    Query(description="Exact lowercase completion state"),
]
```

`Literal` restricts accepted values. `Query()` adds boundary metadata. FastAPI
uses both for validation and OpenAPI.

### Response models are active behavior

`response_model=TaskResponse` is not only documentation. FastAPI validates,
serializes, and filters returned data according to that model. An invalid output
is an application bug and produces a server error rather than silently emitting
an undocumented shape.

## 🚨 6. Override FastAPI error boundaries deliberately

FastAPI has default handlers for validation and `HTTPException`. A checked-in API
contract may require a different envelope:

```python
@app.exception_handler(RequestValidationError)
def handle_request_validation(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse: ...
```

The handler receives the current request and exception and returns a response.
The lessons use normal `def` handlers to avoid introducing asynchronous syntax.

Register routing errors against Starlette's `HTTPException`, not only FastAPI's
subclass. Starlette itself raises routing `404` and `405`.

Do not echo `str(RequestValidationError)` or its request body blindly. Validation
objects can include internal locations and untrusted data. Extract only the
bounded fields required by the public contract.

## 🧪 7. TestClient and generated OpenAPI

FastAPI's `TestClient` comes from Starlette and is based on HTTPX:

```python
with TestClient(app) as client:
    response = client.post("/tasks", json={"title": "Learn FastAPI"})
```

The test remains synchronous. No server process or `await` is needed.

`app.openapi()` returns the generated OpenAPI dictionary:

```python
schema = app.openapi()
assert "/tasks" in schema["paths"]
assert "TaskResponse" in schema["components"]["schemas"]
```

Generated OpenAPI describes what FastAPI inferred from routes, models, response
models, and dependencies. Review it against the framework-neutral behavioral
contract. Generation cannot decide product semantics such as error precedence,
idempotency, authorization, or whether two status codes should share an
envelope.

The required Task project keeps its authoritative contract in:

- `projects/tasks/docs/SPEC.md`; and
- `projects/tasks/docs/openapi.yaml`.

## 🔁 Read, predict, run, modify

### Lesson 1 — minimal Flask and test client

Read `01_flask_minimal_app_and_test_client.py`.

Predict the status and body for a valid JSON POST and for a GET to that
POST-only route.

```bash
python lessons/17_web_apis_with_flask_and_fastapi/01_flask_minimal_app_and_test_client.py
```

Change the route path in one place and predict which test fails.

### Lesson 2 — factory, errors, and dependencies

Read `_task_domain.py`, then
`02_flask_factory_errors_and_dependencies.py`.

Predict whether two calls to `create_app()` share repository state.

```bash
python lessons/17_web_apis_with_flask_and_fastapi/02_flask_factory_errors_and_dependencies.py
```

Change one injected repository and observe that only its app sees the task.

### Lesson 3 — Pydantic boundary models

Read `03_pydantic_boundary_models.py`.

Predict which inputs are rejected by strict type checking, extra-field policy,
and length constraints.

```bash
python lessons/17_web_apis_with_flask_and_fastapi/03_pydantic_boundary_models.py
```

Temporarily change `extra="forbid"` to `extra="ignore"` and observe that the
same extra-field input is accepted but omitted from `model_dump()`.

### Lesson 4 — FastAPI composition

Read `04_fastapi_dependencies_responses_and_openapi.py`.

Trace one POST through model validation, dependency resolution, the service,
response-model filtering, and serialization.

```bash
python lessons/17_web_apis_with_flask_and_fastapi/04_fastapi_dependencies_responses_and_openapi.py
```

Then add an undeclared field to the test request and inspect the stable error
envelope plus generated schema.

## ⚠️ Common mistakes

- Teaching a complete factory and dependency graph before one minimal route.
- Accessing Flask's `request` proxy outside a request context.
- Constructing a repository inside every route.
- Starting a development server at import time.
- Putting domain rules directly in framework handlers.
- Assuming Pydantic is strict or forbids extra data by default.
- Reusing one model for unrelated input and output contracts.
- Calling the function passed to `Depends` instead of passing the callable.
- Hiding an app-owned service in unstructured module global state.
- Returning raw validation or storage exceptions to clients.
- Assuming generated OpenAPI proves runtime behavior.
- Introducing `async def` before its scheduling model is taught.

## 🧾 Summary

- Flask begins with `Flask(__name__)`, route decorators, request context, and a
  test client.
- An application factory creates fresh apps and wires injected dependencies
  once.
- Centralized handlers translate domain and framework exceptions to public
  responses.
- Pydantic models validate resulting typed structures; strictness and extra-field
  behavior are explicit policies.
- FastAPI resolves `Depends`, validates inputs and response models, and generates
  OpenAPI from synchronous path operations.
- Framework objects stay at the adapter boundary; both frameworks call the same
  service and repository protocol.

## ❓ Review questions (closed notes)

1. What does `Flask(__name__)` create, and what does the argument identify?
2. Why does Flask's `request` work inside a route but fail outside a request
   context?
3. What test and ownership benefits come from an application factory?
4. Which Pydantic defaults change when `strict=True` and `extra="forbid"` are
   configured?
5. Why should input and output models be separate?
6. Why does `Depends(get_service)` omit parentheses?
7. What does `response_model` do at runtime in addition to documenting OpenAPI?
8. Why is generated OpenAPI evidence but not the only contract authority?

## 📚 Authoritative references

- [Flask 3.1 quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [Flask application factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [Flask request context](https://flask.palletsprojects.com/en/stable/reqcontext/)
- [Testing Flask applications](https://flask.palletsprojects.com/en/stable/testing/)
- [Flask error handling](https://flask.palletsprojects.com/en/stable/errorhandling/)
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [Pydantic fields](https://docs.pydantic.dev/latest/concepts/fields/)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI error handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI OpenAPI generation](https://fastapi.tiangolo.com/how-to/extending-openapi/)

Next, complete the
[Chapter 17 exercise](../../exercises/17_web_apis_with_flask_and_fastapi/README.md).
Then continue to
[Chapter 18: HTTP clients and transports](../18_http_clients_and_transports/README.md).
