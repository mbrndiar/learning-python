"""Milestone-two persistence tests for interchangeable repositories.

Starter-only cases require clear guided failures rather than accidental partial
implementations. Solution cases first apply one CRUD/reopen/ID contract
to both backends, then probe SQLite transactions and Markdown canonical-format,
replacement, cleanup, and in-process serialization guarantees.
"""

import contextlib
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, local
from typing import Any, cast

import pytest
from contracts.repository import RepositoryFactory, run_repository_contract
from implementation import IMPLEMENTATION
from support import FIXTURES, temporary_project_directory
from tasks_api.bootstrap import ServerSettings, build_repository, build_service
from tasks_core import (
    CreateTaskInput,
    IncompleteImplementationError,
    StorageError,
    Task,
    TaskNotFoundError,
    UpdateTaskInput,
)
from tasks_core.repositories import (
    MarkdownTaskRepository,
    SQLiteTaskRepository,
    TaskRepository,
)

STARTER = IMPLEMENTATION == "starter"
# Parametrized solution tests are intentionally skipped as a unit for starter
# runs; the starter-specific test pinpoints the learner-facing TODO instead.
solution_only = pytest.mark.skipif(STARTER, reason="solution milestone-two behavior")
starter_only = pytest.mark.skipif(not STARTER, reason="starter guidance behavior")


@pytest.fixture(
    params=(
        pytest.param((SQLiteTaskRepository, "tasks.db"), id="sqlite"),
        pytest.param((MarkdownTaskRepository, "tasks.md"), id="markdown"),
    )
)
def repository_case(
    request: pytest.FixtureRequest,
) -> tuple[RepositoryFactory, str]:
    """Pair each adapter with its native storage filename for one contract."""

    return cast(tuple[RepositoryFactory, str], request.param)


@starter_only
def test_starter_repository_adapters_fail_deliberately() -> None:
    with temporary_project_directory() as directory:
        repositories = (
            SQLiteTaskRepository(directory / "tasks.db"),
            MarkdownTaskRepository(directory / "tasks.md"),
        )
        for repository in repositories:
            with pytest.raises(
                IncompleteImplementationError,
                match=r"milestone 2 .* list.*intentionally incomplete",
            ):
                repository.list()


@solution_only
def test_repository_contract_is_shared_by_both_backends(
    repository_case: tuple[RepositoryFactory, str],
) -> None:
    # The parameter ID localizes parity failures to sqlite or markdown while
    # keeping the behavioral sequence exactly identical.
    factory, filename = repository_case
    with temporary_project_directory() as directory:
        run_repository_contract(factory, directory / filename)


@solution_only
def test_service_uses_real_repositories_interchangeably(
    repository_case: tuple[RepositoryFactory, str],
) -> None:
    factory, filename = repository_case
    with temporary_project_directory() as directory:
        from tasks_core import TaskService

        service = TaskService(factory(directory / filename))
        created = service.create_task("  Persist through the service  ")
        assert created == Task(1, "Persist through the service", False)
        assert service.update_task(1, completed=True) == Task(
            1,
            "Persist through the service",
            True,
        )
        assert service.list_tasks(True) == [
            Task(1, "Persist through the service", True)
        ]
        service.delete_task(1)
        with pytest.raises(TaskNotFoundError):
            service.get_task(1)


@solution_only
def test_sqlite_serializes_partial_read_modify_write_updates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.db"
        task = SQLiteTaskRepository(path).create(CreateTaskInput("Original"))
        barrier = Barrier(2)
        thread_state = local()
        original_get = SQLiteTaskRepository._get_with_connection

        def coordinated_get(
            self: SQLiteTaskRepository,
            connection: sqlite3.Connection,
            task_id: int,
            *,
            operation: str,
        ) -> Task:
            current = original_get(
                self,
                connection,
                task_id,
                operation=operation,
            )
            # The old implementation reached this read outside a transaction.
            # Synchronizing that window makes its lost update deterministic,
            # while the fixed BEGIN IMMEDIATE path never enters the barrier.
            if (
                operation == "update"
                and not connection.in_transaction
                and not getattr(thread_state, "waited", False)
            ):
                thread_state.waited = True
                barrier.wait(timeout=5)
            return current

        monkeypatch.setattr(
            SQLiteTaskRepository,
            "_get_with_connection",
            coordinated_get,
        )
        with ThreadPoolExecutor(max_workers=2) as executor:
            updates = (
                executor.submit(
                    SQLiteTaskRepository(path).update,
                    task.id,
                    UpdateTaskInput(title="Renamed"),
                ),
                executor.submit(
                    SQLiteTaskRepository(path).update,
                    task.id,
                    UpdateTaskInput(completed=True),
                ),
            )
            for update in updates:
                update.result(timeout=10)

        assert SQLiteTaskRepository(path).get(task.id) == Task(
            task.id,
            "Renamed",
            True,
        )


