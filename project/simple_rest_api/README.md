# Simple REST API

A dependency-free JSON API that stores notes in SQLite. It demonstrates HTTP
methods, URL routing, status codes, request validation, JSON responses, SQL, and
persistent storage using Python's standard library.

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

## Run the tests

```bash
python test_api.py
```
