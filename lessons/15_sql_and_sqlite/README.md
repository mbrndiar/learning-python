# 🗄️ Chapter 15: SQL and SQLite

**Semantic ID:** `module.sql-and-sqlite` ·
**Prerequisites:** `module.environments-processes-and-packaging`

## 📍 Where this fits

The first fourteen chapters taught you to model values, compose functions and
objects, isolate dependencies behind protocols, test behavior, and own files
and processes. This chapter applies those skills to persistent relational data.
You will learn SQL as a language for declaring the rows you want and Python's
standard-library `sqlite3` module as the concrete adapter that sends SQL to an
embedded SQLite database.

The order matters. First you own a `Connection`, observe the `Cursor` returned
by each operation, and turn result rows into useful Python values. Then you
design constrained tables and implement CRUD, combine related tables, inspect
query plans, control transactions, and finally place persistence behind the
small `Protocol` boundary introduced in Chapter 11.

## 🎯 Learning objectives

After this chapter, you should be able to:

- open and close a SQLite connection explicitly and explain what the connection
  context manager does and does not own;
- choose among `execute()`, `executemany()`, and `executescript()`, then use
  `lastrowid`, `rowcount`, `fetchone()`, and `fetchall()` correctly;
- configure `sqlite3.Row` at the connection boundary and map storage rows into
  domain dataclasses;
- model related data with primary keys, foreign keys, `NOT NULL`, `UNIQUE`,
  `CHECK`, and `DEFAULT` constraints;
- parameterize values in CRUD queries and explain why parameters cannot replace
  identifiers or SQL syntax;
- use inner and left joins, `GROUP BY`, aggregates, parameterized `HAVING`,
  indexes, and `EXPLAIN QUERY PLAN`;
- make several writes one atomic unit with explicit commit/rollback or
  `with connection:`;
- explain SQLite-specific foreign-key settings, type affinity, generated IDs,
  `AUTOINCREMENT`, in-memory databases, and write-concurrency limits;
- implement both an in-memory repository and a SQLite repository under one
  behavior contract.

## 🧠 The relational mental model

A **database** contains tables. A **table** has named columns and rows, while
its **schema** records rules for every writer:

- a **primary key** identifies one row;
- a **foreign key** points to a row in another table;
- `NOT NULL`, `UNIQUE`, `CHECK`, and `DEFAULT` constrain valid values;
- an **index** is an additional structure that can accelerate selected reads at
  the cost of storage and write work;
- a **transaction** makes a group of statements one atomic unit: all of it is
  committed, or all of it is rolled back.

SQL is declarative. A query states the result you need; the database optimizer
chooses an execution plan. Python's `sqlite3` module implements the Python
DB-API for one specific engine. Keep three layers distinct:

1. **Relational and SQL concepts** such as tables, constraints, joins,
   aggregates, transactions, and indexes are broadly portable.
2. **Python `sqlite3` API spellings** such as `?` placeholders,
   `Connection.execute()`, `sqlite3.Row`, and `Cursor.lastrowid` belong to this
   driver.
3. **SQLite-specific behavior** includes `PRAGMA`, type affinity,
   `INTEGER PRIMARY KEY` as a rowid alias, `AUTOINCREMENT`, and
   `EXPLAIN QUERY PLAN` output.

Other databases may use different types, generated-key syntax, placeholder
styles, transaction defaults, locking models, and plan formats.

## 🔌 1. Own the connection before writing SQL

`sqlite3.connect(path)` opens a database and returns a `Connection`. The special
path `":memory:"` creates a database private to that connection; its contents
disappear when the connection closes.

```python
from contextlib import closing
import sqlite3

with closing(sqlite3.connect(":memory:")) as connection:
    connection.row_factory = sqlite3.Row
    ...
```

`contextlib.closing()` owns the resource lifetime and calls `close()`. This is
different from `with connection:`, which owns only transaction completion:
normal exit commits a pending transaction and an escaping exception rolls it
back. It neither starts a transaction by itself nor closes the connection.

Set `connection.row_factory = sqlite3.Row` immediately after connecting and
before creating cursors. Rows created afterward support both positional access
(`row[0]`) and readable name access (`row["title"]`).

