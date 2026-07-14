"""Task Manager domain model and storage-independent business operations."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, Self, TypedDict


class TaskData(TypedDict):
    id: int
    title: str
    done: bool


class TaskNotFoundError(Exception):
    """Raised when a requested task identifier does not exist."""


@dataclass
class Task:
    """A single to-do item shared by every storage strategy."""

    id: int
    title: str
    done: bool = False

    @staticmethod
    def _validate_values(
        task_id: object,
        title: object,
        done: object,
    ) -> tuple[int, str, bool]:
        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
            raise ValueError("Task id must be a positive integer")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Task title must be a non-empty string")
        if not isinstance(done, bool):
            raise ValueError("Task done must be a boolean")
        return task_id, title.strip(), done

    def __post_init__(self) -> None:
        self.id, self.title, self.done = self._validate_values(
            self.id,
            self.title,
            self.done,
        )

    def mark_done(self) -> None:
        self.done = True

    def to_dict(self) -> TaskData:
        return {"id": self.id, "title": self.title, "done": self.done}

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        try:
            task_id = data["id"]
            title = data["title"]
            done = data["done"]
        except KeyError as error:
            raise ValueError(f"Task data is missing {error.args[0]!r}") from error

        validated_id, validated_title, validated_done = cls._validate_values(
            task_id,
            title,
            done,
        )
        return cls(
            id=validated_id,
            title=validated_title,
            done=validated_done,
        )


class TaskStorage(Protocol):
    """Contract implemented by local and remote persistence strategies."""

    def list_tasks(self) -> list[Task]: ...

    def get(self, task_id: int) -> Task: ...

    def add(self, title: str) -> Task: ...

    def complete(self, task_id: int) -> Task: ...

    def remove(self, task_id: int) -> None: ...


class TaskManager:
    """Apply task operations through an injected persistence strategy."""

    def __init__(self, storage: TaskStorage):
        self.storage = storage

    def add(self, title: str) -> Task:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Task title must be a non-empty string")
        return self.storage.add(title.strip())

    def list_tasks(self, include_done: bool = True) -> list[Task]:
        tasks = self.storage.list_tasks()
        return tasks if include_done else [task for task in tasks if not task.done]

    def get(self, task_id: int) -> Task:
        return self.storage.get(task_id)

    def complete(self, task_id: int) -> Task:
        return self.storage.complete(task_id)

    def remove(self, task_id: int) -> None:
        return self.storage.remove(task_id)
