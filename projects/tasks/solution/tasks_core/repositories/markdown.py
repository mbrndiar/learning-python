"""Versioned Markdown implementation of the Task repository contract."""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from uuid import uuid4

from ..domain import CreateTaskInput, Task, UnsetType, UpdateTaskInput, validate_title
from ..errors import StorageError, TaskNotFoundError, ValidationError

_METADATA = re.compile(
    r"<!-- rest-task-api:v(?P<version>[1-9][0-9]*) "
    r"next-id=(?P<next_id>[1-9][0-9]*) -->"
)
_CHECKLIST_ROW = re.compile(
    r"- \[(?P<completed>[ x])\] "
    r"(?P<task_id>[1-9][0-9]*): (?P<title>.+)"
)
_FORMAT_VERSION = 1
_HEADING = "# Tasks"

_locks_guard = RLock()
_path_locks: dict[Path, RLock] = {}


def _lock_for(path: Path) -> RLock:
    key = path.absolute()
    with _locks_guard:
        lock = _path_locks.get(key)
        if lock is None:
            lock = RLock()
            _path_locks[key] = lock
        return lock


@dataclass(frozen=True, slots=True)
class _Document:
    next_id: int
    tasks: list[Task]


class MarkdownTaskRepository:
    """One-file repository synchronized only between threads in this process."""

    def __init__(self, document_path: str | Path) -> None:
        self.document_path = Path(document_path)
        self._lock = _lock_for(self.document_path)

    @staticmethod
    def _storage_error(operation: str, message: str) -> StorageError:
        return StorageError(
            f"Markdown {operation} failed: {message}",
            operation=operation,
        )

    def _read_text(self, operation: str) -> str:
        try:
            with self.document_path.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as stream:
                return stream.read()
        except FileNotFoundError:
            document = _Document(next_id=1, tasks=[])
            self._save(document, operation)
            return self._render(document)
        except (OSError, UnicodeError) as error:
            raise self._storage_error(operation, str(error)) from error

    def _load(self, operation: str) -> _Document:
        text = self._read_text(operation)
        if not text.endswith("\n") or "\r" in text:
            raise self._storage_error(
                operation,
                "document must use LF lines and end with one newline",
            )

        lines = text[:-1].split("\n")
        if len(lines) < 2:
            raise self._storage_error(operation, "document is incomplete")

        metadata = _METADATA.fullmatch(lines[0])
        if metadata is None:
            raise self._storage_error(operation, "metadata comment is malformed")

        version = int(metadata.group("version"))
        if version != _FORMAT_VERSION:
            raise self._storage_error(
                operation,
                f"unsupported format version {version}",
            )
        next_id = int(metadata.group("next_id"))

        if lines[1] != _HEADING:
            raise self._storage_error(operation, "Tasks heading is malformed")

        if len(lines) == 2:
            row_lines: list[str] = []
        elif lines[2] != "":
            raise self._storage_error(
                operation,
                "checklist rows must follow one blank line",
            )
        else:
            row_lines = lines[3:]
            if not row_lines:
                raise self._storage_error(
                    operation,
                    "empty documents must not contain a trailing blank line",
                )

        tasks: list[Task] = []
        seen_ids: set[int] = set()
        previous_id = 0
        for line_number, line in enumerate(row_lines, start=4):
            match = _CHECKLIST_ROW.fullmatch(line)
            if match is None:
                raise self._storage_error(
                    operation,
                    f"malformed checklist row at line {line_number}",
                )

            task_id = int(match.group("task_id"))
            if task_id in seen_ids:
                raise self._storage_error(
                    operation,
                    f"duplicate task ID {task_id}",
                )
            if task_id < previous_id:
                raise self._storage_error(
                    operation,
                    f"task IDs are out of order at line {line_number}",
                )

            raw_title = match.group("title")
            try:
                title = validate_title(raw_title)
            except ValidationError as error:
                raise self._storage_error(
                    operation,
                    f"invalid title at line {line_number}: {error}",
                ) from error
            if title != raw_title:
                raise self._storage_error(
                    operation,
                    f"title at line {line_number} is not stored literally",
                )

            tasks.append(
                Task(
                    task_id,
                    title,
                    match.group("completed") == "x",
                )
            )
            seen_ids.add(task_id)
            previous_id = task_id

        if tasks and next_id <= tasks[-1].id:
            raise self._storage_error(
                operation,
                "next-id must be greater than every stored task ID",
            )
        return _Document(next_id=next_id, tasks=tasks)

    @staticmethod
    def _render(document: _Document) -> str:
        lines = [
            f"<!-- rest-task-api:v{_FORMAT_VERSION} next-id={document.next_id} -->",
            _HEADING,
        ]
        if document.tasks:
            lines.append("")
            lines.extend(
                f"- [{'x' if task.completed else ' '}] {task.id}: {task.title}"
                for task in document.tasks
            )
        return "\n".join(lines) + "\n"

    def _save(self, document: _Document, operation: str) -> None:
        temporary_path = self.document_path.with_name(
            f".{self.document_path.name}.{uuid4().hex}.tmp"
        )
        try:
            with temporary_path.open(
                "x",
                encoding="utf-8",
                newline="",
            ) as stream:
                stream.write(self._render(document))
                stream.flush()
                os.fsync(stream.fileno())
            temporary_path.replace(self.document_path)
        except (OSError, UnicodeError) as error:
            raise self._storage_error(operation, str(error)) from error
        finally:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

    def create(self, task: CreateTaskInput) -> Task:
        operation = "create"
        with self._lock:
            document = self._load(operation)
            created = Task(document.next_id, task.title, False)
            self._save(
                _Document(
                    next_id=document.next_id + 1,
                    tasks=[*document.tasks, created],
                ),
                operation,
            )
            return created

    def list(self, completed: bool | None = None) -> list[Task]:
        with self._lock:
            tasks = self._load("list").tasks
            if completed is None:
                return list(tasks)
            return [task for task in tasks if task.completed is completed]

    def get(self, task_id: int) -> Task:
        with self._lock:
            for task in self._load("get").tasks:
                if task.id == task_id:
                    return task
        raise TaskNotFoundError(task_id)

    def update(
        self,
        task_id: int,
        update: UpdateTaskInput,
    ) -> Task:
        operation = "update"
        with self._lock:
            document = self._load(operation)
            tasks = list(document.tasks)
            for index, current in enumerate(tasks):
                if current.id != task_id:
                    continue
                updated = Task(
                    task_id,
                    current.title
                    if isinstance(update.title, UnsetType)
                    else update.title,
                    current.completed
                    if isinstance(update.completed, UnsetType)
                    else update.completed,
                )
                tasks[index] = updated
                self._save(
                    _Document(next_id=document.next_id, tasks=tasks),
                    operation,
                )
                return updated
        raise TaskNotFoundError(task_id)

    def delete(self, task_id: int) -> None:
        operation = "delete"
        with self._lock:
            document = self._load(operation)
            tasks = [task for task in document.tasks if task.id != task_id]
            if len(tasks) == len(document.tasks):
                raise TaskNotFoundError(task_id)
            self._save(
                _Document(next_id=document.next_id, tasks=tasks),
                operation,
            )


__all__ = ["MarkdownTaskRepository"]
