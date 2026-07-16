# 🗄️ Exercises: Module 10 - SQL and SQLite

Practice the relational and repository boundaries from
[`lessons/10_sql_and_sqlite/`](../../lessons/10_sql_and_sqlite/README.md) with
an in-memory SQLite database.

## 🧩 What you will implement

- A constrained `projects` and `tasks` schema with primary, foreign, unique,
  range, and boolean-value rules.
- Parameterized create, read, update, and delete operations.
- Filtering, deterministic ordering, and a caller-supplied result limit.
- A row-to-`Task` mapping that converts SQLite's integer flag to `bool`.
- One inner join for task/project names.
- One left-join aggregate using `COUNT`, `GROUP BY`, and `HAVING`.
- A two-statement transaction that fully rolls back after a constraint failure.
- A small `TaskRepository` protocol, SQLite adapter, injected application
  function, and reusable contract checks.

The relational goals are portable, but the exercise uses SQLite's `?`
placeholders, `INTEGER PRIMARY KEY` generated IDs, `sqlite3.Row`, and connection
transaction context manager. Revisit the lesson's
[portability labels](../../lessons/10_sql_and_sqlite/README.md#portability-labels)
before translating this code to another database or driver.

## ▶️ Run the exercise

From the repository root:

```bash
python exercises/10_sql_and_sqlite/exercises.py
```

Implement each `TODO` until the script prints `All checks passed!`. Then compare
your work with the reference implementation:

```bash
python exercises/10_sql_and_sqlite/solutions.py
```

Both scripts use only the standard library, open in-memory databases, use
deterministic data and ordering, and close every connection.

> **Course-order compatibility:** Continue to the
> [REST/HTTP Module 11 exercises](../11_rest_apis_and_clients/README.md). The
> existing concurrency exercises keep their old directory number until the
> separately planned renumbering.
