"""Shared persistence contract for SQLite and Markdown repositories.

The sequence is intentionally stateful: it checks CRUD and filtering, verifies
that ``UNSET`` fields leave stored values untouched, reopens storage through new
adapter instances, and deletes records before confirming IDs remain monotonic
and are never reused. Running one sequence against both adapters prevents
backend tests from drifting into different definitions of persistence.
"""

from pathlib import Path
from typing import Protocol

import pytest
from tasks_core import (
    CreateTaskInput,
    Task,
    TaskNotFoundError,
    UpdateTaskInput,
)
from tasks_core.repositories import TaskRepository


class RepositoryFactory(Protocol):
    def __call__(self, path: Path) -> TaskRepository: ...


def run_repository_contract(
    repository_factory: RepositoryFactory,
    storage_path: Path,
) -> None:
    """Exercise identical CRUD, adapter-reopen, and identifier semantics."""

    repository = repository_factory(storage_path)
    assert repository.list() == []

    first = repository.create(CreateTaskInput("Learn SQLite"))
    second = repository.create(CreateTaskInput("Build an API"))
    third = repository.create(CreateTaskInput("Write contracts"))
    assert (first, second, third) == (
        Task(1, "Learn SQLite", False),
        Task(2, "Build an API", False),
        Task(3, "Write contracts", False),
    )
    assert repository.list() == [first, second, third]
    assert repository.list(False) == [first, second, third]
    assert repository.list(True) == []
    assert repository.get(2) == second

    # Each partial update carries UNSET for omitted fields; preserving the
    # other stored field is the repository boundary's patch invariant.
    completed = repository.update(2, UpdateTaskInput(completed=True))
    assert completed == Task(2, "Build an API", True)
    renamed = repository.update(2, UpdateTaskInput(title="Ship the API"))
    assert renamed == Task(2, "Ship the API", True)
    unchanged = repository.update(2, UpdateTaskInput(completed=True))
    assert unchanged == renamed
    assert repository.list(False) == [first, third]
    assert repository.list(True) == [renamed]

    for operation in (
        lambda: repository.get(99),
        lambda: repository.update(99, UpdateTaskInput(completed=True)),
        lambda: repository.delete(99),
    ):
        with pytest.raises(TaskNotFoundError) as error:
            operation()
        assert error.value.task_id == 99

    repository.delete(2)
    with pytest.raises(TaskNotFoundError):
        repository.get(2)

    # A fresh adapter instance distinguishes persisted state from an in-memory
    # cache that happened to satisfy the earlier CRUD assertions.
    reopened = repository_factory(storage_path)
    assert reopened.list() == [first, third]
    fourth = reopened.create(CreateTaskInput("Reopen safely"))
    assert fourth == Task(4, "Reopen safely", False)

    reopened.delete(1)
    reopened.delete(3)
    reopened.delete(4)
    assert reopened.list() == []

    # Deletion must not rewind allocator state: external task references stay
    # unambiguous across empty stores and adapter re-instantiation.
    reopened_again = repository_factory(storage_path)
    assert reopened_again.create(CreateTaskInput("Never reuse IDs")) == Task(
        5,
        "Never reuse IDs",
        False,
    )


__all__ = ["RepositoryFactory", "run_repository_contract"]