@solution_only
def test_bootstrap_selects_backend_and_builds_a_framework_neutral_service() -> None:
    with temporary_project_directory() as directory:
        sqlite = build_repository("sqlite", directory / "tasks.db")
        markdown = build_repository("markdown", directory / "tasks.md")
        assert isinstance(sqlite, SQLiteTaskRepository)
        assert isinstance(markdown, MarkdownTaskRepository)
        assert isinstance(sqlite, TaskRepository)
        assert isinstance(markdown, TaskRepository)

        service = build_service(
            ServerSettings(
                host="127.0.0.1",
                port=8000,
                backend="markdown",
                data=directory / "service.md",
            )
        )
        assert service.create_task("Built without a framework").id == 1

        with pytest.raises(ValueError, match="unsupported backend"):
            build_repository(cast(Any, "other"), directory / "other.data")


@solution_only
def test_sqlite_schema_is_idempotent_checked_and_autoincrementing() -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.db"
        SQLiteTaskRepository(path)
        SQLiteTaskRepository(path)

        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            row = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'tasks'"
            ).fetchone()
        assert row is not None
        schema = cast(str, row[0]).upper()
        assert "INTEGER PRIMARY KEY AUTOINCREMENT" in schema
        assert "CHECK (COMPLETED IN (0, 1))" in schema


@solution_only
def test_sqlite_failed_mutations_roll_back_without_consuming_an_id() -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.db"
        repository = SQLiteTaskRepository(path)
        assert repository.create(CreateTaskInput("First")).id == 1

        # Triggers fail inside SQLite's mutation boundary, exercising rollback
        # after an operation starts rather than merely rejecting bad input.
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.executescript(
                """
                CREATE TRIGGER reject_failed_insert
                BEFORE INSERT ON tasks
                WHEN NEW.title = 'Fail insert'
                BEGIN
                    SELECT RAISE(ABORT, 'forced insert failure');
                END;

                CREATE TRIGGER reject_failed_update
                BEFORE UPDATE ON tasks
                WHEN NEW.title = 'Fail update'
                BEGIN
                    SELECT RAISE(ABORT, 'forced update failure');
                END;
                """
            )

        with pytest.raises(StorageError, match="forced insert failure"):
            repository.create(CreateTaskInput("Fail insert"))
        assert repository.list() == [Task(1, "First", False)]

        with pytest.raises(StorageError, match="forced update failure"):
            repository.update(1, UpdateTaskInput(title="Fail update"))
        assert repository.get(1) == Task(1, "First", False)

        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("DROP TRIGGER reject_failed_insert")
        assert repository.create(CreateTaskInput("Second")).id == 2


@solution_only
def test_sqlite_translates_path_and_schema_failures() -> None:
    with temporary_project_directory() as directory:
        with pytest.raises(StorageError) as path_error:
            SQLiteTaskRepository(directory / "missing" / "tasks.db")
        assert path_error.value.operation == "initialize"

        path = directory / "wrong-schema.db"
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("CREATE TABLE tasks (unexpected TEXT)")
        repository = SQLiteTaskRepository(path)
        with pytest.raises(StorageError) as schema_error:
            repository.list()
        assert schema_error.value.operation == "list"


@solution_only
def test_markdown_uses_the_exact_versioned_deterministic_format() -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.md"
        repository = MarkdownTaskRepository(path)
        assert repository.list() == []
        assert path.read_text(encoding="utf-8") == (
            "<!-- rest-task-api:v1 next-id=1 -->\n# Tasks\n"
        )

        repository.create(CreateTaskInput("Learn SQLite"))
        repository.create(CreateTaskInput("Build an API"))
        repository.update(2, UpdateTaskInput(completed=True))
        expected = (
            "<!-- rest-task-api:v1 next-id=3 -->\n"
            "# Tasks\n"
            "\n"
            "- [ ] 1: Learn SQLite\n"
            "- [x] 2: Build an API\n"
        )
        assert path.read_text(encoding="utf-8") == expected

        reopened = MarkdownTaskRepository(path)
        assert reopened.list() == [
            Task(1, "Learn SQLite", False),
            Task(2, "Build an API", True),
        ]
        assert path.read_text(encoding="utf-8") == expected


