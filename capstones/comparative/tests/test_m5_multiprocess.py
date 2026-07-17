"""Milestone 5 contract for independent-process contention and cleanup.

The fixture runs real CLI children against one database and checks permitted
aggregate outcomes, lock behavior, deadlines, and final state.  Repetition
samples nondeterministic interleavings; it does not promise deterministic
scheduling, fairness, or prove that unobserved races are absent.
"""

import unittest

from implementation import IMPLEMENTATION
from support import run_multiprocess_fixture


class MultiprocessTests(unittest.TestCase):
    def test_every_required_process_scenario_and_repeat(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        run_multiprocess_fixture(self)


if __name__ == "__main__":
    unittest.main(verbosity=2)
