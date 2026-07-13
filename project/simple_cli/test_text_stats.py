"""Tests for the text statistics CLI."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from text_stats import count_text, main


class TestTextStats(unittest.TestCase):
    def test_count_text(self):
        self.assertEqual(
            count_text("Hello, Python!\nKeep learning."),
            {"lines": 2, "words": 4, "characters": 29},
        )

    def test_main_counts_text_argument(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(["--text", "one two"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Words: 2", output.getvalue())

    def test_main_reads_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("first\nsecond", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["--file", str(path)])
        self.assertEqual(exit_code, 0)
        self.assertIn("Lines: 2", output.getvalue())

    def test_main_reports_missing_file(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(["--file", "does-not-exist.txt"])
        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
