# 🔗 Connected Task Projects

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

## 🚀 Quick start

Run Task Manager locally:

```bash
python -m project.task_manager.cli add "Local task"
python -m project.task_manager.cli list
```

Or start the API and use either remote front end:

```bash
python -m project.task_rest_api.api
python -m project.task_rest_client.cli add "Remote task"
python -m project.task_manager.cli --backend rest list
```

Commands are run from the repository root so Python can resolve the `project`
package consistently.

## 🧪 Run all project tests

```bash
python -m unittest \
  project.task_rest_api.test_api \
  project.task_rest_client.test_client \
  project.task_manager.test_task_manager -v
```

The tests use temporary JSON and SQLite files and ephemeral local ports.
