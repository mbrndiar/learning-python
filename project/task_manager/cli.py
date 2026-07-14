"""Command-line Task Manager with selectable file or REST persistence."""

import argparse
import sys
from pathlib import Path

from project.task_rest_client.client import APIError, TaskRestClient

from .storage import FileTaskStorage, RestTaskStorage
from .task_manager import TaskManager, TaskNotFoundError

DEFAULT_STORAGE_PATH = Path(__file__).with_name("tasks.json")


def build_parser():
    parser = argparse.ArgumentParser(description="A task manager")
    parser.add_argument(
        "--backend",
        choices=("file", "rest"),
        default="file",
        help="Persistence strategy (default: file)",
    )
    parser.add_argument(
        "--storage",
        type=Path,
        default=DEFAULT_STORAGE_PATH,
        help="JSON path used by the file backend",
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="Server URL used by the REST backend",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add", help="Add a new task")
    add_parser.add_argument("title")
    list_parser = commands.add_parser("list", help="List tasks")
    list_parser.add_argument("--pending-only", action="store_true")
    complete_parser = commands.add_parser("complete", help="Mark a task done")
    complete_parser.add_argument("task_id", type=int)
    remove_parser = commands.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("task_id", type=int)
    return parser


def create_manager(args):
    """Build only the strategy selected at the command-line boundary."""

    if args.backend == "rest":
        storage = RestTaskStorage(TaskRestClient(args.api_url))
    else:
        storage = FileTaskStorage(args.storage)
    return TaskManager(storage)


def format_task(task):
    status = "x" if task.done else " "
    return f"[{status}] #{task.id} {task.title}"


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        manager = create_manager(args)
        if args.command == "add":
            task = manager.add(args.title)
            print(f"Added task #{task.id}: {task.title}")
        elif args.command == "list":
            tasks = manager.list_tasks(include_done=not args.pending_only)
            print("\n".join(format_task(task) for task in tasks) or "No tasks yet.")
        elif args.command == "complete":
            task = manager.complete(args.task_id)
            print(f"Completed task #{task.id}: {task.title}")
        elif args.command == "remove":
            manager.remove(args.task_id)
            print(f"Removed task #{args.task_id}")
    except (APIError, OSError, ValueError, TaskNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
