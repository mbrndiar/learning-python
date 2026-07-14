"""Task Manager domain model and storage-independent business operations."""

from dataclasses import asdict, dataclass
from typing import Protocol


class TaskNotFoundError(Exception):
    """Raised when a requested task identifier does not exist."""


@dataclass
class Task:
    """A single to-do item shared by every storage strategy."""

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


class TaskStorage(Protocol):
    """Contract implemented by local and remote persistence strategies."""

    def list_tasks(self): ...

    def get(self, task_id): ...

    def add(self, title): ...

    def complete(self, task_id): ...

    def remove(self, task_id): ...


class TaskManager:
    """Apply task operations through an injected persistence strategy."""

    def __init__(self, storage: TaskStorage):
        self.storage = storage

    def add(self, title):
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Task title must be a non-empty string")
        return self.storage.add(title.strip())

    def list_tasks(self, include_done=True):
        tasks = self.storage.list_tasks()
        return tasks if include_done else [task for task in tasks if not task.done]

    def get(self, task_id):
        return self.storage.get(task_id)

    def complete(self, task_id):
        return self.storage.complete(task_id)

    def remove(self, task_id):
        return self.storage.remove(task_id)
