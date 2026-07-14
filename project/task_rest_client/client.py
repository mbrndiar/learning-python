"""Reusable standard-library client for the tasks REST API."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class APIError(Exception):
    """Represent an HTTP or connectivity failure at the client boundary."""


class TaskRestClient:
    """Expose task operations without leaking HTTP details to callers."""

    def __init__(self, base_url, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method, path, data=None):
        body = json.dumps(data).encode("utf-8") if data is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"} if body else {},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content = response.read()
                return json.loads(content) if content else None
        except HTTPError as error:
            try:
                message = json.loads(error.read()).get("error", str(error))
            except (json.JSONDecodeError, UnicodeDecodeError):
                message = str(error)
            raise APIError(message) from error
        except URLError as error:
            raise APIError(f"Could not connect to the API: {error.reason}") from error

    def list_tasks(self):
        return self.request("GET", "/tasks")

    def get(self, task_id):
        return self.request("GET", f"/tasks/{task_id}")

    def add(self, title):
        return self.request("POST", "/tasks", {"title": title})

    def complete(self, task_id):
        return self.request("PATCH", f"/tasks/{task_id}", {"done": True})

    def remove(self, task_id):
        self.request("DELETE", f"/tasks/{task_id}")
