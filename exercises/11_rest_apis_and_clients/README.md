# 🌐 Exercises: Module 11 - REST APIs and HTTP Clients

Practice the boundaries from
[`lessons/11_rest_apis_and_clients/`](../../lessons/11_rest_apis_and_clients/README.md)
without starting a server or using a network.

## 🧩 What you will implement

1. `validate_create_request()` and `validate_update_request()` map untrusted JSON
   objects into small Task commands while rejecting wrong types, unknown fields,
   empty updates, invalid titles, and non-Boolean completion values.
2. `parse_completed_filter()` accepts only one exact lowercase `true` or
   `false` query value.
3. `map_domain_error()` maps validation, not-found, and storage failures to the
   documented status and error envelope, sanitizing internal failures.
4. `get_task()` makes one call through an injected narrow transport with a
   positive finite timeout.
5. `decode_task_response()` checks status before trusting a success payload and
   rejects malformed API errors, content types, JSON, fields, and values.

The functions use the bounded Task contract from
[`projects/tasks/docs/SPEC.md`](../../projects/tasks/docs/SPEC.md), but the
exercise does not require any of the project's three future server
implementations. Its fake transport records requests entirely in memory.

## ▶️ Run the exercise

From the repository root:

```bash
python exercises/11_rest_apis_and_clients/exercises.py
```

Implement each `TODO` until it prints `All checks passed!`. Then compare with:

```bash
python exercises/11_rest_apis_and_clients/solutions.py
```

The reference solution is deterministic, offline, and standard-library only.
Concurrency remains in its existing `11_concurrency/` directory until the
separate course-renumbering change.
