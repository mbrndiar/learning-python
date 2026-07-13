"""
Capstone Project: Task Manager

Core data model and business logic for a simple command-line task
manager. This module combines concepts from across the course:
classes and dataclasses (module 6), custom exceptions (module 5),
JSON file persistence (module 5), comprehensions (module 4) and type
hints (module 7).
"""

import json
import os
from dataclasses import asdict, dataclass
from typing import List, Optional


class TaskNotFoundError(Exception):
    """Raised when a task id does not exist in the task manager."""


@dataclass
class Task:
    """A single to-do item."""

    id: int
    title: str
    done: bool = False

    def mark_done(self):
        self.done = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(id=data["id"], title=data["title"], done=data["done"])


class TaskManager:
    """Stores tasks in memory and persists them to a JSON file."""

    def __init__(self, storage_path):
        self.storage_path = storage_path
        self._tasks: List[Task] = []
        self._next_id = 1
        self._load()

    def _load(self):
        if not os.path.exists(self.storage_path):
            return
        with open(self.storage_path, "r", encoding="utf-8") as file:
            raw_tasks = json.load(file)
        self._tasks = [Task.from_dict(item) for item in raw_tasks]
        if self._tasks:
            self._next_id = max(task.id for task in self._tasks) + 1

    def save(self):
        with open(self.storage_path, "w", encoding="utf-8") as file:
            json.dump([task.to_dict() for task in self._tasks], file, indent=2)

    def add(self, title):
        task = Task(id=self._next_id, title=title)
        self._tasks.append(task)
        self._next_id += 1
        self.save()
        return task

    def list_tasks(self, include_done=True):
        if include_done:
            return list(self._tasks)
        return [task for task in self._tasks if not task.done]

    def _find(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"No task with id {task_id}")

    def complete(self, task_id):
        task = self._find(task_id)
        task.mark_done()
        self.save()
        return task

    def remove(self, task_id):
        task = self._find(task_id)
        self._tasks.remove(task)
        self.save()

    def get(self, task_id) -> Optional[Task]:
        return self._find(task_id)
