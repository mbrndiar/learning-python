"""Smoke tests for the comparative starter/solution harness."""

import io
import unittest
from contextlib import redirect_stdout
from importlib import import_module
from pathlib import Path

from implementation import IMPLEMENTATION
from support import test_directory

comparative_kv = import_module("comparative_kv")
comparative_cli = import_module("comparative_kv.cli")


class ComparativeHarnessSmokeTests(unittest.TestCase):
    def test_selected_target_imports_and_parses_every_command(self):
        parser = comparative_cli.build_parser()
        command_lines = (
            ["--db", "state.db", "set", "theme", "--value-json", '"dark"'],
            ["--db", "state.db", "get", "theme"],
            ["--db", "state.db", "delete", "theme"],
            ["--db", "state.db", "list"],
        )

        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        self.assertEqual(
            [parser.parse_args(arguments).command for arguments in command_lines],
            ["set", "get", "delete", "list"],
        )

    def test_selected_target_has_the_expected_learning_boundary(self):
        if IMPLEMENTATION == "starter":
            with self.assertRaisesRegex(
                comparative_kv.IncompleteImplementationError,
                "comparative command execution.*intentionally incomplete",
            ):
                comparative_cli.main(["--db", "state.db", "list"])
            return
        with test_directory() as directory, redirect_stdout(io.StringIO()) as stdout:
            exit_code = comparative_cli.main(
                ["--db", str(Path(directory) / "state.db"), "list"]
            )
        self.assertEqual(exit_code, 0)
        self.assertIn('"global_revision":0', stdout.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
