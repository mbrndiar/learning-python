# ⚠️ Temporary legacy: Task Manager

> This path is preserved only until the next cleanup todo. It is not a required
> capstone; see the [migration guide](../../docs/CAPSTONE_MIGRATION.md) and the
> [two completed capstones](../../capstones/README.md).

Task Manager combines the course concepts in one application while allowing its
persistence mechanism to change. It can store tasks in a local JSON file or use
the paired Task REST API.

## 🏗️ Architecture

The dependency direction is:

```text
CLI -> TaskManager -> TaskStorage
                         |-- FileTaskStorage -> JSON file
                         `-- RestTaskStorage -> TaskRestClient -> HTTP API -> SQLite
```

- `task_manager.py` contains the `Task` model, `TaskStorage` protocol,
  `TaskNotFoundError`, and storage-independent `TaskManager`.
- `storage.py` contains the file strategy and the adapter around
  `TaskRestClient`.
- `cli.py` selects and constructs a strategy at the application boundary.
- `test_task_manager.py` applies one contract suite to both storage strategies.

`TaskManager` filters pending tasks but does not read files, issue HTTP
requests, allocate IDs, parse arguments, or print. Each storage implementation
owns ID allocation: `FileTaskStorage` computes local IDs, while
`RestTaskStorage` accepts the ID returned by SQLite through the API.

## 💾 Local file backend

The default requires no running service:

```bash
python -m project.task_manager.cli add "Buy milk"
python -m project.task_manager.cli list
python -m project.task_manager.cli complete 1
python -m project.task_manager.cli list --pending-only
python -m project.task_manager.cli remove 1
```

Tasks persist in `project/task_manager/tasks.json`. Select another file by
placing `--storage PATH` before the command:

```bash
python -m project.task_manager.cli --storage legacy-tasks.json add "Local task"
```

The file contains a JSON object with `next_id` and a `tasks` list. Persisting
`next_id` prevents deleted identifiers from being reused after a restart. Bare
task lists from the earlier version remain readable and are upgraded on the
next write. The loader rejects duplicate or invalid identifiers. UTF-8 writes
use a temporary file followed by an atomic replacement so interruption cannot
leave a partially written destination.

## 🌐 REST backend

First start the server:

```bash
python -m project.task_rest_api.api
```

Then choose REST storage:

```bash
python -m project.task_manager.cli --backend rest add "Shared task"
python -m project.task_manager.cli --backend rest list
python -m project.task_manager.cli --backend rest complete 1
python -m project.task_manager.cli --backend rest remove 1
```

Use `--api-url URL` before the command for a non-default server. The same
commands and `Task` objects are available with either backend. The important
difference is ownership: file mode persists directly in JSON, whereas REST mode
crosses a process boundary and the server persists in SQLite. Network and API
errors therefore apply only to REST mode. Client errors preserve the HTTP
status code, allowing adapters to translate `404` without comparing text.

## 📜 Storage contract

A strategy must list, retrieve, add, complete, and remove tasks. Unknown IDs
raise `TaskNotFoundError` at the Task Manager boundary. Adding returns the
complete stored task, including the ID assigned by that strategy.

This protocol makes another backend—such as an in-memory teaching double or a
cloud database adapter—possible without changing domain logic.

## 🧪 Test

```bash
python -m unittest project.task_manager.test_task_manager -v
```

The suite checks the shared contract against both implementations, local
round-trip persistence, server integration, ID ownership, missing tasks, and
pending-task filtering. Temporary files, databases, and ports keep tests
isolated from user data.

## ✅ Learning checklist

- Explain why `TaskManager` receives storage rather than constructing it.
- Trace a REST-backed `complete` operation through every layer.
- Identify where dictionaries become `Task` objects.
- Compare local I/O failures with HTTP failures.
- Add a strategy while leaving `TaskManager` unchanged.

## 🚀 Extension exercises

Implement these in order. Add or update a test before, or alongside, each
behavior change.

1. **In-memory storage:** add `InMemoryTaskStorage` and run the existing storage
   contract against it without changing `TaskManager`.
2. **Edit a title:** add `edit TASK_ID TITLE` across the protocol, both storage
   implementations, REST API/client and CLI.
3. **Priorities:** add a small enum-backed priority and support filtering or
   ordering tasks by it.
4. **Due dates:** accept an ISO date, validate it at the boundary and display
   overdue pending tasks.
5. **Search and sorting:** add `list --contains TEXT` and a selectable sort
   order without duplicating filtering logic in storage classes.
6. **CSV export:** export the currently selected tasks using the standard
   library `csv` module without changing persisted data.
7. **Structured API errors:** preserve HTTP status codes in `APIError` and make
   adapters branch on status rather than comparing message text.
8. **Pagination:** add `limit` and `offset` query parameters to the API and
   client, validating negative and non-integer values.

For each extension, define normal behavior, at least one boundary case and one
failure case. Keep file and REST backends behaviorally consistent through the
shared contract tests.