## 🧭 2. Follow the `sqlite3` operation ladder

The connection offers cursor-creating shortcuts:

```python
cursor = connection.execute(
    "INSERT INTO notes (body) VALUES (?)",
    ("Read the next section",),
)
note_id = cursor.lastrowid

connection.executemany(
    "INSERT INTO notes (body) VALUES (?)",
    [("First",), ("Second",)],
)

row = connection.execute(
    "SELECT id, body FROM notes WHERE id = ?",
    (note_id,),
).fetchone()
rows = connection.execute(
    "SELECT id, body FROM notes ORDER BY id",
).fetchall()
```

- `execute()` runs one statement and returns its `Cursor`.
- `executemany()` repeats one parameterized DML statement for each parameter
  collection.
- `executescript()` runs several semicolon-separated statements. In Python
  3.11 it first commits a pending transaction; if the script itself must be
  atomic, put explicit `BEGIN;` and `COMMIT;` statements in the script.
- `lastrowid` is updated by a successful single `INSERT` or `REPLACE` through
  `execute()`, not by `executemany()` or `executescript()`.
- `rowcount` reports affected rows for completed DML. It is `-1` for statements
  such as `SELECT`, so do not use it as a universal result count.
- `fetchone()` returns the next row or `None`; `fetchall()` returns all
  remaining rows as a list, including an empty list when nothing matches.

Call `commit()` after a successful unit of writes and `rollback()` after a
failed one. Chapter 15 uses Python 3.11's `isolation_level` behavior; the
`autocommit=` parameter belongs to Python 3.12 and later.

## 🧱 3. Put invariants in the schema

This schema protects projects and tasks regardless of which program writes to
the database:

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (name <> '')
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK (title <> ''),
    priority INTEGER NOT NULL
        CHECK (typeof(priority) = 'integer' AND priority BETWEEN 1 AND 5),
    done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    UNIQUE (project_id, title),
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

SQLite foreign-key enforcement is a per-connection setting and is normally off
by default. Run the fixed statement `PRAGMA foreign_keys = ON` immediately
after connecting, before any transaction begins. Changing this pragma during a
transaction is a no-op.

Schema constraints do not replace all domain validation. Rules involving
external services, authorization, or several aggregate values may still belong
in application logic. Put rules close to the data when every writer must obey
them.

## 🛡️ 4. Parameterize values, never interpolate them

Values travel separately from SQL text:

```python
connection.execute(
    "SELECT id, title FROM tasks WHERE project_id = ? AND done = ?",
    (project_id, 0),
)
```

The `?` markers are **value positions**. They preserve quotes correctly and
prevent input from becoming executable SQL syntax. Never construct a value
with an f-string, `%`, or `.format()`.

Parameters cannot stand for a table name, column name, keyword, sort direction,
or arbitrary SQL fragment because SQLite parses that structure before binding
values. When an identifier must vary, choose it from a closed allowlist in
trusted application code and interpolate only the already-validated spelling.

For deterministic results, use `ORDER BY` whenever callers depend on order.
`LIMIT ?` is valid in SQLite because the limit is a value. Always convert rows
to domain types at one boundary instead of leaking driver rows throughout the
application.

## 🔗 5. Combine and summarize related rows

An `INNER JOIN` keeps rows that match on both sides. A `LEFT JOIN` keeps every
left-side row and supplies `NULL` for missing right-side columns. Be careful:
a predicate on the nullable right side in `WHERE` can accidentally turn a left
join into an inner join.

Aggregates such as `COUNT`, `SUM`, `MIN`, and `MAX` summarize groups:

```sql
SELECT projects.name, COUNT(tasks.id) AS task_count
FROM projects
LEFT JOIN tasks ON tasks.project_id = projects.id
GROUP BY projects.id, projects.name
HAVING COUNT(tasks.id) >= ?
ORDER BY projects.id
```

`WHERE` filters input rows before grouping; `HAVING` filters completed groups.
The threshold above remains a parameter just like any other value.

An index can reduce work for a repeated lookup, but every index consumes space
and must be updated by writes. Add one for an observed access pattern, not for
every column. SQLite's `EXPLAIN QUERY PLAN` helps you inspect whether a query
scans or searches data, but its text and optimizer choices are explicitly not
a stable application API. Test that your schema contains the intended index;
inspect plans for understanding rather than asserting exact wording.

