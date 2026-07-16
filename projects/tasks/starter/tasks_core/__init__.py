"""Framework-neutral public boundary for the Task application."""

from .domain import (
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    UNSET,
    CreateTaskInput,
    Task,
    UnsetType,
    UpdateTaskInput,
    normalize_create_input,
    normalize_update_input,
    validate_completed,
    validate_completed_filter,
    validate_task_id,
    validate_title,
)
from .errors import (
    ErrorCode,
    IncompleteImplementationError,
    StorageError,
    TaskError,
    TaskNotFoundError,
    ValidationError,
)
from .service import TaskService

__all__ = [
    "MAX_TITLE_LENGTH",
    "MIN_TITLE_LENGTH",
    "UNSET",
    "CreateTaskInput",
    "ErrorCode",
    "IncompleteImplementationError",
    "StorageError",
    "Task",
    "TaskError",
    "TaskNotFoundError",
    "TaskService",
    "UnsetType",
    "UpdateTaskInput",
    "ValidationError",
    "normalize_create_input",
    "normalize_update_input",
    "validate_completed",
    "validate_completed_filter",
    "validate_task_id",
    "validate_title",
]
