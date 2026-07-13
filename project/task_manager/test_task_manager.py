"""
Tests for the Task Manager capstone project.

Run with:
    python -m unittest project.task_manager.test_task_manager -v
or, from inside project/task_manager/:
    python test_task_manager.py
"""

import os
import tempfile
import unittest

from task_manager import Task, TaskManager, TaskNotFoundError


class TestTask(unittest.TestCase):
    def test_mark_done(self):
        task = Task(id=1, title="Write tests")
        self.assertFalse(task.done)
        task.mark_done()
        self.assertTrue(task.done)

    def test_to_dict_and_from_dict_round_trip(self):
        task = Task(id=2, title="Ship it", done=True)
        rebuilt = Task.from_dict(task.to_dict())
        self.assertEqual(task, rebuilt)


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        fd, self.storage_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.storage_path)  # start from a clean slate
        self.manager = TaskManager(self.storage_path)

    def tearDown(self):
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)

    def test_add_creates_incrementing_ids(self):
        first = self.manager.add("Task one")
        second = self.manager.add("Task two")
        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)

    def test_list_tasks_pending_only(self):
        self.manager.add("Pending task")
        done_task = self.manager.add("Done task")
        self.manager.complete(done_task.id)

        pending = self.manager.list_tasks(include_done=False)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].title, "Pending task")

    def test_complete_unknown_task_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete(999)

    def test_remove_task(self):
        task = self.manager.add("Temporary task")
        self.manager.remove(task.id)
        self.assertEqual(self.manager.list_tasks(), [])

    def test_persistence_across_instances(self):
        self.manager.add("Persisted task")
        reloaded = TaskManager(self.storage_path)
        self.assertEqual(len(reloaded.list_tasks()), 1)
        self.assertEqual(reloaded.list_tasks()[0].title, "Persisted task")


if __name__ == "__main__":
    unittest.main(verbosity=2)
