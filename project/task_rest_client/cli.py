"""Command-line interface for :class:`TaskRestClient`."""

import argparse
import sys

from .client import APIError, TaskRestClient


def build_parser():
    parser = argparse.ArgumentParser(description="Manage tasks through the REST API")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List all tasks")
    add_parser = commands.add_parser("add", help="Create a task")
    add_parser.add_argument("title")
    complete_parser = commands.add_parser("complete", help="Mark a task done")
    complete_parser.add_argument("task_id", type=int)
    remove_parser = commands.add_parser("remove", help="Delete a task")
    remove_parser.add_argument("task_id", type=int)
    return parser


def format_task(task):
    status = "x" if task["done"] else " "
    return f"[{status}] #{task['id']} {task['title']}"


def main(argv=None):
    args = build_parser().parse_args(argv)
    client = TaskRestClient(args.api_url)
    try:
        if args.command == "list":
            tasks = client.list_tasks()
            print("\n".join(format_task(task) for task in tasks) or "No tasks yet.")
        elif args.command == "add":
            print(format_task(client.add(args.title)))
        elif args.command == "complete":
            print(format_task(client.complete(args.task_id)))
        elif args.command == "remove":
            client.remove(args.task_id)
            print(f"Removed task #{args.task_id}")
    except APIError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
