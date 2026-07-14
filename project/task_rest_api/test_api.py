"""Integration tests for the tasks REST API and SQLite store."""

import http.client
import json
import os
import tempfile
import threading
import unittest

from project.task_rest_api.api import TaskStore, create_server


class TestTasksAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descriptor, cls.database_path = tempfile.mkstemp(suffix=".db")
        os.close(descriptor)
        cls.server = create_server(port=0, database_path=cls.database_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        os.remove(cls.database_path)

    def setUp(self):
        with self.server.store._connect() as connection:
            connection.execute("DELETE FROM tasks")
            connection.execute("DELETE FROM sqlite_sequence WHERE name = 'tasks'")

    def raw_request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=2
        )
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        content = response.read()
        connection.close()
        return response.status, json.loads(content) if content else None

    def request(self, method, path, data=None):
        body = json.dumps(data) if data is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        return self.raw_request(method, path, body=body, headers=headers)

    def test_create_list_complete_and_delete_task(self):
        status, created = self.request("POST", "/tasks", {"title": "Learn HTTP"})
        self.assertEqual((status, created["done"]), (201, False))

        status, tasks = self.request("GET", "/tasks")
        self.assertEqual((status, tasks), (200, [created]))

        status, completed = self.request("PATCH", "/tasks/1", {"done": True})
        self.assertEqual((status, completed["done"]), (200, True))

        status, content = self.request("DELETE", "/tasks/1")
        self.assertEqual((status, content), (204, None))

    def test_rejects_invalid_title_and_completion(self):
        status, content = self.request("POST", "/tasks", {"title": "  "})
        self.assertEqual(status, 400)
        self.assertIn("title", content["error"])

        self.request("POST", "/tasks", {"title": "Valid"})
        status, content = self.request("PATCH", "/tasks/1", {"done": False})
        self.assertEqual(status, 400)
        self.assertIn("Completion", content["error"])

    def test_returns_not_found(self):
        status, content = self.request("GET", "/tasks/999")
        self.assertEqual((status, content), (404, {"error": "Task not found"}))
        status, content = self.request("PATCH", "/tasks/999", {"done": True})
        self.assertEqual((status, content), (404, {"error": "Task not found"}))
        status, content = self.request("DELETE", "/tasks/999")
        self.assertEqual((status, content), (404, {"error": "Task not found"}))

    def test_rejects_unknown_routes_and_invalid_json_bodies(self):
        for method in ("GET", "POST", "PATCH", "DELETE"):
            with self.subTest(method=method):
                status, content = self.request(method, "/unknown")
                self.assertEqual(status, 404)
                self.assertEqual(content, {"error": "Route not found"})

        status, content = self.raw_request(
            "POST",
            "/tasks",
            body="not json",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertIn("valid JSON", content["error"])

        status, content = self.request("POST", "/tasks", ["not", "an", "object"])
        self.assertEqual(status, 400)
        self.assertIn("JSON object", content["error"])

        status, content = self.raw_request("POST", "/tasks")
        self.assertEqual(status, 400)
        self.assertIn("contain JSON", content["error"])

    def test_tasks_persist_in_sqlite(self):
        self.request("POST", "/tasks", {"title": "Persist me"})
        reopened_store = TaskStore(self.database_path)
        self.assertEqual(reopened_store.list()[0]["title"], "Persist me")


if __name__ == "__main__":
    unittest.main(verbosity=2)
