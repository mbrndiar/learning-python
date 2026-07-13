"""Integration tests for the notes CLI and REST API."""

import contextlib
import io
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

REST_API_DIRECTORY = Path(__file__).parents[1] / "simple_rest_api"
# The examples are deliberately plain scripts rather than installed packages.
sys.path.insert(0, str(REST_API_DIRECTORY))

from api import create_server
from notes_cli import main


class TestNotesCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_descriptor, cls.database_path = tempfile.mkstemp(suffix=".db")
        os.close(file_descriptor)
        # Let the operating system choose a free port for this isolated server.
        cls.server = create_server(port=0, database_path=cls.database_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.start()
        cls.api_arguments = [
            "--api-url",
            f"http://127.0.0.1:{cls.server.server_port}",
        ]

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

    def run_cli(self, *arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exit_code = main(self.api_arguments + list(arguments))
        return exit_code, output.getvalue()

    def test_add_list_update_and_delete(self):
        exit_code, output = self.run_cli("add", "First", "--body", "Some text")
        self.assertEqual(exit_code, 0)
        self.assertIn("#1 First", output)

        _, output = self.run_cli("list")
        self.assertIn("Some text", output)

        _, output = self.run_cli("update", "1", "Changed")
        self.assertIn("#1 Changed", output)

        _, output = self.run_cli("delete", "1")
        self.assertIn("Deleted note #1", output)

    def test_export_and_import_json_file(self):
        self.run_cli("add", "Exported", "--body", "From API")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.json"
            exit_code, _ = self.run_cli("export", str(path))
            self.assertEqual(exit_code, 0)
            self.run_cli("delete", "1")
            exit_code, output = self.run_cli("import", str(path))
        self.assertEqual(exit_code, 0)
        self.assertIn("Imported 1 note(s)", output)
        _, output = self.run_cli("list")
        self.assertIn("Exported", output)

    def test_reports_invalid_import_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.json"
            path.write_text("{}", encoding="utf-8")
            exit_code, output = self.run_cli("import", str(path))
        self.assertEqual(exit_code, 1)
        self.assertIn("JSON list", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
