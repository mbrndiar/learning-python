"""Milestone 2: exact CLI grammar, envelopes, precedence, and exit codes."""

import unittest

from implementation import IMPLEMENTATION
from support import run_sequential_fixture


class CLITests(unittest.TestCase):
    def test_invalid_and_usage_scenarios(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        run_sequential_fixture(self, "invalid.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
