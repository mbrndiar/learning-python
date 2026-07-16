"""Smoke tests for the comparative starter/solution harness."""

import unittest
from importlib import import_module

from implementation import IMPLEMENTATION

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

    def test_selected_target_reaches_only_the_intentional_placeholder(self):
        with self.assertRaisesRegex(
            comparative_kv.IncompleteImplementationError,
            "comparative command execution.*intentionally incomplete",
        ):
            comparative_cli.main(["--db", "state.db", "list"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
