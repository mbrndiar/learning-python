# Simple CLI Application

`notes_cli.py` is a client for the neighboring
[notes REST API](../simple_rest_api/README.md). It demonstrates `argparse`,
HTTP requests, JSON files, error handling, exit codes, and integration testing.

The CLI is intentionally a separate process from the API. `build_parser`
defines the command-line boundary, `NotesClient` owns HTTP communication, and
`main` translates commands into client calls and terminal output. This makes it
possible to replace the terminal interface or HTTP library without changing
the API.

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

The entire file is validated before the first request is sent. This prevents a
malformed later item from causing a partial import. Network failures and HTTP
errors are converted to `APIError`; `main` prints the message to standard error
and returns a nonzero exit status.

## Run the tests

```bash
python test_notes_cli.py
```

These are integration tests: they start the neighboring REST API with a
temporary SQLite database and exercise the CLI against it.

## Alternative: requests

The standard-library `urllib.request` module keeps this example dependency-free
and exposes byte encoding, headers, status errors, and timeouts. In many
applications, the popular [Requests](https://requests.readthedocs.io/) package
provides a simpler synchronous interface: method helpers accept `json=...`,
responses expose `.json()`, and `raise_for_status()` identifies unsuccessful
status codes.

After completing the example, try replacing only `NotesClient.request` with
Requests while preserving its public methods and tests. Retain an explicit
timeout and translate library-specific exceptions into `APIError`, so the rest
of the CLI does not depend on the chosen HTTP package. If an application needs
both synchronous and asynchronous clients, [HTTPX](https://www.python-httpx.org/)
is a common alternative.
