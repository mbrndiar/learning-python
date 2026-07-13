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

## Build it as a staged assessment

Reading the finished implementation is useful, but rebuilding or extending it
provides stronger evidence that you understand the course. Work in small
stages:

1. **Model:** create a `Task` with a description and completion state.
2. **Collection:** add, list, complete, and remove tasks in memory.
3. **Failures:** reject invalid data and report unknown task identifiers with
   a domain-specific exception.
4. **Persistence:** serialize tasks to JSON and reconstruct them on startup.
5. **Interface:** connect the operations to `argparse` subcommands.
6. **Tests:** cover each operation, empty storage, invalid JSON, and round-trip
   persistence using a temporary file.
7. **Polish:** improve help text and error messages without mixing terminal
   output into the core model.

After each stage, run the tests and use the application manually. Commit a
working stage before beginning the next one.

## Requirements to preserve

- Task identifiers remain unique after loading and deleting tasks.
- Completing an already-completed task has predictable behavior.
- Removing or completing an unknown identifier raises `TaskNotFoundError`.
- Saving and loading preserve every user-visible field.
- Core classes do not parse arguments or print output.
- Tests never read or overwrite a user's real task file.

Write down any new behavior before implementing an extension. For example,
decide how missing due dates sort, which priority is the default, or how invalid
stored data is reported.

## Self-review checklist

- Can you explain every class and function without reading its body?
- Does each function have one clear responsibility?
- Are expected failures represented by useful exceptions?
- Are files always closed and test files isolated?
- Do tests include boundaries and failure paths, not only normal use?
- Could another programmer discover every command through `--help`?
- Can the program be imported without starting the CLI?
