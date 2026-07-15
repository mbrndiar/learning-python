# 🌐 Task REST API

A dependency-free JSON API that persists tasks in SQLite. It is the server used
by both `task_rest_client` and Task Manager's optional REST storage strategy.

## 🏗️ Architecture and data flow

`TaskStore` owns SQL and returns plain dictionaries. `TasksHandler` owns HTTP
routing, input validation, status codes, and JSON serialization.
`create_server()` joins both layers and lets tests inject a temporary database
and operating-system-selected port.

For example, creating a task flows through:

1. `POST /tasks` receives and validates a JSON title.
2. `TaskStore.create()` inserts the row with a parameterized SQL query.
3. SQLite assigns the identifier; no client supplies one.
4. The handler returns the complete task as JSON with status `201`.

SQLite stores `done` as `0` or `1`; `TaskStore` converts it to a JSON boolean at
the data-layer boundary. Connections are explicitly closed after short-lived
read or transaction scopes.

## ▶️ Run

From the repository root:

```bash
python -m project.task_rest_api.api
python -m project.task_rest_api.api --port 9000 --database /tmp/tasks.db
```

The default address is `127.0.0.1:8000`, and the default database is `tasks.db`
beside `api.py`. This is an educational development server, not a hardened
production deployment.

## 📜 REST contract

Every task has the shape:

```json
{"id": 1, "title": "Learn storage strategies", "done": false}
```

| Method | Route | Request | Success |
| --- | --- | --- | --- |
| `GET` | `/tasks` | none | `200` and all tasks ordered by ID |
| `GET` | `/tasks/{id}` | none | `200` and one task |
| `POST` | `/tasks` | `{"title": "..."}` | `201` and the created task |
| `PATCH` | `/tasks/{id}` | `{"done": true}` | `200` and the completed task |
| `DELETE` | `/tasks/{id}` | none | `204` and no body |

Titles must be non-empty strings. Request bodies must be JSON objects no larger
than 1 MB. Completion deliberately accepts exactly `{"done": true}`: the domain
supports completing a task, not toggling arbitrary fields.

Errors are JSON objects such as `{"error": "Task not found"}`. Invalid requests
return `400`; unknown routes or task IDs return `404`.

## 🧪 Test

```bash
python -m unittest project.task_rest_api.test_api -v
```

The integration tests start a real local HTTP server against a temporary SQLite
database and cover CRUD-like operations, validation, missing IDs, and reopening
the persistent store.
