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
        run_sequential_fixture(self, "storage.json")
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

    def test_schema_validation_preserves_sql_literal_quotes(self):
        with test_directory() as directory:
            database = directory / "store.db"
            with closing(sqlite3.connect(database)) as connection:
                connection.executescript(
                    """
                    CREATE TABLE store_metadata (
                        singleton INTEGER PRIMARY KEY CHECK (singleton = '1'),
                        schema_version INTEGER NOT NULL CHECK (schema_version = '1'),
                        global_revision INTEGER NOT NULL
                            CHECK (global_revision BETWEEN '0' AND '9007199254740991')
                    );
                    CREATE TABLE entries (
                        key TEXT PRIMARY KEY COLLATE BINARY,
                        value_json TEXT NOT NULL CHECK (json_valid(value_json)),
                        revision INTEGER NOT NULL
                            CHECK (revision BETWEEN '1' AND '9007199254740991')
                    );
                    INSERT INTO store_metadata VALUES (1, 1, 0);
                    """
                )
            assert_process(
                self,
                run_cli(["--db", str(database), "list"]),
                {
                    "exit": 5,
                    "stderr": "",
                    "stdout": {
                        "ok": False,
                        "error": {
                            "category": "invalid_storage",
                            "details": {"reason": "malformed_schema"},
                        },
                    },
                },
            )
            _cleanup_database(database)


if __name__ == "__main__":
    unittest.main(verbosity=2)
