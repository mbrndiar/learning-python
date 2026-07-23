"""
Exercises: Chapter 15 - SQL and SQLite

Implement the complete sqlite3 lifecycle, relational operations, SQLite
behavior checks, and two TaskRepository adapters below.

Run from the repository root:

    python exercises/15_sql_and_sqlite/exercises.py

The evaluator uses only connection-private in-memory databases and reports the
first incomplete behavior group. It checks observable results plus three API
requirements that behavior alone cannot prove: executescript() for the schema,
executemany() for the batch, parameterized HAVING, and a real parameterized
EXPLAIN QUERY PLAN call.
"""

import ast
import inspect
import re
import sqlite3
import textwrap
from collections.abc import Callable, Iterable
from contextlib import closing
from dataclasses import dataclass, replace
from typing import Protocol

_VALUE_PLACEHOLDER = r"(?:\?|:[A-Z_][A-Z0-9_]*)"
_MISSING = object()


@dataclass(frozen=True)
class Task:
    id: int
    project_id: int
    title: str
    priority: int
    done: bool


@dataclass(frozen=True)
class TaskProject:
    task_title: str
    project_name: str


@dataclass(frozen=True)
class ProjectSummary:
    project_name: str
    task_count: int
    completed_count: int


class RecordingConnection(sqlite3.Connection):
    """Test connection that records direct and cursor execute() calls."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.executed_statements: list[tuple[str, object]] = []

    def execute(
        self,
        sql: str,
        parameters: object = (),
    ) -> sqlite3.Cursor:
        self.executed_statements.append((sql, parameters))
        return super().execute(sql, parameters)

    def executemany(
        self,
        sql: str,
        parameters: Iterable[object],
    ) -> sqlite3.Cursor:
        parameter_rows = tuple(parameters)
        self.executed_statements.append((sql, parameter_rows))
        return super().executemany(sql, parameter_rows)

    def cursor(
        self,
        factory: type[sqlite3.Cursor] | None = None,
    ) -> sqlite3.Cursor:
        return super().cursor(factory or RecordingCursor)


class RecordingCursor(sqlite3.Cursor):
    """Cursor that records SQL on its owning RecordingConnection."""

    def execute(
        self,
        sql: str,
        parameters: object = (),
    ) -> sqlite3.Cursor:
        connection = self.connection
        if isinstance(connection, RecordingConnection):
            connection.executed_statements.append((sql, parameters))
        return super().execute(sql, parameters)

    def executemany(
        self,
        sql: str,
        parameters: Iterable[object],
    ) -> sqlite3.Cursor:
        parameter_rows = tuple(parameters)
        connection = self.connection
        if isinstance(connection, RecordingConnection):
            connection.executed_statements.append((sql, parameter_rows))
        return super().executemany(sql, parameter_rows)


def configure_connection(connection: sqlite3.Connection) -> None:
    """Configure readable rows and enforced foreign keys on a fresh connection."""
    # TODO: configure both connection-owned settings
    raise NotImplementedError


def create_schema(connection: sqlite3.Connection) -> None:
    """Create constrained projects, tasks, and affinity-example tables.

    Use executescript() for one multi-statement schema. projects needs a
    generated integer primary key and constrained unique non-empty name. tasks
    needs a generated key, project foreign key, unique non-empty title per
    project, integer-only priority 1-5, and constrained 0/1 done default.
    affinity_examples needs one INTEGER-affinity value column.
    """
    # TODO: create the complete schema
    raise NotImplementedError


def add_project(connection: sqlite3.Connection, name: str) -> int:
    """Insert a project as one transaction and return its generated ID."""
    # TODO: parameterized INSERT + individual cursor.lastrowid
    raise NotImplementedError


def add_task(
    connection: sqlite3.Connection,
    project_id: int,
    title: str,
    priority: int,
) -> int:
    """Insert one unfinished task and return its generated ID."""
    # TODO: parameterized INSERT + individual cursor.lastrowid
    raise NotImplementedError


def add_tasks(
    connection: sqlite3.Connection,
    project_id: int,
    tasks: Iterable[tuple[str, int]],
) -> int:
    """Batch (title, priority) pairs with executemany and return rowcount."""
    # TODO: explicitly begin one transaction, then make one executemany() call
    raise NotImplementedError


def row_to_task(row: sqlite3.Row) -> Task:
    """Map a storage row to Task, including an explicit bool conversion."""
    # TODO: map all five named columns
    raise NotImplementedError


def find_task(connection: sqlite3.Connection, task_id: int) -> Task | None:
    """Return one mapped task, or None when the ID does not exist."""
    # TODO: parameterized SELECT + fetchone()
    raise NotImplementedError


def list_tasks(
    connection: sqlite3.Connection,
    *,
    done: bool | None,
    minimum_priority: int,
    limit: int,
) -> list[Task]:
    """Filter and order tasks; reject a negative result limit."""
    # TODO: support done=True, done=False, and done=None with value parameters
    raise NotImplementedError


def set_task_done(
    connection: sqlite3.Connection,
    task_id: int,
    done: bool,
) -> bool:
    """Update one task and report whether it existed."""
    # TODO: parameterized UPDATE + cursor.rowcount
    raise NotImplementedError


def delete_task(connection: sqlite3.Connection, task_id: int) -> bool:
    """Delete one task and report whether it existed."""
    # TODO: parameterized DELETE + cursor.rowcount
    raise NotImplementedError


def list_tasks_with_projects(
    connection: sqlite3.Connection,
) -> list[TaskProject]:
    """Use an inner join and return mapped rows in task-ID order."""
    # TODO: join tasks to projects
    raise NotImplementedError


def summarize_projects(
    connection: sqlite3.Connection,
    minimum_task_count: int,
) -> list[ProjectSummary]:
    """Summarize every qualifying project in project-ID order.

    Use LEFT JOIN, COUNT, GROUP BY, a parameterized HAVING threshold, and a
    conditional aggregate for completed_count.
    """
    # TODO: grouped left-join query + row mapping
    raise NotImplementedError


def add_lookup_index(connection: sqlite3.Connection) -> None:
    """Create idx_tasks_project_done on (project_id, done)."""
    # TODO: create and commit the named index
    raise NotImplementedError


def explain_open_task_lookup(
    connection: sqlite3.Connection,
    project_id: int,
) -> list[str]:
    """Return non-empty detail strings for an open-task EXPLAIN QUERY PLAN."""
    # TODO: parameterized plan for project_id = ? AND done = 0
    raise NotImplementedError


def add_pair_atomically(
    connection: sqlite3.Connection,
    project_id: int,
    first_title: str,
    second_title: str,
) -> None:
    """Insert both priority-1 tasks atomically."""
    # TODO: explicitly begin one transaction containing two parameterized INSERTs
    raise NotImplementedError


def store_affinity_values(
    connection: sqlite3.Connection,
    values: Iterable[object],
) -> list[tuple[str, object]]:
    """Store values and return (typeof(value), value) rows in insertion order."""
    # TODO: batch values, then query SQLite storage classes and values
    raise NotImplementedError


class TaskRepository(Protocol):
    def add(self, project_id: int, title: str, priority: int) -> Task:
        """Store and return a new task."""

    def find(self, task_id: int) -> Task | None:
        """Return one task, or None when it does not exist."""

    def list(
        self,
        *,
        done: bool | None,
        minimum_priority: int,
        limit: int,
    ) -> list[Task]:
        """Return matching tasks; reject a negative result limit."""

    def set_done(self, task_id: int, done: bool) -> bool:
        """Update one task and report whether it existed."""


class InMemoryTaskRepository:
    """A dict-backed TaskRepository with generated IDs starting at 1."""

    def __init__(self) -> None:
        # TODO: initialize owned task state and the next generated ID
        raise NotImplementedError

    def add(self, project_id: int, title: str, priority: int) -> Task:
        # TODO: store and return one unfinished Task
        raise NotImplementedError

    def find(self, task_id: int) -> Task | None:
        # TODO: return one task or None
        raise NotImplementedError

    def list(
        self,
        *,
        done: bool | None,
        minimum_priority: int,
        limit: int,
    ) -> list[Task]:
        # TODO: validate, filter, order, and limit exactly like list_tasks()
        raise NotImplementedError

    def set_done(self, task_id: int, done: bool) -> bool:
        # TODO: replace the immutable Task, preserving the missing False path
        raise NotImplementedError


class SQLiteTaskRepository:
    """A TaskRepository over an injected, caller-owned SQLite connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        # TODO: retain the injected connection without opening or closing one
        raise NotImplementedError

    def add(self, project_id: int, title: str, priority: int) -> Task:
        # TODO: delegate to the relational functions and return the Task
        raise NotImplementedError

    def find(self, task_id: int) -> Task | None:
        # TODO: delegate to the relational functions
        raise NotImplementedError

    def list(
        self,
        *,
        done: bool | None,
        minimum_priority: int,
        limit: int,
    ) -> list[Task]:
        # TODO: delegate to the relational functions
        raise NotImplementedError

    def set_done(self, task_id: int, done: bool) -> bool:
        # TODO: delegate to the relational functions
        raise NotImplementedError


