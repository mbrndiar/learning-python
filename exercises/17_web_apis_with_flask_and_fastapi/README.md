# 🧪 Exercises: Chapter 17 — Web APIs with Flask and FastAPI

Build two in-process web adapters over one framework-neutral task service. The
exercise starts no server and makes no network request.

## 🧩 What you will implement

1. Configure strict Pydantic input and output models.
2. Build a Flask application factory with injected storage, routes, and
   centralized JSON error handlers.
3. Build a FastAPI application factory with `app.state`, `Depends`, synchronous
   handlers, response models, and centralized exception handlers.
4. Keep the observable success and error contract aligned across both
   frameworks.

The domain service, repository, public payload helper, and deterministic
evaluator are provided. Your work stays at the framework boundary.

## 📋 Contract

- `POST /tasks` accepts exactly one string `title`, strips surrounding
  whitespace, and returns a public task with status `201`.
- Titles contain 1–120 characters after stripping and may not contain control
  characters.
- Input models reject type coercion and undeclared fields.
- Public task responses contain only `id`, `title`, and `completed`; the
  repository's `internal_note` must never leave either API.
- `GET /tasks` accepts an absent `completed` filter or one exact lowercase
  `true`/`false` value.
- Validation failures use status `422` and code `validation_error`.
- Malformed Flask JSON uses status `400` and code `invalid_json`.
- Unknown routes use `404`/`not_found`; unsupported methods use
  `405`/`method_not_allowed` and preserve `Allow`.
- Each factory creates independent default state and must use an explicitly
  supplied repository even when that object is false-like.
- FastAPI dependencies and route handlers remain synchronous.
- Generated OpenAPI documents both task paths and the request/response models.

## ▶️ Run the exercise

From the repository root:

```bash
python exercises/17_web_apis_with_flask_and_fastapi/exercises.py
```

The untouched starter fails in the Pydantic-model group. Implement the `TODO`
blocks until all four groups pass. The reference solution remains locked until
you have attempted the exercise.
