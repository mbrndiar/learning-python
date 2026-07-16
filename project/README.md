# ⚠️ Temporary legacy: connected Task projects

> This entire `project/` tree is temporary legacy material, not a required
> capstone. Both completed capstones live under [`../capstones/`](../capstones/README.md).
> Use the [migration guide](../docs/CAPSTONE_MIGRATION.md) to map concepts and
> commands. These paths remain only until the next cleanup todo.

These three standard-library projects form one progressive example:

- [`task_rest_api/`](task_rest_api/README.md) owns remote task data in SQLite
  and exposes it through JSON over HTTP.
- [`task_rest_client/`](task_rest_client/README.md) provides a reusable Python
  client plus a dedicated command-line interface.
- [`task_manager/`](task_manager/README.md) contains the domain model and can
  select either local JSON persistence or the REST client adapter.

The projects demonstrate classes, dataclasses, protocols, dependency injection,
JSON and file I/O, HTTP, SQLite, `argparse`, exceptions, and integration tests
without hiding those concepts behind third-party frameworks.

## 🧭 How the projects connect

File mode is a single process:

```text
Task Manager CLI -> TaskManager -> FileTaskStorage -> tasks.json
```

REST mode connects all three projects:

```text
Task Manager CLI -> TaskManager -> RestTaskStorage
    -> TaskRestClient -> Task REST API -> TaskStore -> tasks.db
```

The standalone REST client CLI is another front end over the same
`TaskRestClient`. Both front ends therefore share the same remote data.

## 🧩 Reading the implementation

The legacy example uses a few standard-library techniques beyond the smallest
lesson examples:

- [`TypedDict`, `Self`, and `cast`](https://docs.python.org/3/library/typing.html)
  give mypy more precise information; they do not change runtime behavior.
- `TypeVar` lets the REST storage error helper preserve the concrete return type
  of whichever operation it runs.
- [`tempfile.mkstemp`](https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp),
  [`os.fsync`](https://docs.python.org/3/library/os.html#os.fsync), and
  [`os.replace`](https://docs.python.org/3/library/os.html#os.replace) implement
  an atomic save: write and flush a complete temporary file, then publish it in
  one replacement step so readers never see partial JSON.

These are production-oriented extensions of the resource ownership, typing, and
file-handling rules taught earlier. Read the surrounding comments first; the
linked standard-library references provide the full contracts.

## 🚀 Quick start

Run Task Manager locally:

```bash
python -m project.task_manager.cli add "Local task"
python -m project.task_manager.cli list
```

Or start the API in one terminal:

```bash
python -m project.task_rest_api.api
```

Then use either remote front end from another terminal:

```bash
python -m project.task_rest_client.cli add "Remote task"
python -m project.task_manager.cli --backend rest list
```

Commands are run from the repository root so Python can resolve the `project`
package consistently.

## 🧪 Legacy validation

```bash
python -m unittest \
  project.task_rest_api.test_api \
  project.task_rest_client.test_client \
  project.task_manager.test_task_manager -v
```

The tests use temporary JSON and SQLite files and ephemeral local ports. These
focused commands remain available while studying this temporary code.

The default mypy, coverage, and
[GitHub Actions](https://docs.github.com/en/actions) gates now cover both
completed capstones instead of this legacy tree.
