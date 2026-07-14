"""Persistence strategies for the Task Manager."""

import json
from pathlib import Path

from project.task_rest_client.client import APIError

from .task_manager import Task, TaskNotFoundError


class FileTaskStorage:
    """Store tasks in a UTF-8 JSON file on the local filesystem."""

    def __init__(self, storage_path):
        self.storage_path = Path(storage_path)
        self._tasks = []
        self._next_id = 1
        self._load()

    def _load(self):
        if not self.storage_path.exists():
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        # Older course versions stored a bare list. Accept it while writing the
        # richer envelope needed to preserve the next ID after deletions.
        if isinstance(data, list):
            raw_tasks = data
        elif isinstance(data, dict) and isinstance(data.get("tasks"), list):
            raw_tasks = data["tasks"]
            self._next_id = data.get("next_id", 1)
        else:
            raise ValueError("Task storage must contain tasks and a next ID")
        self._tasks = [Task.from_dict(item) for item in raw_tasks]
        if self._tasks and isinstance(data, list):
            # IDs belong to the storage layer. Continuing after the maximum
            # avoids reusing an identifier when a previously last task vanished.
            self._next_id = max(task.id for task in self._tasks) + 1
        if not isinstance(self._next_id, int) or self._next_id < 1:
            raise ValueError("Task storage next_id must be a positive integer")

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(
                {
                    "next_id": self._next_id,
                    "tasks": [task.to_dict() for task in self._tasks],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def list_tasks(self):
        return list(self._tasks)

    def get(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"No task with id {task_id}")

    def add(self, title):
        task = Task(self._next_id, title)
        self._tasks.append(task)
        self._next_id += 1
        self._save()
        return task

    def complete(self, task_id):
        task = self.get(task_id)
        task.mark_done()
        self._save()
        return task

    def remove(self, task_id):
        self._tasks.remove(self.get(task_id))
        self._save()


class RestTaskStorage:
    """Adapt :class:`TaskRestClient` dictionaries to domain ``Task`` objects."""

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _task(data):
        return Task.from_dict(data)

    def _translate_not_found(self, operation):
        try:
            return operation()
        except APIError as error:
            if str(error) == "Task not found":
                raise TaskNotFoundError(str(error)) from error
            raise

    def list_tasks(self):
        return [self._task(item) for item in self.client.list_tasks()]

    def get(self, task_id):
        return self._translate_not_found(lambda: self._task(self.client.get(task_id)))

    def add(self, title):
        # The server creates the ID; the adapter only converts its response.
        return self._task(self.client.add(title))

    def complete(self, task_id):
        return self._translate_not_found(
            lambda: self._task(self.client.complete(task_id))
        )

    def remove(self, task_id):
        return self._translate_not_found(lambda: self.client.remove(task_id))