@solution_only
@pytest.mark.parametrize(
    "document",
    (
        "",
        "<!-- rest-task-api:v2 next-id=1 -->\n# Tasks\n",
        "<!-- rest-task-api:v1 next-id=nope -->\n# Tasks\n",
        "<!-- rest-task-api:v1 next-id=2 -->\n# Wrong\n",
        "<!-- rest-task-api:v1 next-id=2 -->\n# Tasks\n- [ ] 1: No blank\n",
        (
            "<!-- rest-task-api:v1 next-id=2 -->\n# Tasks\n\n"
            "- [ ] 1: First\n- [x] 1: Duplicate\n"
        ),
        (
            "<!-- rest-task-api:v1 next-id=4 -->\n# Tasks\n\n"
            "- [ ] 2: Second\n- [ ] 1: First\n"
        ),
        ("<!-- rest-task-api:v1 next-id=2 -->\n# Tasks\n\n- [X] 1: Wrong marker\n"),
        ("<!-- rest-task-api:v1 next-id=2 -->\n# Tasks\n\n- [ ] 1:  Padded title\n"),
        ("<!-- rest-task-api:v1 next-id=1 -->\n# Tasks\n\n- [ ] 1: Next ID is stale\n"),
        "<!-- rest-task-api:v1 next-id=1 -->\n# Tasks",
        "<!-- rest-task-api:v1 next-id=1 -->\r\n# Tasks\r\n",
    ),
)
def test_markdown_rejects_malformed_or_noncanonical_documents(
    document: str,
) -> None:
    # These documents are often parseable Markdown but violate the repository's
    # canonical on-disk grammar; accepting them would make rewrites ambiguous.
    with temporary_project_directory() as directory:
        path = directory / "tasks.md"
        path.write_text(document, encoding="utf-8", newline="")
        with pytest.raises(StorageError):
            MarkdownTaskRepository(path).list()


@solution_only
def test_checked_in_malformed_markdown_fixture_is_rejected() -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.md"
        path.write_bytes((FIXTURES / "markdown" / "malformed-metadata.md").read_bytes())
        with pytest.raises(StorageError):
            MarkdownTaskRepository(path).list()


@solution_only
def test_markdown_rejects_invalid_utf8() -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.md"
        path.write_bytes(b"\xff\xfe")
        with pytest.raises(StorageError) as error:
            MarkdownTaskRepository(path).list()
        assert error.value.operation == "list"


@solution_only
def test_markdown_failed_replace_preserves_target_and_cleans_temporary_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.md"
        repository = MarkdownTaskRepository(path)
        repository.create(CreateTaskInput("Existing"))
        original = path.read_bytes()
        original_replace = Path.replace

        # Fail only the final atomic replace so setup writes still use the real
        # filesystem and the test observes the exact commit failure window.
        def fail_replace(source: Path, target: Path) -> Path:
            if source.parent == directory and target == path:
                raise OSError("forced replace failure")
            return original_replace(source, target)

        monkeypatch.setattr(Path, "replace", fail_replace)
        with pytest.raises(StorageError, match="forced replace failure"):
            repository.create(CreateTaskInput("Not committed"))

        assert path.read_bytes() == original
        assert list(directory.glob(".tasks.md.*.tmp")) == []


@solution_only
def test_markdown_translates_storage_path_failures_and_cleans_up() -> None:
    with temporary_project_directory() as directory:
        path = directory / "missing" / "tasks.md"
        repository = MarkdownTaskRepository(path)
        with pytest.raises(StorageError) as error:
            repository.list()
        assert error.value.operation == "list"
        assert list(directory.rglob("*.tmp")) == []


@solution_only
def test_markdown_serializes_concurrent_writes_within_one_process() -> None:
    with temporary_project_directory() as directory:
        path = directory / "tasks.md"

        def create_task(number: int) -> Task:
            repository = MarkdownTaskRepository(path)
            return repository.create(CreateTaskInput(f"Task {number:02d}"))

        # Separate repository instances model callers that share a path but not
        # object state; the path-scoped lock must still prevent lost updates.
        with ThreadPoolExecutor(max_workers=8) as executor:
            created = list(executor.map(create_task, range(24)))

        assert sorted(task.id for task in created) == list(range(1, 25))
        reopened = MarkdownTaskRepository(path)
        assert [task.id for task in reopened.list()] == list(range(1, 25))
        assert path.read_bytes().endswith(b"\n")
        assert list(directory.glob(".tasks.md.*.tmp")) == []
