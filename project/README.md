# Projects

Small, complete Python applications for practicing the course material.

There are three directories because they serve two different learning goals:

- `task_manager/` is the course capstone. It is a self-contained application
  for combining the concepts taught across the lessons.
- `simple_rest_api/` and `simple_cli/` form one client-server example. The API
  owns and persists notes, while the CLI calls it over HTTP. Keeping them
  separate demonstrates the boundary between a service and its client.

All three deliberately begin with Python's standard library. This keeps the
examples runnable after installing Python and makes the underlying HTTP, JSON,
SQL, argument-parsing, and testing concepts visible. The project guides also
point to popular third-party alternatives used in production applications.

## Simple CLI Application

[`simple_cli/`](simple_cli/README.md) contains an `argparse` client for the notes
API. It provides CRUD commands and imports or exports notes as JSON files.

## Simple REST API

[`simple_rest_api/`](simple_rest_api/README.md) contains a notes API backed by
SQLite and built entirely with the standard library. It demonstrates HTTP
methods, routing, JSON, validation, status codes, persistence, and integration
tests.

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

The notes API and client are optional application examples rather than
prerequisites for the capstone. Read the API first, start it, and then use the
CLI to observe how two independently running programs communicate.
