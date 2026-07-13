# Capstone Project: Task Manager

A small command-line to-do list manager that ties together concepts
from across the whole course:

- **classes & `@dataclass`** (module 6) for the `Task` model
- **custom exceptions** (module 5) for `TaskNotFoundError`
- **file I/O with JSON** (module 5) for persistence between runs
- **comprehensions & type hints** (modules 4 and 7)
- **argparse subcommands** (module 9) for the CLI
- **unittest** (module 8) for the test suite

## Files

- `task_manager.py` - the `Task` and `TaskManager` classes (the core
  logic, with no I/O beyond reading/writing the JSON storage file).
- `cli.py` - a command-line interface built on top of `task_manager.py`.
- `test_task_manager.py` - unit tests for the core logic.

## Running it

From this directory (`project/task_manager/`):

```bash
python cli.py add "Buy milk"
python cli.py add "Write more Python"
python cli.py list
python cli.py complete 1
python cli.py list --pending-only
python cli.py remove 2
```

Tasks are stored in `tasks.json` in this directory by default (pass
`--storage /path/to/file.json` to use a different location). Delete
that file to start fresh.

## Running the tests

```bash
python test_task_manager.py
```

## Ideas to extend it yourself

- Add due dates and sort tasks by them.
- Add priorities (low/medium/high) using an `enum.Enum` (module 6).
- Add a `--format json` option to `list` that prints tasks as JSON.
- Rewrite the storage layer to use `sqlite3` instead of a JSON file.
