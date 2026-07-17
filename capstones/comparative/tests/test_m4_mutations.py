"""Milestone 4 contract for atomic mutations and compare-and-set revisions.

Normal and boundary fixtures specify creation, replacement, deletion, ordering,
and revision transitions as one mutation model.  Exact CAS outcomes matter
because later process-contention tests rely on these operations being atomic.
"""

import unittest

from implementation import IMPLEMENTATION
from support import run_sequential_fixture


class MutationTests(unittest.TestCase):
    def test_all_normal_and_boundary_scenarios(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        run_sequential_fixture(self, "normal.json")
        run_sequential_fixture(self, "boundary.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
