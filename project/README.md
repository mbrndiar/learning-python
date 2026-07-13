# Projects

Small, complete Python applications for practicing the course material.

## Simple CLI Application

[`simple_cli/`](simple_cli/README.md) contains a text statistics tool built with
`argparse`. It is a beginner-friendly example of terminal input, file I/O,
error handling, and testable application structure.

## Simple REST API

[`simple_rest_api/`](simple_rest_api/README.md) contains an in-memory notes API
built entirely with the standard library. It demonstrates HTTP methods,
routing, JSON, validation, status codes, and integration tests.

## Task Manager

[`task_manager/`](task_manager/README.md) is a command-line to-do list
manager combining:

- classes and `@dataclass` (module 6) for the `Task` model
- custom exceptions (module 5) for `TaskNotFoundError`
- file I/O with JSON (module 5) for persistence between runs
- comprehensions and type hints (modules 4 and 7)
- `argparse` subcommands (module 9) for the CLI
- `unittest` (module 8) for the test suite

See [`task_manager/README.md`](task_manager/README.md) for how to run it,
its file layout, and ideas for extending it yourself.

## When to build the capstone

Work through all ten [`lessons/`](../lessons/README.md) modules and their
matching [`exercises/`](../exercises/README.md) first. This project is
meant to be read and extended once you're comfortable with classes,
exceptions, file I/O, argparse and testing.

Treat the project as an assessment rather than another demonstration. Before
opening the implementation, sketch the model, operations, storage format, and
important failures. Then compare your design with the supplied code. Follow
the staged build and self-review checklist in the
[`task_manager` guide](task_manager/README.md#build-it-as-a-staged-assessment).
