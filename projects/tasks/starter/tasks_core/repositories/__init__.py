"""Persistence adapters for the shared Task repository contract."""

from .markdown import MarkdownTaskRepository
from .protocol import TaskRepository
from .sqlite import SQLiteTaskRepository

__all__ = ["MarkdownTaskRepository", "SQLiteTaskRepository", "TaskRepository"]
