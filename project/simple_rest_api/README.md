# Simple REST API

A dependency-free JSON API that stores notes in SQLite. It demonstrates HTTP
methods, URL routing, status codes, request validation, JSON responses, SQL, and
persistent storage using Python's standard library.

## How it is structured

`NoteStore` is the data layer. It creates the SQLite table and provides CRUD
operations without knowing anything about HTTP. `NotesHandler` is the transport
layer: it maps request methods and paths to store operations, validates JSON,
and converts results and failures into HTTP responses. `create_server` connects
these layers and makes it possible for tests to use a temporary database and an
ephemeral port.

A request therefore follows this path:

1. `ThreadingHTTPServer` passes it to `NotesHandler`.
2. The handler identifies the route and reads JSON when required.
3. `NoteStore` executes a parameterized SQL statement.
4. The handler serializes the result as JSON and sends an HTTP status code.

This separation keeps SQL out of routing decisions and allows the store and
HTTP behavior to be tested independently.

## Run the API

From this directory:

```bash
python api.py
```

The server listens only on `127.0.0.1:8000` by default. Try it from another
terminal:

```bash
curl http://127.0.0.1:8000/notes
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn REST", "body": "Build a small API"}'
curl http://127.0.0.1:8000/notes/1
curl -X PUT http://127.0.0.1:8000/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn REST", "body": "Finished"}'
curl -X DELETE http://127.0.0.1:8000/notes/1
```

Supported routes:

| Method | Route | Behavior |
| --- | --- | --- |
| `GET` | `/notes` | List all notes |
| `POST` | `/notes` | Create a note |
| `GET` | `/notes/{id}` | Get one note |
| `PUT` | `/notes/{id}` | Replace one note |
| `DELETE` | `/notes/{id}` | Delete one note |

Notes persist in `notes.db` by default. Use another database file with
`python api.py --database /path/to/notes.db`.

## Validation and errors

Request bodies must be JSON objects no larger than 1 MB. A note requires a
non-empty string `title`; `body` is optional but must be a string. The API
returns JSON errors with the following status codes:

| Status | Meaning |
| --- | --- |
| `400 Bad Request` | The JSON, note fields, or declared body size are invalid |
| `404 Not Found` | The route or requested note does not exist |

SQL values are passed through placeholders rather than interpolated into query
strings. The server listens on the loopback interface by default and is an
educational development server, not a production deployment.

## Run the tests

```bash
python test_api.py
```

The tests start a real server on a temporary local port and use a temporary
SQLite database, so they do not overwrite `notes.db`.

## Alternative: Flask

[Flask](https://flask.palletsprojects.com/) is a popular third-party web
framework that provides routing, request parsing, JSON responses, and error
handling at a higher level. After understanding this standard-library version,
reimplementing the same routes in Flask is a useful comparison: `NoteStore` can
remain unchanged while Flask replaces `ThreadingHTTPServer` and `NotesHandler`.

Flask is usually more concise and extensible for an application, but it also
hides some HTTP mechanics that this example intentionally exposes and adds a
dependency. Keep validation, persistence, and tests separate from route
functions in either version. For APIs centered on type annotations and
generated schemas, [FastAPI](https://fastapi.tiangolo.com/) is another common
next step.