def finish_next_task(repository: TaskRepository) -> Task | None:
    """Complete and return the highest-priority open task, if one exists."""
    # TODO: use only the TaskRepository protocol
    raise NotImplementedError


def assert_repository_contract(
    repository: TaskRepository,
    project_id: int,
    mutation_complete: Callable[[], None] | None = None,
) -> None:
    """Exercise the same observable behavior against every fresh adapter."""
    assert finish_next_task(repository) is None

    low = repository.add(project_id, "Low priority", 1)
    if mutation_complete is not None:
        mutation_complete()
    high = repository.add(project_id, "High priority", 5)
    if mutation_complete is not None:
        mutation_complete()

    assert low == Task(1, project_id, "Low priority", 1, False)
    assert high == Task(2, project_id, "High priority", 5, False)
    assert repository.find(low.id) == low
    assert repository.find(999) is None
    assert repository.list(done=False, minimum_priority=1, limit=10) == [high, low]
    assert repository.list(done=False, minimum_priority=5, limit=10) == [high]
    assert repository.list(done=False, minimum_priority=1, limit=1) == [high]
    assert repository.list(done=False, minimum_priority=1, limit=0) == []
    try:
        repository.list(done=False, minimum_priority=1, limit=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("repository list must reject a negative limit")
    assert repository.set_done(999, True) is False
    if mutation_complete is not None:
        mutation_complete()

    completed = finish_next_task(repository)
    if mutation_complete is not None:
        mutation_complete()
    assert completed == replace(high, done=True)
    assert repository.find(high.id) == completed
    assert repository.list(done=True, minimum_priority=1, limit=10) == [completed]
    assert repository.list(done=None, minimum_priority=1, limit=10) == [
        completed,
        low,
    ]
    assert finish_next_task(repository) == replace(low, done=True)
    if mutation_complete is not None:
        mutation_complete()
    assert finish_next_task(repository) is None


def _calls_method(function: Callable[..., object], method_name: str) -> bool:
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == method_name
        for node in ast.walk(tree)
    )


