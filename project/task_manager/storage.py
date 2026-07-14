"""Persistence strategies for the Task Manager."""

import json
import os
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TypeVar

from project.task_rest_client.client import APIError, TaskPayload, TaskRestClient

from .task_manager import Task, TaskNotFoundError

T = TypeVar("T")


class FileTaskStorage:
    """Store tasks in a UTF-8 JSON file on the local filesystem."""

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self._tasks: list[Task] = []
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        # Older course versions stored a bare list. Accept it while writing the
        # richer envelope needed to preserve the next ID after deletions.
        if isinstance(data, list):
            raw_tasks: list[object] = list(data)
            stored_next_id: object | None = None
        elif isinstance(data, dict):
            raw_value = data.get("tasks")
            stored_next_id = data.get("next_id")
            if not isinstance(raw_value, list):
                raise ValueError("Task storage tasks must be a list")
            raw_tasks = list(raw_value)
        else:
            raise ValueError("Task storage must contain tasks and a next ID")

        self._tasks = []
        for item in raw_tasks:
            if not isinstance(item, Mapping):
                raise ValueError("Every stored task must be an object")
            self._tasks.append(Task.from_dict(item))
        task_ids = [task.id for task in self._tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Task storage contains duplicate IDs")

        if isinstance(data, list):
            # IDs belong to the storage layer. Continuing after the maximum
            # avoids reusing an identifier when a previously last task vanished.
            self._next_id = max(task_ids, default=0) + 1
        else:
            if (
                isinstance(stored_next_id, bool)
                or not isinstance(stored_next_id, int)
                or stored_next_id < 1
            ):
                raise ValueError("Task storage next_id must be a positive integer")
            self._next_id = stored_next_id

        if self._next_id <= max(task_ids, default=0):
            raise ValueError("Task storage next_id must exceed every task ID")

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = (
            json.dumps(
                {
                    "next_id": self._next_id,
                    "tasks": [task.to_dict() for task in self._tasks],
                },
                indent=2,
            )
            + "\n"
        )
        descriptor, temporary_name = tempfile.mkstemp(
            dir=self.storage_path.parent,
            prefix=f".{self.storage_path.name}.",
            suffix=".tmp",
            text=True,
        )
        temporary_path: Path | None = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            assert temporary_path is not None
            os.replace(temporary_path, self.storage_path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def list_tasks(self) -> list[Task]:
        return list(self._tasks)

    def get(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"No task with id {task_id}")

    def add(self, title: str) -> Task:
        task = Task(self._next_id, title)
        self._tasks.append(task)
        self._next_id += 1
        self._save()
        return task

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.mark_done()
        self._save()
        return task

    def remove(self, task_id: int) -> None:
        self._tasks.remove(self.get(task_id))
        self._save()


class RestTaskStorage:
    """Adapt :class:`TaskRestClient` dictionaries to domain ``Task`` objects."""

    def __init__(self, client: TaskRestClient):
        self.client = client

    @staticmethod
    def _task(data: TaskPayload) -> Task:
        return Task.from_dict(data)

    def _translate_not_found(self, operation: Callable[[], T]) -> T:
        try:
            return operation()
        except APIError as error:
            if error.status_code == 404:
                raise TaskNotFoundError(str(error)) from error
            raise

    def list_tasks(self) -> list[Task]:
        return [self._task(item) for item in self.client.list_tasks()]

    def get(self, task_id: int) -> Task:
        return self._translate_not_found(lambda: self._task(self.client.get(task_id)))

    def add(self, title: str) -> Task:
        # The server creates the ID; the adapter only converts its response.
        return self._task(self.client.add(title))

    def complete(self, task_id: int) -> Task:
        return self._translate_not_found(
            lambda: self._task(self.client.complete(task_id))
        )

    def remove(self, task_id: int) -> None:
        return self._translate_not_found(lambda: self.client.remove(task_id))
