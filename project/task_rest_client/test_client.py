"""Integration tests for the reusable REST client and its CLI."""

import contextlib
import io
import os
import tempfile
import threading
import unittest
from unittest import mock

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
        with self.assertRaisesRegex(APIError, "Task not found") as context:
            self.client.get(999)
        self.assertEqual(context.exception.status_code, 404)

    def test_client_reports_unavailable_server(self):
        unavailable = TaskRestClient("http://127.0.0.1:1", timeout=0.1)
        with self.assertRaisesRegex(APIError, "Could not connect"):
            unavailable.list_tasks()

    def test_client_translates_socket_level_failures(self):
        with mock.patch(
            "project.task_rest_client.client.urlopen",
            side_effect=TimeoutError("timed out"),
        ):
            with self.assertRaisesRegex(APIError, "Could not communicate"):
                self.client.list_tasks()

    def test_client_validates_task_response_shape(self):
        with self.assertRaisesRegex(APIError, "invalid task"):
            TaskRestClient._task({"id": "wrong", "title": "Task", "done": False})
        with self.assertRaisesRegex(APIError, "invalid JSON"):
            TaskRestClient._decode(b"not json")

    def run_cli(self, *arguments):
        output = io.StringIO()
        errors = io.StringIO()
        argv = ["--api-url", self.url, *arguments]
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            exit_code = main(argv)
        return exit_code, output.getvalue(), errors.getvalue()

    def test_cli_uses_reusable_client_for_every_command(self):
        exit_code, output, _ = self.run_cli("list")
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), "No tasks yet.")

        exit_code, output, _ = self.run_cli("add", "From CLI")
        self.assertEqual(exit_code, 0)
        self.assertIn("#1 From CLI", output)

        exit_code, output, _ = self.run_cli("list")
        self.assertEqual(exit_code, 0)
        self.assertIn("[ ] #1 From CLI", output)

        exit_code, output, _ = self.run_cli("complete", "1")
        self.assertEqual(exit_code, 0)
        self.assertIn("[x] #1 From CLI", output)

        exit_code, output, _ = self.run_cli("remove", "1")
        self.assertEqual(exit_code, 0)
        self.assertIn("Removed task #1", output)

        exit_code, _, errors = self.run_cli("complete", "999")
        self.assertEqual(exit_code, 1)
        self.assertIn("Task not found", errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
