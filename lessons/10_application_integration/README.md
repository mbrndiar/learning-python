# 🔌 Module 10: Application Integration

This module connects core Python concepts into application boundaries: JSON,
SQLite and HTTP. These are the main new standard-library tools used by the
connected Task Manager projects.

## 🎯 Learning objectives

After this module, you should be able to serialize structured values, execute
parameterized SQL, manage database connections, recognize HTTP request and
response responsibilities, and validate data when it crosses a boundary.

## 🗄️ SQLite

`sqlite3` stores relational data in a local file without a separate database
server. Use `?` placeholders for values instead of formatting values into SQL:

```python
connection.execute(
    "SELECT id, title FROM tasks WHERE id = ?",
    (task_id,),
)
```

A connection used as a context manager commits a successful transaction or
rolls it back when an exception escapes; that context manager does not close the
connection. Closing is a separate resource-management responsibility, shown in
the lesson with `contextlib.closing`.

Think of a write as one unit: open a connection, begin a transaction, execute
parameterized statements, commit only when the whole unit succeeds, and close
the connection. If an exception escapes, roll back rather than leaving a
half-applied update.

## 🌐 HTTP and JSON

An HTTP API maps methods and routes to operations, validates request data, and
returns a status code plus a response body. JSON is only the transport shape;
convert it to domain objects at an application boundary instead of spreading
unvalidated dictionaries throughout the program.

Follow one request across the boundary:

```text
client builds request
→ server matches method and route
→ handler validates bytes/JSON
→ application performs the operation
→ handler chooses status, headers, and response body
→ client checks status and validates decoded data
```

A successful JSON parse proves only that the bytes contained valid JSON. It
does not prove that required keys exist, values have useful types, or the
response belongs to the endpoint the caller expected.

The standard-library server in this module is educational rather than a
production deployment. It exposes the same fundamentals hidden behind web
frameworks: routing, headers, status codes, bytes, encoding and serialization.

## 📚 Concepts covered

- **`01_sqlite_basics.py`** - schema creation, parameterized statements,
  transactions, generated IDs and row conversion.
- **`02_http_and_json.py`** - a local HTTP server, route handling, JSON
  responses, finite client timeouts and boundary validation.

## ▶️ Running

```bash
python lessons/10_application_integration/01_sqlite_basics.py
python lessons/10_application_integration/02_http_and_json.py
```

Then complete
[`exercises/10_application_integration/`](../../exercises/10_application_integration/README.md)
before reading the connected projects in [`project/`](../../project/README.md).

## ⚠️ Common mistakes

- Formatting untrusted values directly into SQL.
- Leaving database connections or HTTP responses open.
- Treating decoded JSON as trustworthy domain data without validation.
- Omitting a network timeout.
- Assuming every non-200 response contains the expected JSON shape.

## ❓ Review questions

1. Why should SQL values use placeholders?
2. What does a connection context manager do on success and failure?
3. Which responsibilities belong to an HTTP handler?
4. Why validate JSON after decoding it?
5. Why should an HTTP client use a finite timeout?
