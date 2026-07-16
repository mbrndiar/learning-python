"""Milestone 5: real child-process races, busy behavior, and cleanup."""

import unittest

from implementation import IMPLEMENTATION
from support import run_multiprocess_fixture


class MultiprocessTests(unittest.TestCase):
    def test_every_required_process_scenario_and_repeat(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        run_multiprocess_fixture(self)


if __name__ == "__main__":
    unittest.main(verbosity=2)
