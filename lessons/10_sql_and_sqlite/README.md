# 🗄️ Module 10: SQL and SQLite

Relational databases organize data into tables whose schema states what rows
mean and which values are valid. SQL describes the result or change you want;
the database engine chooses how to perform it. This module teaches relational
and SQL fundamentals with Python's standard-library `sqlite3` module, while
calling out where SQLite or a Python driver supplies non-portable behavior.

## 🎯 Learning objectives

After this module, you should be able to:

- model related data with tables, primary keys, foreign keys, and constraints;
- use parameterized `INSERT`, `SELECT`, `UPDATE`, and `DELETE` statements;
- filter, order, limit, join, group, and aggregate rows;
- convert database rows into application-domain values;
- treat a transaction as one atomic unit and distinguish commit from rollback;
- explain generated IDs, type affinity, pragmas, and `AUTOINCREMENT` in SQLite;
- use an index and inspect a query plan without assuming the optimizer's choice;
- place SQL behind a small repository boundary when that boundary earns its
  cost.

## 🏷️ Portability labels

The lessons use these distinctions:

- **Portable relational/SQL concept** — tables, keys, constraints,
  parameterization, CRUD, joins, grouping, transactions, and indexes exist in
  mainstream relational systems. Exact syntax and behavior still need checking
  against the target database.
- **Python DB-API / `sqlite3` spelling** — Python's `sqlite3` driver uses `?`
  placeholders, `Connection.execute()`, `sqlite3.Row`, `lastrowid`, and a
  connection context manager. Other language bindings and Python drivers may
  expose different APIs or placeholder styles.
- **SQLite-specific** — `PRAGMA`, dynamic typing and affinity,
  `INTEGER PRIMARY KEY` as a rowid alias, `AUTOINCREMENT` semantics, and
  `EXPLAIN QUERY PLAN` output are not portable contracts.

Do not copy SQL to another engine merely because its keywords look familiar.
Check its data types, generated-key syntax, identifier quoting, limit syntax,
transaction defaults, isolation model, and driver parameter markers.

## 🧱 The relational model

A table has named columns and rows. A schema records rules close to the data:

- a **primary key** identifies a row;
- a **foreign key** refers to a row in another table;
- `NOT NULL`, `UNIQUE`, `CHECK`, and `DEFAULT` express constraints;
- application-domain validation still handles rules that do not belong in, or
  cannot be expressed by, the database schema.

Constraints are not merely documentation. They protect every writer, including
scripts or future application versions that bypass today's Python checks.

## 🔎 Querying and changing rows

CRUD is shorthand for create, read, update, and delete. In SQL those operations
usually use `INSERT`, `SELECT`, `UPDATE`, and `DELETE`. Always state deterministic
ordering when callers rely on order:

```python
rows = connection.execute(
    """
    SELECT id, title
    FROM tasks
    WHERE done = ?
    ORDER BY id
    LIMIT ?
    """,
    (0, 20),
).fetchall()
```

The values are parameters; they are not formatted into SQL text. Parameter
markers represent values only, not table names, column names, keywords, or
arbitrary SQL fragments. Choose identifiers from trusted application code.

Database rows are storage representations. Convert integer flags, nullable
columns, timestamps, and identifiers into explicit domain types at one
boundary instead of leaking driver rows through the application.

## 🔗 Joins, aggregates, and indexes

An `INNER JOIN` returns matching rows from both sides. A `LEFT JOIN` keeps every
left-side row and supplies `NULL` for a missing match. Aggregates such as
`COUNT`, `SUM`, `MIN`, and `MAX` summarize groups; `WHERE` filters input rows,
while `HAVING` filters grouped results.

Indexes can reduce work for selected lookups and orderings, but they consume
space and make writes maintain another structure. Add one for an observed query
pattern, not for every column. SQLite's `EXPLAIN QUERY PLAN` is useful
orientation, but its human-readable details and optimizer choices can change
between versions. Other engines provide different explain commands and plans.

## 🔒 Transactions and resource ownership

