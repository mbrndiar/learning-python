"""Milestone 3 contract for schema identity, initialization, and migration.

Scenario fixtures exercise persistence and reopen behavior, while direct SQLite
inspection prevents an implementation from passing with an approximately
equivalent schema or with undeclared application objects and metadata.
"""

import sqlite3
import unittest
from contextlib import closing

from implementation import IMPLEMENTATION
from support import (
    _cleanup_database,
    assert_process,
    run_cli,
    run_sequential_fixture,
    test_directory,
)


class StorageTests(unittest.TestCase):
    def test_normal_and_migration_scenarios(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        run_sequential_fixture(self, "normal.json")
        run_sequential_fixture(self, "migration.json")

    def test_fresh_schema_has_only_the_two_exact_application_tables(self):
        with test_directory() as directory:
            database = directory / "store.db"
            assert_process(
                self,
                run_cli(["--db", str(database), "list"]),
                {
                    "exit": 0,
                    "stderr": "",
                    "stdout": {
                        "ok": True,
                        "result": {"entries": [], "global_revision": 0},
                    },
                },
            )
            with closing(sqlite3.connect(database)) as connection:
                objects = connection.execute(
                    """
                    SELECT type, name
                    FROM sqlite_schema
                    WHERE name NOT LIKE 'sqlite_%'
                    ORDER BY type, name
                    """
                ).fetchall()
                metadata = connection.execute(
                    """
                    SELECT singleton, schema_version, global_revision
                    FROM store_metadata
                    """
                ).fetchall()
                self.assertEqual(
                    connection.execute("PRAGMA user_version").fetchone(), (0,)
                )
                self.assertEqual(
                    connection.execute("PRAGMA application_id").fetchone(), (0,)
                )
            self.assertEqual(
                objects, [("table", "entries"), ("table", "store_metadata")]
            )
            self.assertEqual(metadata, [(1, 1, 0)])
            _cleanup_database(database)


if __name__ == "__main__":
    unittest.main(verbosity=2)
