# 🧭 Applied projects

Applied projects sit between the focused lessons and the larger
[capstones](../capstones/README.md). They combine several course topics in a
bounded application while still leaving room to compare tools and design
choices.

## 📚 Projects

| Project | Focus | When to start |
| --- | --- | --- |
| [Task REST API and clients](tasks/README.md) | Domain boundaries, repository adapters, SQLite, a versioned Markdown file, HTTP/JSON, three server stacks, and three client libraries | Required after Chapter 18 and before Chapter 19 |

The Task project is required and intentionally smaller than a capstone. Work
through it after
[Chapter 18](../lessons/18_http_clients_and_transports/README.md), then continue to
[Chapter 19](../lessons/12_concurrency/README.md). Complete its
five milestones in order, run the shared contract tests after each milestone,
and compare the framework implementations only after you understand the
standard-library version.

The existing capstones remain the course's final, equally required projects.

## ✅ Setup and checks

The repository-wide development installation includes the Task project's Flask,
FastAPI, HTTP client, OpenAPI, and YAML dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run both source roots from the repository root. The starter suite verifies the
scaffold and skips unfinished milestone behavior; the solution suite exercises
the complete contract:

```bash
PROJECT_IMPLEMENTATION=starter python -m pytest projects/tasks/tests -q
PROJECT_IMPLEMENTATION=solution python -m pytest projects/tasks/tests -q
```

See the [project guide](tasks/README.md) for milestone, type-checking, server,
client, and separate branch-coverage commands.
