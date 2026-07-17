"""Smoke tests for the idiomatic starter/solution harness."""

import io
import unittest
from contextlib import redirect_stdout
from importlib import import_module
from pathlib import Path

from implementation import IMPLEMENTATION
from support import test_directory

ingest_report = import_module("ingest_report")
ingest_report_cli = import_module("ingest_report.cli")


class IdiomaticHarnessSmokeTests(unittest.TestCase):
    def test_selected_target_imports_and_parses_documented_commands(self):
        # The harness milestone verifies that the selected package is coherent
        # enough to expose the documented CLI surface before feature tests run.
        parser = ingest_report_cli.build_parser()
        command_lines = (
            [
                "--db",
                "events.db",
                "ingest",
                "--import-id",
                "csv-1",
                "--format",
                "csv",
                "--input",
                "events.csv",
            ],
            [
                "--db",
                "events.db",
                "ingest",
                "--import-id",
                "jsonl-1",
                "--format",
                "jsonl",
                "--input",
                "events.jsonl",
            ],
            [
                "--db",
                "events.db",
                "ingest",
                "--import-id",
                "http-1",
                "--format",
                "http",
                "--url",
                "http://127.0.0.1:8000/events",
            ],
            ["--db", "events.db", "report", "--output", "json"],
        )

        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        self.assertEqual(
            [parser.parse_args(arguments).command for arguments in command_lines],
            ["ingest", "ingest", "ingest", "report"],
        )

    def test_selected_target_has_the_expected_learning_boundary(self):
        # Starter intentionally stops at command execution, while solution must
        # cross that boundary and run a minimal report against isolated storage.
        if IMPLEMENTATION == "starter":
            with self.assertRaisesRegex(
                ingest_report.IncompleteImplementationError,
                "idiomatic command execution.*intentionally incomplete",
            ):
                ingest_report_cli.main(["--db", "events.db", "report"])
            return
        with test_directory() as directory:
            with redirect_stdout(io.StringIO()):
                exit_code = ingest_report_cli.main(
                    ["--db", str(Path(directory) / "events.db"), "report"]
                )
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
