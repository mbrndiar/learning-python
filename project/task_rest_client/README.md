# 📡 Task REST Client

This paired project consumes the neighboring
[Task REST API](../task_rest_api/README.md) using only Python's standard library.
It deliberately separates reusable HTTP communication from terminal behavior.

## 🗂️ Files and responsibilities

- `client.py` defines `TaskRestClient` and `APIError`. Applications can import
  this module without parsing arguments or printing.
- `cli.py` defines commands, formats tasks, and converts `APIError` into a
  nonzero process result.
- `test_client.py` exercises the reusable client and CLI against a real,
  temporary API.

`TaskRestClient` serializes request dictionaries, applies a finite timeout,
decodes responses, and translates both HTTP and connection failures to
`APIError`. Successful JSON responses are validated before they leave the
client, and HTTP errors retain their status code. Its public operations are
`list_tasks`, `get`, `add`, `complete`, and `remove`.

Task Manager reuses this class through `RestTaskStorage`. The adapter converts
the client's JSON dictionaries into domain `Task` objects; the client remains
independent of Task Manager.

## ▶️ Run

Start the API in one terminal:

```bash
python -m project.task_rest_api.api
```

Use the client from another terminal:

```bash
python -m project.task_rest_client.cli add "Learn REST"
python -m project.task_rest_client.cli list
python -m project.task_rest_client.cli complete 1
python -m project.task_rest_client.cli remove 1
```

Pass `--api-url http://127.0.0.1:9000` before the command when the server uses
another port. A missing task or unavailable server is printed to standard error
and produces exit status `1`.

## ♻️ Reuse as a module

Import `TaskRestClient` from `project.task_rest_client.client`, construct it
with the API base URL, and call its task methods. The server remains the sole
authority for identifiers.

## 🧪 Test

```bash
python -m unittest project.task_rest_client.test_client -v
```

Tests cover all client operations, CLI delegation, missing resources, and a
server connection failure.
