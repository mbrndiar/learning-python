# ✅ Task REST API and clients

Build one small Task application behind three HTTP server implementations and
use it through three HTTP client libraries. The point is not to create three
unrelated applications. It is to keep one domain and one HTTP contract stable
while observing what each library makes explicit, convenient, or implicit.

The project includes matching typed `starter/` and `solution/` public APIs plus
a shared test harness. The starter keeps all five milestones intentionally
guided and incomplete. The solution implements both repositories, all three
servers and clients, the shared contracts, and the interoperability matrix.

## Course placement

This is the required applied project between
[Module 11: REST APIs and HTTP Clients](../../lessons/11_rest_apis_and_clients/README.md)
and [Module 12: Concurrency](../../lessons/12_concurrency/README.md). Module 10's
SQL/SQLite material and Module 11's HTTP boundaries are prerequisites. Complete
all five milestones before moving to concurrency and the final capstones.

## Start with the contract

- [`docs/SPEC.md`](docs/SPEC.md) explains the behavior, workflows, persistence,
  errors, client commands, and project boundaries.
- [`docs/openapi.yaml`](docs/openapi.yaml) is the compact OpenAPI 3.1 HTTP
  contract.
- [`docs/PLAN.md`](docs/PLAN.md) is a reusable, language-independent build plan
  for adapting the project to another learning repository.
- [`docs/PROMPT.md`](docs/PROMPT.md) is a reusable agent instruction template.
- [`requirements.txt`](requirements.txt) declares the project's runtime and
  executable-contract dependencies. The repository's
  [`requirements-dev.txt`](../../requirements-dev.txt) includes it for a clean
  course-wide development installation.

Read the specification before tests or source. Tests will provide fast
feedback, but they are not a hidden replacement for the written contract.

## Architecture

Both source roots will expose the same packages:

```text
projects/tasks/
├── starter/
│   ├── tasks_core/
│   ├── tasks_api/{stdlib,flask,fastapi}/
│   └── tasks_cli/{urllib,requests,httpx}/
├── solution/
│   ├── tasks_core/
│   ├── tasks_api/{stdlib,flask,fastapi}/
│   └── tasks_cli/{urllib,requests,httpx}/
└── tests/
```

`tasks_core` owns the Task value, validation, service, repository protocol,
SQLite repository, and versioned Markdown repository. It has no dependency on
an HTTP server or client library.

Partial updates use the public `UNSET` sentinel through `UpdateTaskInput`.
Omitted fields remain `UNSET`, while `completed=False` is an explicit update;
`None` is never used to mean omission and remains invalid at the service
boundary.

`tasks_api` contains thin inbound adapters over the shared service. `tasks_cli`
contains one shared command application and three thin outbound transports.
Every client must work with every server; the directory names are comparisons,
not pairings.

## Five milestones

1. **Domain and contracts** — implement Task validation, domain errors, the
   repository protocol, the service boundary, and the client transport
   protocol.
2. **Persistence** — implement SQLite and one-file Markdown repositories, then
   run the same repository contract against both.
3. **Standard-library HTTP** — make routing, bytes, JSON, headers, status codes,
   timeouts, and cleanup visible with `http.server` and `urllib`.
4. **Flask** — use an application factory, thin routes, centralized error
   handling, the Flask test client, and a `requests` transport.
5. **FastAPI and comparison** — use typed boundary models, dependency
   injection, response models, exception handlers, generated OpenAPI, and an
   `httpx` transport. Finish by checking cross-server interoperability.

Attempt each starter milestone before reading the corresponding solution.
Useful comparisons concern behavior, readability, resource ownership, and
trade-offs—not whether two files contain identical code.

The Markdown repository coordinates load-modify-save operations only between
threads in one process. It deliberately does not teach or provide cross-process
file locking.

## Intended Python commands

These commands define the learner interface exposed by the source scaffold. Run
them from the repository root; unfinished operations fail with an explicit
milestone message.

The normal course-wide development installation includes this project's runtime
and executable-contract libraries:

```bash
python -m pip install -r requirements-dev.txt
```

To install only the project dependencies instead, use
`python -m pip install -r projects/tasks/requirements.txt`.

Select `starter` or `solution` for tests:

```bash
PROJECT_IMPLEMENTATION=starter \
  python -m pytest projects/tasks/tests -q

PROJECT_IMPLEMENTATION=solution \
  python -m pytest projects/tasks/tests -q
```

Run the project quality gates:

```bash
python -m compileall -q \
  projects/tasks/starter projects/tasks/solution projects/tasks/tests
python -m ruff format --check projects/tasks
python -m ruff check projects/tasks
python -m mypy --strict --no-incremental projects/tasks/starter
python -m mypy --strict --no-incremental projects/tasks/solution
```

Measure the solution separately so coverage from the capstones cannot hide
project gaps:

```bash
python scripts/erase_coverage_data.py
PROJECT_IMPLEMENTATION=solution \
  coverage run -m pytest projects/tasks/tests -q
coverage report --include="projects/tasks/solution/**/*.py"
```

Start any server with either persistence backend:

```bash
PYTHONPATH=projects/tasks/solution \
  python -m tasks_api.stdlib \
  --host 127.0.0.1 --port 8000 --backend sqlite --data tasks.db

PYTHONPATH=projects/tasks/solution \
  python -m tasks_api.flask \
  --host 127.0.0.1 --port 8000 --backend markdown --data tasks.md

PYTHONPATH=projects/tasks/solution \
  python -m tasks_api.fastapi \
  --host 127.0.0.1 --port 8000 --backend sqlite --data tasks.db
```

Then choose any client, regardless of which server is running:

```bash
PYTHONPATH=projects/tasks/solution \
  python -m tasks_cli.urllib \
  --base-url http://127.0.0.1:8000 add "Learn REST"

PYTHONPATH=projects/tasks/solution \
  python -m tasks_cli.requests \
  --base-url http://127.0.0.1:8000 list --completed false

PYTHONPATH=projects/tasks/solution \
  python -m tasks_cli.httpx \
  --base-url http://127.0.0.1:8000 complete 1
```

The server launchers use loopback and one local process for learning. They are
not production deployment instructions.

## What changes between implementations?

| Boundary | Makes explicit | Adds or provides |
| --- | --- | --- |
| `http.server` | Routing, byte decoding, content length, JSON serialization, headers, and status selection | Only standard-library building blocks |
| Flask | Request contexts and response conversion | Concise routing, an application factory pattern, error handlers, and a test client |
| FastAPI | Typed models and dependency wiring at the adapter boundary | Validation integration, response models, and generated OpenAPI |
| `urllib` | Request construction, encoding, response ownership, and HTTP error handling | A standard-library transport |
| `requests` | Session/response ownership and status handling | A compact synchronous API |
| `httpx` | Client lifetime, timeout configuration, and status handling | A modern API that can later extend to asynchronous use |

The shared core should not hide these differences behind a custom universal web
framework or HTTP library.
