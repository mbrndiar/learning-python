"""Reusable standard-library client for the tasks REST API."""

import json
from typing import TypedDict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TaskPayload(TypedDict):
    id: int
    title: str
    done: bool


class APIError(Exception):
    """Represent an HTTP or connectivity failure at the client boundary."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class TaskRestClient:
    """Expose task operations without leaking HTTP details to callers."""

    def __init__(self, base_url: str, timeout: float = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @staticmethod
    def _decode(content: bytes) -> object | None:
        if not content:
            return None
        try:
            data: object = json.loads(content)
            return data
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise APIError("API returned invalid JSON") from error

    @staticmethod
    def _task(data: object) -> TaskPayload:
        if not isinstance(data, dict):
            raise APIError("API returned an invalid task")
        task_id = data.get("id")
        title = data.get("title")
        done = data.get("done")
        if (
            isinstance(task_id, bool)
            or not isinstance(task_id, int)
            or task_id < 1
            or not isinstance(title, str)
            or not isinstance(done, bool)
        ):
            raise APIError("API returned an invalid task")
        return {"id": task_id, "title": title, "done": done}

    def request(
        self,
        method: str,
        path: str,
        data: dict[str, object] | None = None,
    ) -> object | None:
        body = json.dumps(data).encode("utf-8") if data is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"} if body else {},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return self._decode(response.read())
        except HTTPError as error:
            try:
                data = json.loads(error.read())
                message = (
                    data.get("error", str(error))
                    if isinstance(data, dict)
                    else str(error)
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                message = str(error)
            raise APIError(str(message), status_code=error.code) from error
        except URLError as error:
            raise APIError(f"Could not connect to the API: {error.reason}") from error
        except OSError as error:
            raise APIError(f"Could not communicate with the API: {error}") from error

    def list_tasks(self) -> list[TaskPayload]:
        data = self.request("GET", "/tasks")
        if not isinstance(data, list):
            raise APIError("API returned an invalid task list")
        return [self._task(item) for item in data]

    def get(self, task_id: int) -> TaskPayload:
        return self._task(self.request("GET", f"/tasks/{task_id}"))

    def add(self, title: str) -> TaskPayload:
        return self._task(self.request("POST", "/tasks", {"title": title}))

    def complete(self, task_id: int) -> TaskPayload:
        return self._task(self.request("PATCH", f"/tasks/{task_id}", {"done": True}))

    def remove(self, task_id: int) -> None:
        self.request("DELETE", f"/tasks/{task_id}")
