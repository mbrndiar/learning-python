# Simple CLI Application

`notes_cli.py` is a client for the neighboring
[notes REST API](../simple_rest_api/README.md). It demonstrates `argparse`,
HTTP requests, JSON files, error handling, exit codes, and integration testing.

## Run it

Start the REST API first. Then, from this directory:

```bash
python notes_cli.py add "Learn Python" --body "Build two connected projects"
python notes_cli.py list
python notes_cli.py get 1
python notes_cli.py update 1 "Learn Python" --body "Finished"
python notes_cli.py delete 1
```

Use `--api-url` when the API does not run at `http://127.0.0.1:8000`.

## Work with files

Export all notes to a UTF-8 JSON file:

```bash
python notes_cli.py export notes.json
```

Import notes from that file:

```bash
python notes_cli.py import notes.json
```

The import file must contain a JSON list. Each item needs a string `title` and
may include a string `body`. IDs in exported files are ignored during import,
because the API assigns new IDs.

## Run the tests

```bash
python test_notes_cli.py
```
