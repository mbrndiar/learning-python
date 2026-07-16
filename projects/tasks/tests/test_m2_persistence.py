"""Milestone two scaffold checks for both persistence adapters."""

import pytest
from support import temporary_project_directory
from tasks_core import IncompleteImplementationError
from tasks_core.repositories import MarkdownTaskRepository, SQLiteTaskRepository


def test_repository_adapters_fail_deliberately_before_contract_implementation() -> None:
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