## 🔒 6. Make transaction ownership explicit

With Python 3.11's default legacy transaction control, `execute()` and
`executemany()` implicitly open a transaction before DML when one is not
already open. Finish the unit explicitly:

```python
try:
    connection.execute(first_sql, first_parameters)
    connection.execute(second_sql, second_parameters)
except sqlite3.Error:
    connection.rollback()
    raise
else:
    connection.commit()
```

The transaction context manager expresses the same success/failure boundary
more compactly:

```python
with connection:
    connection.execute(first_sql, first_parameters)
    connection.execute(second_sql, second_parameters)
```

The context manager finishes a transaction but does not start one. Under the
chapter's default legacy transaction control, the first DML statement starts it
implicitly. A connection created with `isolation_level=None` instead runs each
statement in SQLite autocommit mode, so a multi-write unit must execute `BEGIN`
inside the context before its first write.

Do not catch the database error *inside* this block and then exit normally;
that would tell the context manager to commit. Let the exception escape the
block, then catch it outside if the application can recover.

Keep transactions short. SQLite allows multiple simultaneous readers but only
one writer at a time; a competing write can wait up to the connection's
`timeout` and then raise `OperationalError`. A connection also defaults to
`check_same_thread=True`, so using it from a different thread raises
`ProgrammingError`. Do not disable that guard casually: if a design shares a
connection, it must serialize writes itself. Chapter 19 revisits these
concurrency choices.

## 🧬 7. Understand SQLite-specific data behavior

- SQLite associates a storage class with each **value** and gives columns a
  preferred **type affinity**. An `INTEGER` column can still store text unless
  constraints or a `STRICT` table prevent it. The task schema therefore checks
  both `typeof(priority) = 'integer'` and the allowed numeric range.
- SQLite has no separate boolean storage class. This chapter stores `False` and
  `True` as constrained integers `0` and `1`, then maps them back to `bool`.
- `INTEGER PRIMARY KEY` aliases SQLite's rowid. Omitting it during an insert
  generates an unused integer, usually one greater than the current maximum.
- `AUTOINCREMENT` is not required for generated IDs. It adds overhead and is
  useful only when deleted rowids must never be reused; generated values may
  still have gaps.
- Every `sqlite3.connect(":memory:")` call creates a separate database. Use it
  for deterministic examples and tests, not as shared persistence.

## 🧰 8. Add a repository only when it earns its cost

A repository translates between domain values and storage operations while
application logic depends on a small `Protocol`. The composition root opens
and closes the connection; the SQLite repository owns its SQL and row mapping,
not the connection lifetime.

One contract can exercise both an `InMemoryTaskRepository` and a
`SQLiteTaskRepository`. That proves the adapters share observable behavior
without claiming their implementation details or performance are identical.
Start with direct query functions when one caller needs one clear operation.
Add the repository boundary when several callers share domain-oriented
operations, when application logic needs an injected seam, or when more than
one adapter must satisfy the same contract.

## 📖 Read-predict-run-modify workflow

Read each file top to bottom, predict its output, then run it:

```bash
python lessons/15_sql_and_sqlite/01_sqlite_connection_cursor_and_rows.py
python lessons/15_sql_and_sqlite/02_relational_schema_and_crud.py
python lessons/15_sql_and_sqlite/03_joins_aggregates_indexes_and_plans.py
python lessons/15_sql_and_sqlite/04_transactions_and_sqlite_behavior.py
python lessons/15_sql_and_sqlite/05_repository_and_contract_tests.py
```

### Expected output highlights

- Lesson 1 prints one fetched row, all remaining rows, and the DML row count.
- Lesson 2 prints constrained, mapped `Task` values and confirms missing
  update/delete paths return `False`.
- Lesson 3 prints inner-join, left-join, and grouped summaries plus one or more
  SQLite query-plan detail rows.
- Lesson 4 confirms rollback for both transaction styles, shows affinity and
  generated-ID behavior, and proves the connection remains open after its
  transaction context exits.
