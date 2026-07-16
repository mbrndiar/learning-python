"""Milestone-two repository contract placeholder."""

from pathlib import Path
from typing import NoReturn, Protocol

import pytest
from tasks_core.repositories import TaskRepository


class RepositoryFactory(Protocol):
    def __call__(self, path: Path) -> TaskRepository: ...


def run_repository_contract(
    repository_factory: RepositoryFactory,
    work_directory: Path,
) -> NoReturn:
    """Reserve the shared persistence contract without claiming behavior."""

    del repository_factory, work_directory
    pytest.skip("repository behavior is intentionally deferred to milestone 2")


__all__ = ["RepositoryFactory", "run_repository_contract"]
