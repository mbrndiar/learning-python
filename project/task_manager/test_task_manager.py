"""Contract and integration tests for Task Manager storage strategies."""

import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path

from project.task_manager.cli import main as task_manager_main
from project.task_manager.storage import FileTaskStorage, RestTaskStorage
from project.task_manager.task_manager import Task, TaskManager, TaskNotFoundError
from project.task_rest_api.api import create_server
from project.task_rest_client.client import TaskRestClient


class TestTask(unittest.TestCase):
    def test_dictionary_round_trip_and_completion(self):
        task = Task(id=2, title="Ship it")
        task.mark_done()
        self.assertEqual(Task.from_dict(task.to_dict()), task)

    def test_rejects_invalid_dictionary_data(self):
        with self.assertRaisesRegex(ValueError, "positive integer"):
            Task.from_dict({"id": 0, "title": "Invalid", "done": False})
        with self.assertRaisesRegex(ValueError, "boolean"):
            Task.from_dict({"id": 1, "title": "Invalid", "done": 0})
        with self.assertRaisesRegex(ValueError, "non-empty"):
            Task(id=1, title="   ")


class StorageContract:
    """Assertions every storage strategy must satisfy."""

    def make_storage(self):
        raise NotImplementedError

    def setUp(self):
        self.storage = self.make_storage()

    def test_add_list_complete_remove_and_missing(self):
        first = self.storage.add("First")
        second = self.storage.add("Second")
        self.assertEqual((first.id, second.id), (1, 2))
        self.assertEqual(len(self.storage.list_tasks()), 2)
        self.assertTrue(self.storage.complete(first.id).done)
        self.storage.remove(second.id)
        self.assertEqual([task.id for task in self.storage.list_tasks()], [first.id])
        with self.assertRaises(TaskNotFoundError):
            self.storage.get(999)
        with self.assertRaises(TaskNotFoundError):
            self.storage.complete(999)
        with self.assertRaises(TaskNotFoundError):
            self.storage.remove(999)


class TestFileTaskStorage(StorageContract, unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        super().setUp()

    def tearDown(self):
        self.directory.cleanup()

    def make_storage(self):
        return FileTaskStorage(Path(self.directory.name) / "tasks.json")

    def test_persistence_and_id_ownership(self):
        first = self.storage.add("Persisted")
        self.storage.add("Removed")
        self.storage.remove(2)
        reopened = FileTaskStorage(self.storage.storage_path)
        self.assertEqual(reopened.list_tasks(), [first])
        self.assertEqual(reopened.add("Next").id, 3)

    def test_rejects_inconsistent_next_id(self):
        path = Path(self.directory.name) / "invalid.json"
        path.write_text(
            json.dumps(
                {
                    "next_id": 1,
                    "tasks": [{"id": 1, "title": "Existing", "done": False}],
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "exceed every task ID"):
            FileTaskStorage(path)

    def test_atomic_save_leaves_no_temporary_file(self):
        self.storage.add("Persist")
        leftovers = list(Path(self.directory.name).glob("*.tmp"))
        self.assertEqual(leftovers, [])

    def test_rejects_invalid_title_before_writing(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            self.storage.add("   ")
        self.assertFalse(self.storage.storage_path.exists())


class TestRestTaskStorage(StorageContract, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descriptor, cls.database_path = tempfile.mkstemp(suffix=".db")
        os.close(descriptor)
        cls.server = create_server(port=0, database_path=cls.database_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()
        cls.client = TaskRestClient(f"http://127.0.0.1:{cls.server.server_port}")

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
        super().setUp()

    def make_storage(self):
        return RestTaskStorage(self.client)

    def test_cli_selects_rest_backend(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = task_manager_main(
                [
                    "--backend",
                    "rest",
                    "--api-url",
                    self.client.base_url,
                    "add",
                    "Remote CLI",
                ]
            )
        self.assertEqual(exit_code, 0)
        self.assertIn("Remote CLI", output.getvalue())


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        storage = FileTaskStorage(Path(self.directory.name) / "tasks.json")
        self.manager = TaskManager(storage)

    def tearDown(self):
        self.directory.cleanup()

    def test_pending_filter_is_domain_logic(self):
        self.manager.add("Pending")
        done = self.manager.add("Done")
        self.manager.complete(done.id)
        self.assertEqual(
            [task.title for task in self.manager.list_tasks(include_done=False)],
            ["Pending"],
        )

    def test_rejects_empty_title_before_calling_storage(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            self.manager.add("  ")


class TestTaskManagerCLI(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.directory.name) / "tasks.json"

    def tearDown(self):
        self.directory.cleanup()

    def run_cli(self, *arguments):
        output = io.StringIO()
        errors = io.StringIO()
        argv = ["--storage", str(self.storage_path), *arguments]
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            exit_code = task_manager_main(argv)
        return exit_code, output.getvalue(), errors.getvalue()

    def test_file_backend_commands_and_error(self):
        code, output, _ = self.run_cli("add", "From CLI")
        self.assertEqual(code, 0)
        self.assertIn("Added task #1", output)

        code, output, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("[ ] #1 From CLI", output)

        code, output, _ = self.run_cli("complete", "1")
        self.assertEqual(code, 0)
        self.assertIn("Completed task #1", output)

        _, output, _ = self.run_cli("list", "--pending-only")
        self.assertEqual(output.strip(), "No tasks yet.")

        code, output, _ = self.run_cli("remove", "1")
        self.assertEqual(code, 0)
        self.assertIn("Removed task #1", output)

        code, _, errors = self.run_cli("remove", "999")
        self.assertEqual(code, 1)
        self.assertIn("No task with id 999", errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