- Lesson 5 runs the same repository contract against in-memory and SQLite
  adapters.

Then change one variable and predict again: raise Lesson 3's
`minimum_task_count`, or deliberately duplicate a title in Lesson 4's atomic
pair and observe that neither insert survives.

## ⚠️ Common mistakes

- Using `with connection:` as though it closed the connection.
- Enabling `PRAGMA foreign_keys` after a transaction has already started.
- Building SQL values with string formatting instead of placeholders.
- Trying to bind a table name or `ORDER BY` direction as a parameter.
- Reading `lastrowid` from `executemany()` instead of the cursor from one
  successful `execute()`.
- Depending on row order without `ORDER BY`.
- Treating `rowcount` as a result count for `SELECT`.
- Filtering nullable right-side rows in `WHERE` after a left join.
- Catching an error inside a transaction block and accidentally committing a
  partial unit.
- Asserting exact `EXPLAIN QUERY PLAN` text or assuming an index must always be
  selected by the optimizer.
- Adding `AUTOINCREMENT` by habit or assuming SQLite column types are rigid.
- Sharing one connection across threads without an explicit synchronization
  design.

## 🧾 Summary

- The code that calls `connect()` owns `close()`; `with connection:` only
  commits or rolls back a pending transaction.
- `execute()`, `executemany()`, and `executescript()` return cursors but have
  different contracts; `lastrowid`, `rowcount`, `fetchone()`, and `fetchall()`
  each answer a specific question.
- Schema constraints protect every writer. Parameters protect values and cannot
  replace identifiers or SQL structure.
- Joins combine related rows, aggregates summarize groups, and indexes trade
  write/storage cost for selected read performance.
- SQLite has per-connection foreign-key enforcement, value-oriented type
  affinity, rowid-generated keys, one concurrent writer, and implementation-
  specific query-plan output.
- A small repository protocol can support both in-memory and SQLite adapters
  under one behavior contract while callers retain resource ownership.

## ❓ Review questions (closed notes)

1. Which object owns an open database, and why are `closing(connection)` and
   `with connection:` not interchangeable?
2. When would you choose `execute()`, `executemany()`, or `executescript()`?
3. When are `lastrowid`, `rowcount`, `fetchone()`, and `fetchall()` meaningful?
4. Why set `row_factory` on the connection immediately after `connect()`?
5. Which invariants belong in the schema, and which still belong in domain
   logic?
6. Why can a placeholder represent a title but not a table name?
7. How do `WHERE` and `HAVING` differ, and when does a left join produce
   `NULL`?
8. Why should code avoid exact assertions about `EXPLAIN QUERY PLAN` output?
9. What happens on normal and exceptional exit from `with connection:`?
10. How do type affinity, `INTEGER PRIMARY KEY`, and `AUTOINCREMENT` differ
    from common assumptions about rigid types and generated IDs?
11. What limits SQLite write concurrency, and what does `check_same_thread`
    guard?
12. What does one repository contract prove about two implementations, and
    what does it not prove?

## 📚 Authoritative references

- [`sqlite3` — DB-API 2.0 interface for SQLite databases (Python 3.11)](https://docs.python.org/3.11/library/sqlite3.html)
- [`sqlite3` transaction control](https://docs.python.org/3.11/library/sqlite3.html#sqlite3-transaction-control)
- [`sqlite3` connection context manager](https://docs.python.org/3.11/library/sqlite3.html#sqlite3-connection-context-manager)
- [`sqlite3` placeholders](https://docs.python.org/3.11/library/sqlite3.html#sqlite3-placeholders)
- [SQLite foreign-key support](https://www.sqlite.org/foreignkeys.html)
- [SQLite type affinity](https://www.sqlite.org/datatype3.html)
- [SQLite `AUTOINCREMENT`](https://www.sqlite.org/autoinc.html)
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html)
- [SQLite `EXPLAIN QUERY PLAN`](https://www.sqlite.org/eqp.html)
- [SQLite in-memory databases](https://www.sqlite.org/inmemorydb.html)

Once you can answer the review questions and have run all five lesson files,
continue to
[`exercises/15_sql_and_sqlite/`](../../exercises/15_sql_and_sqlite/README.md).
