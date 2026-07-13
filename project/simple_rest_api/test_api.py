"""Integration tests for the notes REST API."""

import http.client
import json
import os
import tempfile
import threading
import unittest

from api import NoteStore, create_server


class TestNotesAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_descriptor, cls.database_path = tempfile.mkstemp(suffix=".db")
        os.close(file_descriptor)
        # Port 0 asks the operating system for an unused test port.
        cls.server = create_server(port=0, database_path=cls.database_path)
        # serve_forever blocks, so the test server runs beside the test thread.
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
            connection.execute("DELETE FROM notes")
            connection.execute("DELETE FROM sqlite_sequence WHERE name = 'notes'")

    def request(self, method, path, data=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_port, timeout=2
        )
        body = json.dumps(data) if data is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read()
        connection.close()
        return response.status, json.loads(content) if content else None

    def test_create_list_update_and_delete_note(self):
        status, created = self.request(
            "POST", "/notes", {"title": "Learn HTTP", "body": "Build an API"}
        )
        self.assertEqual(status, 201)
        self.assertEqual(created["id"], 1)

        status, notes = self.request("GET", "/notes")
        self.assertEqual(status, 200)
        self.assertEqual(notes, [created])

        status, updated = self.request(
            "PUT", "/notes/1", {"title": "Learn REST", "body": "Done"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(updated["title"], "Learn REST")

        status, content = self.request("DELETE", "/notes/1")
        self.assertEqual(status, 204)
        self.assertIsNone(content)

    def test_rejects_invalid_note(self):
        status, content = self.request("POST", "/notes", {"title": "  "})
        self.assertEqual(status, 400)
        self.assertIn("title", content["error"])

    def test_returns_not_found(self):
        status, content = self.request("GET", "/notes/999")
        self.assertEqual(status, 404)
        self.assertEqual(content, {"error": "Note not found"})

    def test_notes_persist_in_sqlite(self):
        self.request("POST", "/notes", {"title": "Persist me"})
        reopened_store = NoteStore(self.database_path)
        self.assertEqual(reopened_store.list()[0]["title"], "Persist me")


if __name__ == "__main__":
    unittest.main(verbosity=2)