A transaction groups statements into one unit. Commit only when the complete
unit succeeds; otherwise roll it back. Python's SQLite connection context
manager commits on normal exit and rolls back when an exception escapes:

```python
with connection:
    connection.execute("INSERT INTO tasks (title) VALUES (?)", (first,))
    connection.execute("INSERT INTO tasks (title) VALUES (?)", (second,))
```

That `with` block does **not** close the connection. The code that opens a
connection should also close it, for example with `contextlib.closing`.
Transaction modes, isolation, DDL behavior, and concurrency differ among
engines, so treat SQLite behavior as one implementation rather than universal
SQL behavior.

## 🧰 A repository boundary

A repository can translate between domain values and SQL while application
logic depends on a small `Protocol`. Injecting that capability makes a contract
test reusable across implementations. Keep ownership explicit: in the lesson,
the composition code owns the connection and the repository owns its SQL and
per-operation transaction boundaries.

Do not begin with a generic persistence framework. A direct function containing
one clear query is often enough. Add a repository when several callers need the
same domain-oriented operations, when tests need a real seam, or when multiple
adapters must satisfy the same observable contract.

## 📚 Lesson files

1. **`01_relational_model_and_sql.py`** — schema constraints, portable CRUD
   concepts, filters, ordering, limits, parameterization, and row conversion.
2. **`02_joins_aggregates_and_indexes.py`** — related tables, inner and left
   joins, grouping, aggregates, `HAVING`, indexes, and SQLite query-plan
   orientation.
3. **`03_transactions_and_sqlite.py`** — commit/rollback, generated IDs,
   connection ownership, SQLite affinity, `AUTOINCREMENT`, pragmas, and limits.
4. **`04_repository_pattern.py`** — a small `TaskRepository` protocol, SQLite
   adapter, dependency injection, and repository contract checks.

## ▶️ Run the lessons

From the repository root:

```bash
python lessons/10_sql_and_sqlite/01_relational_model_and_sql.py
python lessons/10_sql_and_sqlite/02_joins_aggregates_and_indexes.py
python lessons/10_sql_and_sqlite/03_transactions_and_sqlite.py
python lessons/10_sql_and_sqlite/04_repository_pattern.py
python exercises/10_sql_and_sqlite/solutions.py
```

All examples use in-memory databases, deterministic seed data, the standard
library, and explicit connection cleanup. Then complete the
[Module 10 exercises](../../exercises/10_sql_and_sqlite/README.md).

> **Course-order compatibility:** Concurrency remains in the existing Module 11
> folder until its separately planned renumbering. This module does not create
> the pending REST/HTTP Module 11.

## ⚠️ Common mistakes

- Building SQL by interpolating values instead of passing parameters.
- Assuming parameter markers can safely substitute identifiers or keywords.
- Omitting constraints and relying on one application path to protect data.
- Depending on row order without an `ORDER BY`.
- Turning `LEFT JOIN` into an accidental inner join by filtering nullable
  right-side rows in `WHERE`.
- Selecting non-aggregated columns without grouping them explicitly.
- Adding indexes without measuring the read benefit and write/storage cost.
- Catching an error inside a transaction block and accidentally allowing a
  partial unit to commit.
- Assuming a connection context manager closes the connection.
- Assuming SQLite's types, generated IDs, pragmas, locking, or explain output
  behave the same in a server database.
- Creating a large generic repository before the application has a concrete
  boundary to protect.

## ❓ Review questions

1. Which rules belong in a relational schema, and which still belong in domain
   validation?
2. Why are values parameterized, and why can a parameter not stand for a table
   name?
3. How do `WHERE` and `HAVING` differ?
4. When does a left join produce `NULL` values?
5. Why is an index a trade-off rather than an automatic improvement?
6. What makes two writes one atomic operation?
7. What does `with connection:` manage, and what does it leave open?
8. How do SQLite's type affinity and `AUTOINCREMENT` differ from assumptions
   common in other databases?
9. What should a row-to-domain conversion function validate or normalize?
10. When does a repository protocol simplify a design, and when is it premature
    abstraction?
