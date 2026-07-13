"""Contract and integration tests for Task Manager storage strategies."""

import os
import tempfile
import threading
import unittest
from pathlib import Path

from project.task_manager.storage import FileTaskStorage, RestTaskStorage
from project.task_manager.task_manager import Task, TaskManager, TaskNotFoundError
from project.task_rest_api.api import create_server
from project.task_rest_client.client import TaskRestClient


class TestTask(unittest.TestCase):
    def test_dictionary_round_trip_and_completion(self):
        task = Task(id=2, title="Ship it")
        task.mark_done()
        self.assertEqual(Task.from_dict(task.to_dict()), task)


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


class TestRestTaskStorage(StorageContract, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        descriptor, cls.database_path = tempfile.mkstemp(suffix=".db")
        os.close(descriptor)
        cls.server = create_server(port=0, database_path=cls.database_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()
        cls.client = TaskRestClient(
            f"http://127.0.0.1:{cls.server.server_port}"
        )

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
