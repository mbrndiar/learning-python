"""Integration tests for the notes REST API."""

import http.client
import json
import threading
import unittest

from api import create_server


class TestNotesAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.store.notes.clear()
        self.server.store.next_id = 1

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
