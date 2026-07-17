"""Milestone 2 contract for the exact command-line interface.

The fixture covers grammar, error precedence, compact JSON envelopes, stderr,
and exit codes together because callers depend on the whole process boundary,
not merely on equivalent command semantics.
"""

import unittest

from implementation import IMPLEMENTATION
from support import run_sequential_fixture


class CLITests(unittest.TestCase):
    def test_invalid_and_usage_scenarios(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        run_sequential_fixture(self, "invalid.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