def _assert_integrity_error(
    connection: sqlite3.Connection,
    sql: str,
    parameters: object,
    message: str,
) -> None:
    try:
        with connection:
            connection.execute(sql, parameters)
    except sqlite3.IntegrityError:
        return
    raise AssertionError(message)


def _parameter_sets(parameters: object) -> list[object]:
    if (
        isinstance(parameters, (list, tuple))
        and parameters
        and all(isinstance(row, (dict, list, tuple)) for row in parameters)
    ):
        return list(parameters)
    return [parameters]


def _bindings_match(sql: str, parameters: object) -> bool:
    placeholders = re.findall(_VALUE_PLACEHOLDER, sql, flags=re.IGNORECASE)
    if not placeholders:
        return False
    if all(placeholder == "?" for placeholder in placeholders):
        return isinstance(parameters, (list, tuple)) and len(parameters) == len(
            placeholders
        )
    if any(placeholder == "?" for placeholder in placeholders):
        return False
    names = {placeholder[1:] for placeholder in placeholders}
    return isinstance(parameters, dict) and names.issubset(parameters)


def _bound_parameter_values(sql: str, parameters: object) -> list[object]:
    placeholders = re.findall(_VALUE_PLACEHOLDER, sql, flags=re.IGNORECASE)
    if all(placeholder == "?" for placeholder in placeholders):
        return list(parameters) if isinstance(parameters, (list, tuple)) else []
    if isinstance(parameters, dict):
        return [
            parameters[placeholder[1:]]
            for placeholder in placeholders
            if placeholder[1:] in parameters
        ]
    return []


def _all_bound_parameter_values(sql: str, parameters: object) -> list[object]:
    values: list[object] = []
    for parameter_set in _parameter_sets(parameters):
        values.extend(_bound_parameter_values(sql, parameter_set))
    return values


def _bound_value(
    sql: str,
    parameters: object,
    match: re.Match[str],
    group: str,
) -> object:
    placeholder = match.group(group)
    if placeholder == "?":
        index = sql[: match.start(group)].count("?")
        if isinstance(parameters, (list, tuple)) and index < len(parameters):
            return parameters[index]
        return _MISSING
    if isinstance(parameters, dict):
        return parameters.get(placeholder[1:], _MISSING)
    return _MISSING


def _runtime_call_matches(
    call: tuple[str, object],
    *patterns: str,
    expected_values: tuple[object, ...] = (),
) -> bool:
    sql, parameters = call
    normalized = " ".join(sql.upper().split())
    if not all(re.search(pattern, normalized) for pattern in patterns):
        return False
    parameter_sets = _parameter_sets(parameters)
    if not parameter_sets or not all(
        _bindings_match(sql, parameter_set) for parameter_set in parameter_sets
    ):
        return False
    values = _all_bound_parameter_values(sql, parameters)
    return all(expected in values for expected in expected_values)


