"""
Capstone Project: Task Manager CLI

A command-line interface built on top of task_manager.py, using
argparse (module 9) to parse subcommands.

Usage examples (from the project's `task_manager/` directory):

    python cli.py add "Buy milk"
    python cli.py list
    python cli.py complete 1
    python cli.py remove 1
"""

import argparse
import os
import sys

from task_manager import TaskManager, TaskNotFoundError

DEFAULT_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "tasks.json")


def build_parser():
    parser = argparse.ArgumentParser(description="A simple task manager")
    parser.add_argument(
        "--storage",
        default=DEFAULT_STORAGE_PATH,
        help="Path to the JSON file used to store tasks",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Title of the task")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--pending-only",
        action="store_true",
        help="Only show tasks that are not done",
    )

    complete_parser = subparsers.add_parser("complete", help="Mark a task done")
    complete_parser.add_argument("task_id", type=int)

    remove_parser = subparsers.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("task_id", type=int)

    return parser


def format_task(task):
    status = "x" if task.done else " "
    return f"[{status}] #{task.id} {task.title}"


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # Argument parsing stays at the boundary; TaskManager contains the logic.
    manager = TaskManager(args.storage)

    try:
        if args.command == "add":
            task = manager.add(args.title)
            print(f"Added task #{task.id}: {task.title}")
        elif args.command == "list":
            tasks = manager.list_tasks(include_done=not args.pending_only)
            if not tasks:
                print("No tasks yet.")
            for task in tasks:
                print(format_task(task))
        elif args.command == "complete":
            task = manager.complete(args.task_id)
            print(f"Completed task #{task.id}: {task.title}")
        elif args.command == "remove":
            manager.remove(args.task_id)
            print(f"Removed task #{args.task_id}")
    except TaskNotFoundError as error:
        # Diagnostics go to stderr, leaving stdout available for normal output.
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
