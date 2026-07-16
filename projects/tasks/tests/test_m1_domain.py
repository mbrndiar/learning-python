"""Milestone one scaffold checks for domain and application contracts."""

import pytest
from tasks_core import IncompleteImplementationError, Task, TaskService, validate_title
from tasks_core.repositories import TaskRepository


class _FakeRepository:
    def create(self, title: str) -> Task:
        raise AssertionError("service placeholder must not call the repository")

    def list(self, completed: bool | None = None) -> list[Task]:
        raise AssertionError("service placeholder must not call the repository")

    def get(self, task_id: int) -> Task:
        raise AssertionError("service placeholder must not call the repository")

    def update(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        raise AssertionError("service placeholder must not call the repository")

    def delete(self, task_id: int) -> None:
        raise AssertionError("service placeholder must not call the repository")


def test_task_value_and_repository_protocol_import() -> None:
    task = Task(id=1, title="Learn REST", completed=False)
    repository = _FakeRepository()
    assert task == Task(1, "Learn REST", False)
    assert isinstance(repository, TaskRepository)


def test_domain_and_service_fail_at_explicit_milestone_boundary() -> None:
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 1 title validation.*intentionally incomplete",
    ):
        validate_title("Learn REST")

    service = TaskService(_FakeRepository())
    with pytest.raises(
        IncompleteImplementationError,
        match=r"milestone 1 task creation.*intentionally incomplete",
    ):
        service.create_task("Learn REST")