def _is_open_task_plan_call(
    sql: str,
    parameters: object,
    expected_project_id: int,
) -> bool:
    normalized = " ".join(sql.upper().split())
    predicate = re.search(
        (
            rf"\bWHERE\b"
            rf"(?:(?!\b(?:GROUP BY|HAVING|ORDER BY|LIMIT|OFFSET)\b).)*?"
            rf"\bPROJECT_ID\s*=\s*(?P<project>{_VALUE_PLACEHOLDER})"
        ),
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )
    done_predicate = re.search(
        (
            r"\bWHERE\b"
            r"(?:(?!\b(?:GROUP BY|HAVING|ORDER BY|LIMIT|OFFSET)\b).)*?"
            r"\bDONE\s*=\s*0\b"
        ),
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parameter_sets = _parameter_sets(parameters)
    return (
        "EXPLAIN QUERY PLAN" in normalized
        and "SELECT" in normalized
        and "FROM" in normalized
        and "TASKS" in normalized
        and done_predicate is not None
        and predicate is not None
        and len(parameter_sets) == 1
        and _bindings_match(sql, parameter_sets[0])
        and _bound_value(sql, parameter_sets[0], predicate, "project")
        == expected_project_id
    )


def _plan_details(
    connection: sqlite3.Connection,
    call: tuple[str, object],
) -> list[str]:
    sql, parameters = call
    rows = sqlite3.Connection.execute(connection, sql, parameters).fetchall()
    return [str(row["detail"]) for row in rows]


def _planned_query_rows(
    connection: sqlite3.Connection,
    call: tuple[str, object],
) -> list[tuple[object, ...]]:
    sql, parameters = call
    query = re.sub(
        r"^\s*EXPLAIN\s+QUERY\s+PLAN\s+",
        "",
        sql,
        count=1,
        flags=re.IGNORECASE,
    )
    rows = sqlite3.Connection.execute(connection, query, parameters).fetchall()
    return [tuple(row) for row in rows]


def _bound_integer_matches(
    sql: str,
    parameters: object,
    match: re.Match[str],
    group: str,
    expected: int,
    *,
    allow_bool: bool = False,
) -> bool:
    token = match.group(group)
    if token == str(expected):
        return True
    value = _bound_value(sql, parameters, match, group)
    return value == expected and (
        type(value) is int or (allow_bool and type(value) is bool)
    )


def _is_bound_atomic_insert(sql: str, parameters: object) -> bool:
    match = re.search(
        (
            rf"\bINSERT INTO TASKS\b.*\bVALUES\s*\(\s*"
            rf"(?P<project>{_VALUE_PLACEHOLDER})\s*,\s*"
            rf"(?P<title>{_VALUE_PLACEHOLDER})\s*,\s*"
            rf"(?P<priority>1|{_VALUE_PLACEHOLDER})\s*"
            rf"(?:,\s*(?P<done>0|{_VALUE_PLACEHOLDER})\s*)?\)"
        ),
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parameter_sets = _parameter_sets(parameters)
    if (
        match is None
        or len(parameter_sets) != 1
        or not _bindings_match(sql, parameter_sets[0])
    ):
        return False
    parameter_set = parameter_sets[0]
    done = match.group("done")
    return _bound_integer_matches(
        sql,
        parameter_set,
        match,
        "priority",
        1,
    ) and (
        done is None
        or _bound_integer_matches(
            sql,
            parameter_set,
            match,
            "done",
            0,
            allow_bool=True,
        )
    )


def _has_deterministic_task_order(sql: str) -> bool:
    normalized = " ".join(sql.upper().split())
    return (
        re.search(
            (
                r"ORDER BY (?:\w+\.)?PRIORITY DESC\s*,\s*"
                r"(?:\w+\.)?ID(?: ASC)?(?=\s+(?:LIMIT|OFFSET)\b|\s*$|;)"
            ),
            normalized,
        )
        is not None
    )


def _has_join_task_id_order(sql: str) -> bool:
    normalized = " ".join(sql.upper().split())
    from_tasks = re.search(
        r"\bFROM\s+TASKS\b(?:\s+(?:AS\s+)?(?P<alias>[A-Z_][A-Z0-9_]*))?",
        normalized,
    )
    if from_tasks is None:
        return False
    alias = from_tasks.group("alias")
    if alias in {None, "INNER", "JOIN", "LEFT", "RIGHT", "FULL", "CROSS", "NATURAL"}:
        alias = "TASKS"
    return (
        re.search(
            rf"ORDER BY {re.escape(alias)}\.ID(?: ASC)?(?=\s*$|;)",
            normalized,
        )
        is not None
    )


def _has_project_id_order(sql: str) -> bool:
    normalized = " ".join(sql.upper().split())
    return (
        "GROUP BY" in normalized
        and re.search(
            r"ORDER BY (?:\w+\.)?ID(?: ASC)?(?=\s*$|;)",
            normalized,
        )
        is not None
    )


def _has_affinity_rowid_order(sql: str) -> bool:
    normalized = " ".join(sql.upper().split())
    return (
        "AFFINITY_EXAMPLES" in normalized
        and re.search(
            r"ORDER BY (?:\w+\.)?ROWID(?: ASC)?(?=\s*$|;)",
            normalized,
        )
        is not None
    )


def evaluate_connection_schema_and_crud() -> None:
    connection = sqlite3.connect(":memory:", factory=RecordingConnection)
    assert isinstance(connection, RecordingConnection)
    with closing(connection) as database:
        configure_connection(database)
        assert database.row_factory is sqlite3.Row, (
            "configure sqlite3.Row on the connection"
        )
        foreign_keys = database.execute("PRAGMA foreign_keys").fetchone()[0]
        assert foreign_keys == 1, "enable foreign keys before creating the schema"

        create_schema(database)
        assert _calls_method(create_schema, "executescript"), (
            "create the multi-statement schema with executescript()"
        )
        assert database.in_transaction is False, "finish the schema script transaction"

        course_id = add_project(database, "Course")
        empty_id = add_project(database, "Empty")
        assert (course_id, empty_id) == (1, 2), "return generated project IDs"
        project_statement_count = len(database.executed_statements)
        quoted_project_id = add_project(database, "O'Brien's project")
        assert quoted_project_id == 3, "bind project names as SQL values"
        assert any(
            _runtime_call_matches(
                call,
                rf"\bINSERT INTO PROJECTS\b.*\bVALUES\s*\(\s*{_VALUE_PLACEHOLDER}\s*\)",
                expected_values=("O'Brien's project",),
            )
            for call in database.executed_statements[project_statement_count:]
        ), "bind the project name in its VALUES position"
        assert database.in_transaction is False, (
            "finish each project insert transaction"
        )

        for parameters in (("",), (None,), ("Course",)):
            _assert_integrity_error(
                database,
                "INSERT INTO projects (name) VALUES (?)",
                parameters,
                "the schema must require a non-empty unique project name",
            )

        batch_statement_count = len(database.executed_statements)
        inserted = add_tasks(
            database,
            course_id,
            [("Write queries", 3), ("Read constraints", 5)],
        )
        assert inserted == 2
        assert _calls_method(add_tasks, "executemany"), "batch tasks with executemany()"
        assert any(
            _runtime_call_matches(
                call,
                rf"\bINSERT INTO TASKS\b.*\bVALUES\s*\(\s*"
                rf"{_VALUE_PLACEHOLDER}\s*,\s*{_VALUE_PLACEHOLDER}\s*,\s*"
                rf"{_VALUE_PLACEHOLDER}\s*"
                rf"(?:,\s*(?:0|{_VALUE_PLACEHOLDER})\s*)?\)",
                expected_values=(
                    course_id,
                    "Write queries",
                    3,
                    "Read constraints",
                    5,
                ),
            )
            for call in database.executed_statements[batch_statement_count:]
        ), "bind every batched task value"
        assert database.in_transaction is False, (
            "finish the successful batch transaction"
        )
        try:
            add_tasks(
                database,
                course_id,
                [("Batch must roll back", 3), ("", 3)],
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("the invalid batched title should fail")
        assert database.in_transaction is False, (
            "roll back the failed batch transaction"
        )
        rolled_back_batch = database.execute(
            "SELECT 1 FROM tasks WHERE title = ?",
            ("Batch must roll back",),
        ).fetchone()
        assert rolled_back_batch is None, "roll back every row in a failed batch"

        task_statement_count = len(database.executed_statements)
        quoted_id = add_task(database, course_id, "Read O'Brien's notes", 4)
        assert quoted_id == 3, "return the generated ID from one execute() cursor"
        assert any(
            _runtime_call_matches(
                call,
                rf"\bINSERT INTO TASKS\b.*\bVALUES\s*\(\s*"
                rf"{_VALUE_PLACEHOLDER}\s*,\s*{_VALUE_PLACEHOLDER}\s*,\s*"
                rf"{_VALUE_PLACEHOLDER}\s*"
                rf"(?:,\s*(?:0|{_VALUE_PLACEHOLDER})\s*)?\)",
                expected_values=(course_id, "Read O'Brien's notes", 4),
            )
            for call in database.executed_statements[task_statement_count:]
        ), "bind every single-task value"
        assert database.in_transaction is False, "finish the task insert transaction"
        find_statement_count = len(database.executed_statements)
        quoted_task = find_task(database, quoted_id)
        assert quoted_task is not None
        assert quoted_task == Task(
            quoted_id,
            course_id,
            "Read O'Brien's notes",
            4,
            False,
        )
        assert type(quoted_task.done) is bool, "map the done flag to a real bool"
        assert any(
            _runtime_call_matches(
                call,
                rf"\bFROM TASKS\b.*\bWHERE (?:\w+\.)?ID\s*=\s*{_VALUE_PLACEHOLDER}",
                expected_values=(quoted_id,),
            )
            for call in database.executed_statements[find_statement_count:]
        ), "bind the task ID in find_task"
        assert find_task(database, 999) is None

        list_statement_count = len(database.executed_statements)
        open_tasks = list_tasks(
            database,
            done=False,
            minimum_priority=4,
            limit=2,
        )
        assert open_tasks == [
            Task(2, course_id, "Read constraints", 5, False),
            Task(quoted_id, course_id, "Read O'Brien's notes", 4, False),
        ]
        assert any(
            _has_deterministic_task_order(sql)
            for sql, _parameters in database.executed_statements[list_statement_count:]
        ), "order equal-priority tasks by ID ascending"
        assert any(
            _runtime_call_matches(
                call,
                r"\bFROM TASKS\b",
                rf"\bDONE\s*=\s*{_VALUE_PLACEHOLDER}",
                rf"\bPRIORITY\s*>=\s*{_VALUE_PLACEHOLDER}",
                rf"\bLIMIT\s+{_VALUE_PLACEHOLDER}",
                expected_values=(0, 4, 2),
            )
            for call in database.executed_statements[list_statement_count:]
        ), "bind every list_tasks filter and limit value"
        assert (
            list_tasks(
                database,
                done=False,
                minimum_priority=1,
                limit=0,
            )
            == []
        )
        try:
            list_tasks(
                database,
                done=False,
                minimum_priority=1,
                limit=-1,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("list_tasks must reject a negative limit")
        update_statement_count = len(database.executed_statements)
        assert set_task_done(database, quoted_id, True) is True
        assert any(
            _runtime_call_matches(
                call,
                rf"\bUPDATE TASKS\b.*\bSET DONE\s*=\s*{_VALUE_PLACEHOLDER}\s+"
                rf"WHERE ID\s*=\s*{_VALUE_PLACEHOLDER}",
                expected_values=(1, quoted_id),
            )
            for call in database.executed_statements[update_statement_count:]
        ), "bind the update value and task ID"
        assert database.in_transaction is False, "finish the update transaction"
        assert set_task_done(database, 999, True) is False
        assert database.in_transaction is False, (
            "finish a missing-target update transaction"
        )
        delete_statement_count = len(database.executed_statements)
        assert delete_task(database, 1) is True
        assert any(
            _runtime_call_matches(
                call,
                rf"\bDELETE FROM TASKS\b.*\bWHERE ID\s*=\s*{_VALUE_PLACEHOLDER}",
                expected_values=(1,),
            )
            for call in database.executed_statements[delete_statement_count:]
        ), "bind the task ID in delete_task"
        assert database.in_transaction is False, "finish the delete transaction"
        assert delete_task(database, 1) is False
        assert database.in_transaction is False, (
            "finish a missing-target delete transaction"
        )
        mixed_tasks = list_tasks(
            database,
            done=None,
            minimum_priority=1,
            limit=10,
        )
        assert mixed_tasks == [
            Task(2, course_id, "Read constraints", 5, False),
            Task(quoted_id, course_id, "Read O'Brien's notes", 4, True),
        ], "done=None must preserve both open and completed tasks"
        assert all(type(task.done) is bool for task in mixed_tasks), (
            "map every done flag to bool"
        )

        task_insert = """
            INSERT INTO tasks (project_id, title, priority, done)
            VALUES (?, ?, ?, ?)
        """
        with database:
            database.execute(
                task_insert,
                (course_id, "Shared title", 3, 0),
            )
            database.execute(
                task_insert,
                (empty_id, "Shared title", 3, 0),
            )
            default_cursor = database.execute(
                """
                INSERT INTO tasks (project_id, title, priority)
                VALUES (?, ?, ?)
                """,
                (course_id, "Default done", 3),
            )
        default_row = database.execute(
            "SELECT done FROM tasks WHERE id = ?",
            (default_cursor.lastrowid,),
        ).fetchone()
        assert default_row["done"] == 0, "the schema must default done to 0"

        invalid_tasks = [
            (None, "Missing project ID", 3, 0),
            (course_id, None, 3, 0),
            (course_id, "", 3, 0),
            (course_id, "Invalid low priority", 0, 0),
            (course_id, "Invalid high priority", 6, 0),
            (course_id, "Fractional priority", 1.5, 0),
            (course_id, "Missing priority", None, 0),
            (999, "Missing project", 3, 0),
            (course_id, "Shared title", 3, 0),
            (course_id, "Invalid done flag", 3, 2),
            (course_id, "Missing done flag", 3, None),
        ]
        for parameters in invalid_tasks:
            _assert_integrity_error(
                database,
                task_insert,
                parameters,
                "the schema must enforce every documented task constraint",
            )


def evaluate_queries_transactions_and_sqlite() -> None:
    connection = sqlite3.connect(":memory:", factory=RecordingConnection)
    assert isinstance(connection, RecordingConnection)
    with closing(connection) as database:
        configure_connection(database)
        create_schema(database)
        assert database.in_transaction is False, "finish the schema script transaction"
        course_id = add_project(database, "Course")
        empty_id = add_project(database, "Empty")
        taskless_id = add_project(database, "Taskless")
        assert (empty_id, taskless_id) == (2, 3)
        assert database.in_transaction is False

        add_tasks(
            database,
            course_id,
            [
                ("Learn SQL", 5),
                ("Practice joins", 3),
                ("Inspect a plan", 1),
            ],
        )
        assert database.in_transaction is False
        assert set_task_done(database, 1, True)
        assert database.in_transaction is False

        # Interleave task IDs across projects so ordering by project ID differs
        # from ordering by task ID. The orphan then distinguishes a real inner
        # join from outer, cross, and natural substitutions.
        with database:
            database.execute(
                """
                INSERT INTO tasks (id, project_id, title, priority, done)
                VALUES (?, ?, ?, ?, ?)
                """,
                (0, empty_id, "Empty project task", 1, 0),
            )
        database.execute("PRAGMA foreign_keys = OFF")
        with database:
            database.execute(
                """
                INSERT INTO tasks (id, project_id, title, priority, done)
                VALUES (?, ?, ?, ?, ?)
                """,
                (-1, 999, "Orphan evaluator row", 1, 0),
            )
        database.execute("PRAGMA foreign_keys = ON")
        assert database.execute("PRAGMA foreign_keys").fetchone()[0] == 1

        join_statement_count = len(database.executed_statements)
        joined_tasks = list_tasks_with_projects(database)
        assert joined_tasks == [
            TaskProject("Empty project task", "Empty"),
            TaskProject("Learn SQL", "Course"),
            TaskProject("Practice joins", "Course"),
            TaskProject("Inspect a plan", "Course"),
        ]
        assert any(
            _has_join_task_id_order(sql)
            for sql, _parameters in database.executed_statements[join_statement_count:]
        ), "order joined tasks by task ID"
        assert summarize_projects(database, minimum_task_count=0) == [
            ProjectSummary("Course", 3, 1),
            ProjectSummary("Empty", 1, 0),
            ProjectSummary("Taskless", 0, 0),
        ]
        assert summarize_projects(database, minimum_task_count=1) == [
            ProjectSummary("Course", 3, 1),
            ProjectSummary("Empty", 1, 0),
        ]
        summary_statement_count = len(database.executed_statements)
        assert summarize_projects(database, minimum_task_count=4) == []
        assert any(
            _has_project_id_order(sql)
            for sql, _parameters in database.executed_statements
        ), "order grouped project summaries by project ID"
        assert any(
            _runtime_call_matches(
                call,
                rf"\bHAVING\b.+>=\s*{_VALUE_PLACEHOLDER}",
                expected_values=(4,),
            )
            for call in database.executed_statements[summary_statement_count:]
        ), "bind the minimum task count in the HAVING comparison"

        add_lookup_index(database)
        assert database.in_transaction is False, "finish the index transaction"
        index_columns = [
            str(row["name"])
            for row in database.execute(
                "PRAGMA index_info('idx_tasks_project_done')"
            ).fetchall()
        ]
        assert index_columns == ["project_id", "done"], (
            "create idx_tasks_project_done on (project_id, done)"
        )

        statement_count = len(database.executed_statements)
        plan = explain_open_task_lookup(database, course_id)
        assert plan and all(plan), "return non-empty query-plan detail rows"
        plan_calls = database.executed_statements[statement_count:]
        matching_plan_calls = [
            call for call in plan_calls if _is_open_task_plan_call(*call, course_id)
        ]
        assert matching_plan_calls, (
            "execute a parameterized query plan for the open-task lookup"
        )
        assert any(
            plan == _plan_details(database, call) for call in matching_plan_calls
        ), "return the detail field from every query-plan row"
        expected_lookup_rows = [
            tuple(row)
            for row in sqlite3.Connection.execute(
                database,
                """
                SELECT id, title
                FROM tasks
                WHERE project_id = ? AND done = 0
                """,
                (course_id,),
            ).fetchall()
        ]
        assert any(
            sorted(_planned_query_rows(database, call)) == sorted(expected_lookup_rows)
            for call in matching_plan_calls
        ), "plan the filtered open-task lookup for only the requested project"

        atomic_statement_count = len(database.executed_statements)
        add_pair_atomically(
            database,
            course_id,
            "Atomic first",
            "Atomic second",
        )
        successful_atomic_calls = [
            call
            for call in database.executed_statements[atomic_statement_count:]
            if "INSERT INTO TASKS" in " ".join(call[0].upper().split())
        ]
        assert len(successful_atomic_calls) == 2
        for call, title in zip(
            successful_atomic_calls,
            ("Atomic first", "Atomic second"),
            strict=True,
        ):
            assert _is_bound_atomic_insert(*call)
            values = _all_bound_parameter_values(call[0], call[1])
            assert course_id in values and title in values
        assert [find_task(database, task_id) for task_id in (4, 5)] == [
            Task(4, course_id, "Atomic first", 1, False),
            Task(5, course_id, "Atomic second", 1, False),
        ], "commit both priority-1 tasks when the atomic pair succeeds"
        assert database.in_transaction is False, (
            "finish the successful atomic transaction with a commit"
        )

        failed_atomic_statement_count = len(database.executed_statements)
        try:
            add_pair_atomically(
                database,
                course_id,
                "Must roll back",
                "Learn SQL",
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("the duplicate title should fail")
        failed_atomic_calls = [
            call
            for call in database.executed_statements[failed_atomic_statement_count:]
            if "INSERT INTO TASKS" in " ".join(call[0].upper().split())
        ]
        assert len(failed_atomic_calls) == 2
        for call, title in zip(
            failed_atomic_calls,
            ("Must roll back", "Learn SQL"),
            strict=True,
        ):
            assert _is_bound_atomic_insert(*call)
            values = _all_bound_parameter_values(call[0], call[1])
            assert course_id in values and title in values
        assert database.in_transaction is False, (
            "finish the failed atomic transaction with a rollback"
        )
        assert all(
            task.title != "Must roll back"
            for task in list_tasks(
                database,
                done=None,
                minimum_priority=1,
                limit=20,
            )
        ), "roll back the first insert when the second insert fails"
        assert [find_task(database, task_id) for task_id in (4, 5)] == [
            Task(4, course_id, "Atomic first", 1, False),
            Task(5, course_id, "Atomic second", 1, False),
        ], "the failed transaction must not roll back the earlier committed pair"

        affinity_statement_count = len(database.executed_statements)
        assert store_affinity_values(database, ["42", "forty-two"]) == [
            ("integer", 42),
            ("text", "forty-two"),
        ]
        assert any(
            _runtime_call_matches(
                call,
                rf"\bINSERT INTO AFFINITY_EXAMPLES\b.*\bVALUES\s*\(\s*{_VALUE_PLACEHOLDER}\s*\)",
                expected_values=("42", "forty-two"),
            )
            for call in database.executed_statements[affinity_statement_count:]
        ), "bind every affinity demonstration value"
        assert database.in_transaction is False, "finish the affinity batch transaction"
        assert any(
            _has_affinity_rowid_order(sql)
            for sql, _parameters in database.executed_statements[
                affinity_statement_count:
            ]
        ), "return affinity rows in insertion order"

    evaluate_autocommit_atomicity()


def evaluate_autocommit_atomicity() -> None:
    connection = sqlite3.connect(":memory:", isolation_level=None)
    with closing(connection) as database:
        configure_connection(database)
        create_schema(database)
        project_id = add_project(database, "Autocommit")

        try:
            add_tasks(
                database,
                project_id,
                [("Batch must roll back", 3), ("", 3)],
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("the invalid autocommit batch should fail")
        assert find_task(database, 1) is None, (
            "explicitly begin the batch transaction so every row rolls back "
            "when isolation_level=None"
        )

        existing_id = add_task(database, project_id, "Existing title", 1)
        try:
            add_pair_atomically(
                database,
                project_id,
                "Pair must roll back",
                "Existing title",
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("the duplicate autocommit pair should fail")
        assert find_task(database, existing_id + 1) is None, (
            "explicitly begin the pair transaction so both writes roll back "
            "when isolation_level=None"
        )
        assert database.in_transaction is False


def evaluate_repository_contracts() -> None:
    memory_repository = InMemoryTaskRepository()
    assert_repository_contract(memory_repository, project_id=1)

    with closing(sqlite3.connect(":memory:")) as database:
        configure_connection(database)
        create_schema(database)
        assert database.in_transaction is False, "finish the schema script transaction"
        project_id = add_project(database, "Repository contract")
        sqlite_repository = SQLiteTaskRepository(database)

        def assert_transaction_complete() -> None:
            assert database.in_transaction is False, (
                "each SQLite repository mutation must finish its transaction"
            )

        assert_repository_contract(
            sqlite_repository,
            project_id,
            mutation_complete=assert_transaction_complete,
        )
        stored_rows = database.execute(
            "SELECT id, done FROM tasks ORDER BY id"
        ).fetchall()
        assert [(int(row["id"]), int(row["done"])) for row in stored_rows] == [
            (1, 1),
            (2, 1),
        ], "the SQLite repository must use the injected connection"


def run_evaluation(label: str, evaluation: Callable[[], None]) -> None:
    try:
        evaluation()
    except NotImplementedError as error:
        raise AssertionError(f"{label}: implement the remaining TODO") from error
    print(f"{label}: OK")


if __name__ == "__main__":
    run_evaluation(
        "connection, schema, and CRUD",
        evaluate_connection_schema_and_crud,
    )
    run_evaluation(
        "queries, transactions, and SQLite behavior",
        evaluate_queries_transactions_and_sqlite,
    )
    run_evaluation("repository contracts", evaluate_repository_contracts)
    print("\nAll checks passed!")
