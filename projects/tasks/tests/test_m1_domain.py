"""Milestone-one contract for domain values and the framework-neutral service.

Starter-only checks preserve explicit teaching failures at the intended TODOs;
solution-only checks then define validation, immutable values, partial-update
semantics, and error propagation.  Parser and transport-model checks run for
both trees because their public scaffolding must be usable from the outset.
"""

from dataclasses import FrozenInstanceError

import pytest
from implementation import IMPLEMENTATION
from tasks_cli.application import (
    AddCommand,
    ListCommand,
    UpdateCommand,
    parse_request,
)
from tasks_cli.transport import (
    TaskTransport,
    TransportConnectionError,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
)
from tasks_core import (
    MAX_TITLE_LENGTH,
    UNSET,
    CreateTaskInput,
    IncompleteImplementationError,
    StorageError,
    Task,
    TaskNotFoundError,
    TaskService,
    UnsetType,
    UpdateTaskInput,
    ValidationError,
    normalize_create_input,
    normalize_update_input,
    validate_completed,
    validate_completed_filter,
    validate_task_id,
    validate_title,
)
from tasks_core.repositories import TaskRepository

STARTER = IMPLEMENTATION == "starter"
# A single suite documents both phases: starter markers verify deliberate,
# localized incompleteness while solution markers avoid demanding finished work.
solution_only = pytest.mark.skipif(STARTER, reason="solution milestone-one behavior")
starter_only = pytest.mark.skipif(not STARTER, reason="starter guidance behavior")


class _FakeRepository:
    """Record service delegation and inject storage failures without I/O."""

    def __init__(self) -> None:
        self.tasks = [
            Task(1, "Learn REST", False),
            Task(2, "Write tests", True),
        ]
        self.calls: list[tuple[str, object]] = []
        self.failure: StorageError | None = None

    def _fail_if_configured(self) -> None:
        if self.failure is not None:
            raise self.failure

    def create(self, task: CreateTaskInput) -> Task:
        self.calls.append(("create", task))
        self._fail_if_configured()
        created = Task(len(self.tasks) + 1, task.title, False)
        self.tasks.append(created)
        return created

    def list(self, completed: bool | None = None) -> list[Task]:
        self.calls.append(("list", completed))
        self._fail_if_configured()
        if completed is None:
            return list(self.tasks)
        return [task for task in self.tasks if task.completed is completed]

    def get(self, task_id: int) -> Task:
        self.calls.append(("get", task_id))
        self._fail_if_configured()
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)

    def update(self, task_id: int, update: UpdateTaskInput) -> Task:
        self.calls.append(("update", (task_id, update)))
        self._fail_if_configured()
        current = self.get(task_id)
        title = current.title if isinstance(update.title, UnsetType) else update.title
        completed = (
            current.completed
            if isinstance(update.completed, UnsetType)
            else update.completed
        )
        updated = Task(task_id, title, completed)
        self.tasks[current.id - 1] = updated
        return updated

    def delete(self, task_id: int) -> None:
        self.calls.append(("delete", task_id))
        self._fail_if_configured()
        task = self.get(task_id)
        self.tasks.remove(task)


class _FakeTransport:
    def __init__(self) -> None:
        self.request: TransportRequest | None = None
        self.closed = False

    def send(self, request: TransportRequest) -> TransportResponse:
        self.request = request
        return TransportResponse(200, {"Content-Type": "application/json"}, b"[]")

    def close(self) -> None:
        self.closed = True


def _assert_validation_error(
    error: pytest.ExceptionInfo[ValidationError],
    *,
    field: str,
) -> None:
    assert error.value.code == "validation_error"
    assert error.value.field == field
    assert error.value.details == {"field": field}
    assert str(error.value) == error.value.message


def test_shared_protocols_and_parser_models_are_available() -> None:
    repository = _FakeRepository()
    transport = _FakeTransport()
    assert isinstance(repository, TaskRepository)
    assert isinstance(transport, TaskTransport)

    add = parse_request(["add", "Learn REST"])
    assert add.command == AddCommand("Learn REST")
    assert add.settings.timeout == 5.0

    filtered = parse_request(["list", "--completed", "false"])
    assert filtered.command == ListCommand(False)

    update = parse_request(
        ["update", "2", "--title", "Ship it", "--completed", "false"]
    )
    assert update.command == UpdateCommand(2, "Ship it", False)


def test_update_parser_rejects_an_empty_patch() -> None:
    with pytest.raises(SystemExit) as error:
        parse_request(["update", "1"])
    assert error.value.code == 2


def test_transport_values_and_errors_are_library_neutral() -> None:
    request = TransportRequest(
        "POST",
        "/tasks",
        query={"source": "cli"},
        json_body={"title": "Learn REST"},
    )
    response = _FakeTransport().send(request)

    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json"
    assert TransportTimeoutError("timed out").message == "timed out"
    assert isinstance(TransportTimeoutError("timed out"), TransportConnectionError)


@starter_only
def test_starter_keeps_guided_milestone_failures_explicit() -> None:
    task = Task(id=1, title="Learn REST", completed=False)
    assert task == Task(1, "Learn REST", False)

    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 1 title validation.*intentionally incomplete",
    ):
        validate_title("Learn REST")

    # The repository must remain untouched when execution stops at a guided
    # service TODO; otherwise starter failures could hide unintended mutation.
    repository = _FakeRepository()
    service = TaskService(repository)
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 1 task creation.*intentionally incomplete",
    ):
        service.create_task("Learn REST")
    assert repository.calls == []


