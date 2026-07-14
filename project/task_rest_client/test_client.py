"""Integration tests for the reusable REST client and its CLI."""

import contextlib
import io
import os
import tempfile
import threading
import unittest

from project.task_rest_api.api import create_server
from project.task_rest_client.cli import main
from project.task_rest_client.client import APIError, TaskRestClient


class TestTaskRestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descriptor, cls.database_path = tempfile.mkstemp(suffix=".db")
        os.close(descriptor)
        cls.server = create_server(port=0, database_path=cls.database_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

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
        self.client = TaskRestClient(self.url)

    def test_client_add_list_complete_and_remove(self):
        task = self.client.add("Connected task")
        self.assertEqual(task, {"id": 1, "title": "Connected task", "done": False})
        self.assertTrue(self.client.complete(task["id"])["done"])
        self.assertEqual(len(self.client.list_tasks()), 1)
        self.client.remove(task["id"])
        self.assertEqual(self.client.list_tasks(), [])

    def test_client_reports_missing_task(self):
        with self.assertRaisesRegex(APIError, "Task not found"):
            self.client.get(999)

    def test_client_reports_unavailable_server(self):
        unavailable = TaskRestClient("http://127.0.0.1:1", timeout=0.1)
        with self.assertRaisesRegex(APIError, "Could not connect"):
            unavailable.list_tasks()

    def test_cli_uses_reusable_client(self):
        output = io.StringIO()
        arguments = ["--api-url", self.url, "add", "From CLI"]
        with contextlib.redirect_stdout(output):
            exit_code = main(arguments)
        self.assertEqual(exit_code, 0)
        self.assertIn("#1 From CLI", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
