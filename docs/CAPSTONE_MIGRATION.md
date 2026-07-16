# Migrating from the Task projects to the two capstones

The comparative and idiomatic capstones are complete and equally required.
The older `project/` Task Manager, REST API, and client code and tests were
removed after the capstones were completed; they are not a third capstone.
Current course work, default typing, coverage, and CI gates target both
capstones.

The current required
[`projects/tasks/`](../projects/tasks/README.md) applied project is newly
specified teaching material placed between Modules 11 and 12. It does not
restore the historical `project/` tree or turn that removed source into an
active prerequisite.

No automatic data migration is provided. Legacy `tasks.json` and `tasks.db`
files describe mutable tasks; neither data model can be converted safely into
configuration entries or immutable operational events without an
application-specific policy.

## Inspecting the removed implementation

Commit
[`5e616825a99d4f63fae54b6f768e9ec9b2cec526`](https://github.com/mbrndiar/learning-python/tree/5e616825a99d4f63fae54b6f768e9ec9b2cec526/project)
is the last pre-removal revision containing the complete legacy tree. Its Git
history path is
`5e616825a99d4f63fae54b6f768e9ec9b2cec526:project/`.

Inspect files without restoring them into the current checkout:

```bash
git ls-tree -r --name-only 5e616825a99d4f63fae54b6f768e9ec9b2cec526 -- project/
git show 5e616825a99d4f63fae54b6f768e9ec9b2cec526:project/README.md
git log --all -- project/
```

## Concept mapping

| Legacy Task concept | Comparative capstone | Idiomatic capstone |
| --- | --- | --- |
| `Task` and CRUD operations | A key/value `Entry`; `set`, `get`, `delete`, and `list` add revisions and compare-and-set expectations. | An immutable `Event`; imports append accepted events and reports query them. Events are not updated or deleted. |
| `TaskManager` application service | The CLI/domain/store boundary coordinates validated commands and atomic mutations. | Ingestion application functions coordinate sources, validation, repositories, clocks, and reports. |
| `TaskStorage` protocol | `Store` defines the storage capability used by the command boundary. | `RecordSource`, `EventRepository`, `Clock`, and `PageFetcher` split input, persistence, time, and transport capabilities. |
| `FileTaskStorage` JSON persistence | No JSON-file backend; JSON is a validated value inside the versioned SQLite store. | CSV and JSONL are streaming input formats, while accepted events and rejects persist in SQLite. |
| REST client/storage adapter | Networking is deliberately excluded from the frozen comparative contract. | `PageFetcher` and `URLPageFetcher` provide the injected, loopback-only paginated HTTP boundary. |
| Task REST API SQLite store | The exact v1 schema, v0 migration, WAL behavior, and process contention are normative. | `SQLiteEventRepository` owns atomic imports, duplicate identities, rejects, and report queries. |
| Shared storage contract tests | Frozen fixtures and real child-process scenarios test observable conformance. | Fakes, deterministic fixtures, loopback HTTP, and five milestone groups test idiomatic boundaries. |

Reuse the architectural lessons—validation at boundaries, protocols,
dependency injection, parameterized SQL, resource ownership, and deterministic
tests—but do not rename Task fields into either new domain.

## Command mapping

All commands run from the repository root.

| Historical command or workflow | Replacement |
| --- | --- |
| `python -m project.task_manager.cli add "Title"` | Comparative creation: `PYTHONPATH=capstones/comparative/solution python -m comparative_kv --db state.db set task/1 --value-json '{"title":"Title"}' --expect absent`. Idiomatic batch creation: `PYTHONPATH=capstones/idiomatic/solution python -m ingest_report --db events.db ingest --import-id csv-001 --format csv --input capstones/idiomatic/tests/fixtures/events-valid.csv`. |
| `python -m project.task_manager.cli list` | Comparative: `PYTHONPATH=capstones/comparative/solution python -m comparative_kv --db state.db list`. Idiomatic: `PYTHONPATH=capstones/idiomatic/solution python -m ingest_report --db events.db report --output text`. |
| `... complete ID` | Comparative: read the entry revision, then `set` a replacement value with `--expect REVISION`. Idiomatic events are observations and have no completion mutation. |
| `... remove ID` | Comparative: `delete KEY --expect REVISION`. Idiomatic events are not deleted by the learner contract. |
| Start `project.task_rest_api`, then use `project.task_rest_client` | Comparative has no network mode. Idiomatic HTTP ingestion uses `--format http --url LOOPBACK_URL`; tests inject transport and run only loopback fixtures. |
| Run the three `project.*.test_*` modules | Run both solution suites shown below; each capstone is required. |
| `mypy` with legacy project files in its default scope | `mypy` checks both solution packages; CI additionally runs strict mypy over both starter packages. |

```bash
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/comparative/tests -p 'test_*.py' -v
CAPSTONE_IMPLEMENTATION=solution python -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py' -v
```

Combined branch coverage also requires both suites:

```bash
coverage erase
CAPSTONE_IMPLEMENTATION=solution CAPSTONE_SUBPROCESS_COVERAGE=1 \
  coverage run --parallel-mode -m unittest \
    discover -s capstones/comparative/tests -p 'test_*.py'
CAPSTONE_IMPLEMENTATION=solution coverage run --parallel-mode -m unittest \
  discover -s capstones/idiomatic/tests -p 'test_*.py'
coverage combine
coverage report
```

## Historical source paths

These paths no longer exist in the current tree. Prefix one with
`5e616825a99d4f63fae54b6f768e9ec9b2cec526:` when using `git show`, or browse
the linked pre-removal revision:

- `project/task_manager/`
- `project/task_rest_api/`
- `project/task_rest_client/`
- generated legacy data at `project/task_manager/tasks.json` and
  `project/task_rest_api/tasks.db`

Do not build new lessons, exercises, or capstone requirements on those paths.
Their focused legacy tests and READMEs remain available only in Git history.