@solution_only
def test_task_is_validated_normalized_immutable_and_slotted() -> None:
    task = Task(id=1, title="  Learn REST  ", completed=False)
    assert task == Task(1, "Learn REST", False)
    assert not hasattr(task, "__dict__")

    with pytest.raises(FrozenInstanceError):
        setattr(task, "title", "changed")


@solution_only
@pytest.mark.parametrize("value", [0, -1, True, 1.5, "1", None])
def test_task_id_requires_a_strict_positive_integer(value: object) -> None:
    with pytest.raises(ValidationError) as error:
        validate_task_id(value)
    _assert_validation_error(error, field="id")


@solution_only
def test_title_accepts_trimmed_unicode_and_length_boundaries() -> None:
    # The limit applies after trimming and counts Unicode code points rather than
    # encoded bytes; one user-perceived character may contain multiple points.
    assert validate_title("  Café  ") == "Café"
    assert validate_title("x" * MAX_TITLE_LENGTH) == "x" * MAX_TITLE_LENGTH
    assert normalize_create_input("  Ship it  ") == CreateTaskInput("Ship it")


@solution_only
@pytest.mark.parametrize(
    "value",
    [
        None,
        42,
        "",
        "   ",
        "x" * (MAX_TITLE_LENGTH + 1),
        "first\nsecond",
        "first\x00second",
    ],
)
def test_title_rejects_wrong_shape_length_lines_and_controls(value: object) -> None:
    with pytest.raises(ValidationError) as error:
        validate_title(value)
    _assert_validation_error(error, field="title")


@solution_only
def test_completion_validation_is_strict_and_filter_allows_none() -> None:
    assert validate_completed(True) is True
    assert validate_completed(False) is False
    assert validate_completed_filter(None) is None
    assert validate_completed_filter(False) is False

    for value in (0, 1, "false", None):
        with pytest.raises(ValidationError) as error:
            validate_completed(value)
        _assert_validation_error(error, field="completed")


@solution_only
def test_update_input_uses_a_sentinel_and_preserves_explicit_false() -> None:
    # UNSET distinguishes omission from ``False``.  Collapsing both to a falsey
    # value would make a legitimate request unable to reopen a completed task.
    title_only = normalize_update_input(title="  Clarify API  ")
    assert title_only == UpdateTaskInput(title="Clarify API")
    assert title_only.completed is UNSET

    incomplete = normalize_update_input(completed=False)
    assert incomplete.title is UNSET
    assert incomplete.completed is False

    with pytest.raises(ValidationError) as error:
        normalize_update_input()
    _assert_validation_error(error, field="update")

    with pytest.raises(ValidationError) as error:
        normalize_update_input(completed=None)
    _assert_validation_error(error, field="completed")


@solution_only
def test_narrow_errors_expose_stable_fields() -> None:
    missing = TaskNotFoundError(9)
    assert missing.code == "not_found"
    assert missing.task_id == 9
    assert missing.message == "task 9 was not found"
    assert missing.details == {}

    storage = StorageError("database is unavailable", operation="list")
    assert storage.code == "internal_error"
    assert storage.operation == "list"
    assert storage.details == {"operation": "list"}


@solution_only
def test_service_normalizes_boundaries_and_delegates_repository_values() -> None:
    repository = _FakeRepository()
    service = TaskService(repository)

    assert service.create_task("  Review service  ") == Task(
        3,
        "Review service",
        False,
    )
    assert service.list_tasks(False) == [
        Task(1, "Learn REST", False),
        Task(3, "Review service", False),
    ]
    assert service.get_task(2) == Task(2, "Write tests", True)
    assert service.update_task(2, completed=False) == Task(
        2,
        "Write tests",
        False,
    )
    service.delete_task(1)

    assert repository.calls[0] == (
        "create",
        CreateTaskInput("Review service"),
    )
    assert repository.calls[1] == ("list", False)
    operation, payload = repository.calls[3]
    assert operation == "update"
    assert payload == (2, UpdateTaskInput(completed=False))
    assert repository.calls[-2:] == [("delete", 1), ("get", 1)]


@solution_only
def test_service_rejects_invalid_boundaries_before_repository_access() -> None:
    repository = _FakeRepository()
    service = TaskService(repository)

    # Validation belongs at the service boundary, before adapters can persist
    # malformed state or expose backend-specific failure ordering.
    invalid_calls = (
        lambda: service.create_task(" "),
        lambda: service.list_tasks("false"),
        lambda: service.get_task(True),
        lambda: service.update_task(0, completed=False),
        lambda: service.update_task(1),
        lambda: service.delete_task(-1),
    )
    for call in invalid_calls:
        with pytest.raises(ValidationError):
            call()
    assert repository.calls == []


@solution_only
def test_service_preserves_not_found_and_storage_failures() -> None:
    repository = _FakeRepository()
    service = TaskService(repository)

    with pytest.raises(TaskNotFoundError) as missing:
        service.get_task(99)
    assert missing.value.task_id == 99

    failure = StorageError("read failed", operation="list")
    repository.failure = failure
    with pytest.raises(StorageError) as raised:
        service.list_tasks()
    assert raised.value is failure
