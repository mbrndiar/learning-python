"""Command-line client for the notes REST API."""

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class APIError(Exception):
    pass


class NotesClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def request(self, method, path, data=None):
        body = json.dumps(data).encode("utf-8") if data is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"} if body else {},
        )
        try:
            with urlopen(request, timeout=5) as response:
                content = response.read()
                return json.loads(content) if content else None
        except HTTPError as error:
            try:
                message = json.loads(error.read()).get("error", str(error))
            except (json.JSONDecodeError, UnicodeDecodeError):
                message = str(error)
            raise APIError(message)
        except URLError as error:
            raise APIError(f"Could not connect to the API: {error.reason}")

    def list(self):
        return self.request("GET", "/notes")

    def get(self, note_id):
        return self.request("GET", f"/notes/{note_id}")

    def add(self, title, body=""):
        return self.request("POST", "/notes", {"title": title, "body": body})

    def update(self, note_id, title, body=""):
        return self.request(
            "PUT", f"/notes/{note_id}", {"title": title, "body": body}
        )

    def delete(self, note_id):
        self.request("DELETE", f"/notes/{note_id}")


def build_parser():
    parser = argparse.ArgumentParser(description="Manage notes through the REST API")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="List all notes")

    get_parser = commands.add_parser("get", help="Show one note")
    get_parser.add_argument("note_id", type=int)

    add_parser = commands.add_parser("add", help="Create a note")
    add_parser.add_argument("title")
    add_parser.add_argument("--body", default="")

    update_parser = commands.add_parser("update", help="Replace a note")
    update_parser.add_argument("note_id", type=int)
    update_parser.add_argument("title")
    update_parser.add_argument("--body", default="")

    delete_parser = commands.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("note_id", type=int)

    export_parser = commands.add_parser("export", help="Save notes to a JSON file")
    export_parser.add_argument("file", type=Path)

    import_parser = commands.add_parser("import", help="Create notes from a JSON file")
    import_parser.add_argument("file", type=Path)
    return parser


def format_note(note):
    result = f"#{note['id']} {note['title']}"
    return f"{result}\n  {note['body']}" if note["body"] else result


def read_notes(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Import file must contain a JSON list")
    for note in data:
        if not isinstance(note, dict) or not isinstance(note.get("title"), str):
            raise ValueError("Every imported note must have a string title")
        if not isinstance(note.get("body", ""), str):
            raise ValueError("Every imported note body must be a string")
    return data


def main(argv=None):
    args = build_parser().parse_args(argv)
    client = NotesClient(args.api_url)
    try:
        if args.command == "list":
            notes = client.list()
            print("\n".join(format_note(note) for note in notes) or "No notes.")
        elif args.command == "get":
            print(format_note(client.get(args.note_id)))
        elif args.command == "add":
            print(format_note(client.add(args.title, args.body)))
        elif args.command == "update":
            print(format_note(client.update(args.note_id, args.title, args.body)))
        elif args.command == "delete":
            client.delete(args.note_id)
            print(f"Deleted note #{args.note_id}")
        elif args.command == "export":
            args.file.write_text(
                json.dumps(client.list(), indent=2) + "\n", encoding="utf-8"
            )
            print(f"Exported notes to {args.file}")
        elif args.command == "import":
            notes = read_notes(args.file)
            for note in notes:
                client.add(note["title"], note.get("body", ""))
            print(f"Imported {len(notes)} note(s)")
    except (APIError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
