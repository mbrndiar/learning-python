from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "learning_state.py"
SPEC = importlib.util.spec_from_file_location("learning_state", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
learning_state = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = learning_state
SPEC.loader.exec_module(learning_state)

REMOTE = "git@GitHub.com:Example/Learning-Python.git"
COMMIT_A = "a" * 40
COMMIT_B = "b" * 40
AT = "2026-07-18T20:00:00Z"
CONCEPTS = {
    "concepts": [
        {
            "id": "basics",
            "order": 10,
            "solution_unlock_after": 2,
            "title": "Python basics",
        },
        {
            "id": "loops",
            "order": 20,
            "prerequisites": ["basics"],
            "title": "Loops",
        },
        {
            "id": "functions",
            "order": 30,
            "prerequisites": ["loops"],
            "title": "Functions",
        },
    ]
}


class LearningStateCLITests(unittest.TestCase):
    def setUp(self) -> None:
        test_dir = Path(__file__).parent
        self.temporary = tempfile.TemporaryDirectory(
            prefix=".learning-state-test-",
            dir=test_dir,
        )
        self.root = Path(self.temporary.name)
        self.db = self.root / "state.sqlite3"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(
        self,
        *arguments: str,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        environment = {} if env is None else env
        with (
            mock.patch.dict(os.environ, environment, clear=False),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            code = learning_state.main(list(arguments))
        return code, stdout.getvalue(), stderr.getvalue()

    def command(
        self,
        command: str,
        *,
        commit: str = COMMIT_A,
        db: Path | None = None,
        local: Path | None = None,
        at: str = AT,
        extra: tuple[str, ...] = (),
    ) -> tuple[int, str, str]:
        identity = (
            ("--local-fallback", str(local))
            if local is not None
            else ("--remote", REMOTE)
        )
        return self.run_cli(
            "--db",
            str(self.db if db is None else db),
            command,
            *identity,
            "--commit",
            commit,
            "--at",
            at,
            *extra,
        )

    def initialize(
        self,
        *,
        commit: str = COMMIT_A,
        concepts: dict[str, object] = CONCEPTS,
        db: Path | None = None,
    ) -> dict[str, object]:
        code, stdout, stderr = self.command(
            "init-course",
            commit=commit,
            db=db,
            extra=("--concepts-json", json.dumps(concepts)),
        )
        self.assertEqual((code, stderr), (0, ""))
        return json.loads(stdout)

    def test_initialization_is_idempotent_and_schema_is_versioned(self) -> None:
        first = self.initialize()
        second = self.initialize()

        self.assertEqual(
            first["created"],
            {"course": True, "version": True},
        )
        self.assertEqual(
            second["created"],
            {"course": False, "version": False},
        )
        self.assertEqual(first["schema_version"], 1)
        with contextlib.closing(sqlite3.connect(self.db)) as connection, connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            counts = {
                table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[
                    0
                ]
                for table in ("courses", "course_versions", "concepts")
            }
            mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        self.assertEqual(version, learning_state.SCHEMA_VERSION)
        self.assertEqual(
            counts,
            {"courses": 1, "course_versions": 1, "concepts": 3},
        )
        self.assertEqual(mode, "wal")

    def test_rejects_newer_and_corrupt_versioned_schemas(self) -> None:
        newer = self.root / "newer.sqlite3"
        with contextlib.closing(sqlite3.connect(newer)) as connection, connection:
            connection.execute("PRAGMA user_version = 99")
        code, stdout, stderr = self.command("status", db=newer)
        self.assertEqual((code, stdout), (learning_state.EXIT_STATE, ""))
        self.assertIn("unsupported schema version 99", stderr)

        corrupt = self.root / "corrupt.sqlite3"
        with contextlib.closing(sqlite3.connect(corrupt)) as connection, connection:
            connection.execute(
                "CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT)"
            )
            connection.execute("INSERT INTO schema_meta VALUES ('schema_version', '1')")
            connection.execute("PRAGMA user_version = 1")
        code, stdout, stderr = self.command("status", db=corrupt)
        self.assertEqual((code, stdout), (learning_state.EXIT_STATE, ""))
        self.assertIn("missing table courses", stderr)

    def test_remote_normalization_and_explicit_local_fallback(self) -> None:
        expected = "github.com/Example/Learning-Python"
        remotes = (
            "https://GitHub.com/Example/Learning-Python.git/",
            "ssh://git@github.com/Example/Learning-Python.git",
            "git@github.com:Example/Learning-Python.git",
            "git://github.com/Example/Learning-Python",
        )
        self.assertEqual(
            [learning_state.normalize_remote_url(value) for value in remotes],
            [expected] * len(remotes),
        )

        code, stdout, stderr = self.run_cli(
            "--db",
            str(self.db),
            "init-course",
            "--commit",
            COMMIT_A,
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_USAGE, ""))
        self.assertIn("--remote", stderr)

        local = self.root / "course"
        code, stdout, stderr = self.command(
            "init-course",
            local=local,
            extra=("--concepts-json", '{"concepts":[]}'),
        )
        self.assertEqual(code, 0)
        self.assertIn("warning:", stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["course"]["kind"], "local")
        self.assertEqual(payload["warnings"], [learning_state.LOCAL_WARNING])

    def test_environment_database_override(self) -> None:
        environment_db = self.root / "environment.sqlite3"
        code, stdout, stderr = self.run_cli(
            "init-course",
            "--remote",
            REMOTE,
            "--commit",
            COMMIT_A,
            "--at",
            AT,
            "--concepts-json",
            '{"concepts":[]}',
            env={learning_state.DB_ENV_VAR: str(environment_db)},
        )
        self.assertEqual((code, stderr), (0, ""))
        self.assertTrue(environment_db.exists())
        self.assertEqual(json.loads(stdout)["concepts"]["total"], 0)

    def test_commit_change_preserves_stable_mastery(self) -> None:
        self.initialize()
        code, _, _ = self.command(
            "record-mastery",
            extra=("--concept", "basics", "--mastered"),
        )
        self.assertEqual(code, 0)
        self.initialize(commit=COMMIT_B)

        code, stdout, stderr = self.command("status", commit=COMMIT_B)
        self.assertEqual((code, stderr), (0, ""))
        concepts = {
            concept["id"]: concept for concept in json.loads(stdout)["concepts"]
        }
        self.assertEqual(concepts["basics"]["mastery"], "mastered")
        self.assertFalse(concepts["basics"]["solution"]["unlocked"])
        with contextlib.closing(sqlite3.connect(self.db)) as connection, connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM mastery").fetchone()[0],
                1,
            )

    def test_new_commit_requires_current_attempt_for_requested_unlock(self) -> None:
        concepts = {
            "concepts": [
                {
                    "id": "versioned",
                    "solution_unlock_after": 1,
                    "title": "Versioned solution",
                }
            ]
        }
        self.initialize(concepts=concepts)
        code, _, _ = self.command(
            "record-attempt",
            extra=("--concept", "versioned", "--outcome", "passed"),
        )
        self.assertEqual(code, 0)
        code, _, _ = self.command(
            "record-mastery",
            extra=("--concept", "versioned", "--mastered"),
        )
        self.assertEqual(code, 0)
        self.initialize(commit=COMMIT_B, concepts=concepts)

        code, stdout, stderr = self.command(
            "unlock-solution",
            commit=COMMIT_B,
            extra=("--concept", "versioned"),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_CONFLICT, ""))
        self.assertIn("(0 recorded)", stderr)

        code, _, _ = self.command(
            "record-attempt",
            commit=COMMIT_B,
            extra=("--concept", "versioned", "--outcome", "failed"),
        )
        self.assertEqual(code, 0)
        code, stdout, stderr = self.command(
            "unlock-solution",
            commit=COMMIT_B,
            extra=("--concept", "versioned"),
        )
        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual(
            json.loads(stdout)["reason"],
            "post_attempt_request",
        )

    def test_new_commit_requires_current_pass_for_deterministic_unlock(self) -> None:
        concepts = {
            "concepts": [
                {
                    "id": "versioned",
                    "solution_unlock_after": 1,
                    "title": "Versioned solution",
                }
            ]
        }
        self.initialize(concepts=concepts)
        code, _, _ = self.command(
            "record-attempt",
            extra=("--concept", "versioned", "--outcome", "passed"),
        )
        self.assertEqual(code, 0)
        code, _, _ = self.command(
            "record-mastery",
            extra=("--concept", "versioned", "--mastered"),
        )
        self.assertEqual(code, 0)
        self.initialize(commit=COMMIT_B, concepts=concepts)

        code, stdout, stderr = self.command(
            "unlock-solution",
            commit=COMMIT_B,
            extra=("--concept", "versioned"),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_CONFLICT, ""))
        self.assertIn("(0 recorded)", stderr)

        code, _, _ = self.command(
            "record-attempt",
            commit=COMMIT_B,
            extra=("--concept", "versioned", "--outcome", "passed"),
        )
        self.assertEqual(code, 0)
        code, stdout, stderr = self.command(
            "unlock-solution",
            commit=COMMIT_B,
            extra=("--concept", "versioned"),
        )
        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual(
            json.loads(stdout)["reason"],
            "deterministic_success",
        )

    def test_concept_import_upserts_without_duplication(self) -> None:
        self.initialize()
        updated = {
            "concepts": [
                {
                    "id": "basics",
                    "order": 5,
                    "solution_unlock_after": 4,
                    "title": "Updated basics",
                }
            ]
        }
        self.initialize(concepts=updated)

        code, stdout, _ = self.command("status")
        self.assertEqual(code, 0)
        concepts = {
            concept["id"]: concept for concept in json.loads(stdout)["concepts"]
        }
        self.assertEqual(len(concepts), 3)
        self.assertEqual(concepts["basics"]["title"], "Updated basics")
        self.assertEqual(concepts["basics"]["order"], 5)
        self.assertEqual(
            concepts["basics"]["solution"]["attempts_required_for_request"],
            4,
        )

    def test_next_objective_respects_prerequisites_and_order(self) -> None:
        self.initialize()
        code, stdout, _ = self.command("next-objective")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["objective"]["id"], "basics")

        self.command(
            "record-mastery",
            extra=("--concept", "basics", "--practiced"),
        )
        code, stdout, _ = self.command("next-objective")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["objective"]["id"], "loops")

        self.command(
            "record-mastery",
            extra=("--concept", "basics", "--mastered"),
        )
        self.command(
            "record-mastery",
            extra=("--concept", "loops", "--mastered"),
        )
        self.command(
            "record-mastery",
            extra=("--concept", "functions", "--mastered"),
        )
        code, stdout, _ = self.command("next-objective")
        payload = json.loads(stdout)
        self.assertEqual(code, 0)
        self.assertIsNone(payload["objective"])
        self.assertEqual(payload["reason"], "course_complete")

    def test_attempts_and_hints_store_only_structured_events(self) -> None:
        self.initialize()
        code, stdout, _ = self.command(
            "record-attempt",
            extra=(
                "--concept",
                "basics",
                "--outcome",
                "fail",
                "--score",
                "0.25",
            ),
        )
        self.assertEqual(code, 0)
        attempt = json.loads(stdout)
        self.assertEqual(attempt["outcome"], "failed")
        self.assertEqual(attempt["mastery"], "in_progress")

        code, stdout, _ = self.command(
            "record-hint",
            extra=("--concept", "basics", "--hint-level", "2"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["hints"], 1)

        with contextlib.closing(sqlite3.connect(self.db)) as connection, connection:
            rows = connection.execute(
                """
                SELECT event_type, outcome, score, hint_level
                FROM attempts
                ORDER BY id
                """
            ).fetchall()
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(attempts)")
            }
        self.assertEqual(
            rows,
            [
                ("attempt", "failed", 0.25, None),
                ("hint", None, None, 2),
            ],
        )
        self.assertTrue(
            {"source", "source_code", "prompt", "transcript"}.isdisjoint(columns)
        )

    def test_mastery_and_review_scheduling(self) -> None:
        self.initialize()
        code, stdout, _ = self.command(
            "record-mastery",
            extra=(
                "--concept",
                "basics",
                "--level",
                "mastered",
                "--review-in-days",
                "0",
            ),
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["review"]["due_at"], AT)

        code, stdout, _ = self.command("due-reviews")
        payload = json.loads(stdout)
        self.assertEqual(code, 0)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["reviews"][0]["id"], "basics")

        next_review = "2026-07-19T20:00:00Z"
        code, stdout, _ = self.command(
            "record-mastery",
            at=next_review,
            extra=(
                "--concept",
                "basics",
                "--mastered",
                "--review-result",
                "good",
            ),
        )
        review = json.loads(stdout)["review"]
        self.assertEqual(code, 0)
        self.assertEqual(review["interval_days"], 1)
        self.assertEqual(review["repetitions"], 1)
        self.assertEqual(review["due_at"], "2026-07-20T20:00:00Z")

    def test_solution_lock_policy_and_idempotent_unlock(self) -> None:
        self.initialize()
        code, stdout, stderr = self.command(
            "unlock-solution",
            extra=("--concept", "basics"),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_CONFLICT, ""))
        self.assertIn("2 genuine attempts", stderr)

        code, _, _ = self.command(
            "record-attempt",
            extra=("--concept", "basics", "--outcome", "skipped"),
        )
        self.assertEqual(code, 0)
        code, stdout, stderr = self.command(
            "unlock-solution",
            extra=("--concept", "basics"),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_CONFLICT, ""))
        self.assertIn("(0 recorded)", stderr)

        for _ in range(2):
            code, _, _ = self.command(
                "record-attempt",
                extra=("--concept", "basics", "--outcome", "failed"),
            )
            self.assertEqual(code, 0)
        code, stdout, _ = self.command(
            "unlock-solution",
            extra=("--concept", "basics"),
        )
        unlocked = json.loads(stdout)
        self.assertEqual(code, 0)
        self.assertTrue(unlocked["newly_unlocked"])
        self.assertEqual(unlocked["reason"], "post_attempt_request")

        code, stdout, _ = self.command(
            "unlock-solution",
            extra=("--concept", "basics"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["reason"], "already_unlocked")

        code, _, _ = self.command(
            "record-attempt",
            extra=("--concept", "loops", "--outcome", "passed"),
        )
        self.assertEqual(code, 0)
        code, stdout, _ = self.command(
            "unlock-solution",
            extra=("--concept", "loops"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(stdout)["reason"],
            "deterministic_success",
        )

    def test_json_output_is_compact_sorted_and_deterministic(self) -> None:
        self.initialize()
        first = self.command("status")
        second = self.command("status")
        self.assertEqual(first, second)
        code, stdout, stderr = first
        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual(stdout, learning_state.compact_json(json.loads(stdout)) + "\n")
        self.assertNotIn(": ", stdout)

    def test_invalid_input_has_stable_exit_categories(self) -> None:
        self.initialize()
        code, stdout, stderr = self.command(
            "record-attempt",
            extra=("--concept", "basics", "--outcome", "maybe"),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_USAGE, ""))
        self.assertTrue(stderr.startswith("error[usage]:"))

        code, stdout, stderr = self.command(
            "record-hint",
            extra=("--concept", "missing", "--hint-level", "1"),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_NOT_FOUND, ""))
        self.assertTrue(stderr.startswith("error[not-found]:"))

        code, stdout, stderr = self.command("status", commit="not-a-sha")
        self.assertEqual((code, stdout), (learning_state.EXIT_USAGE, ""))
        self.assertTrue(stderr.startswith("error[usage]:"))

    def test_failed_import_rolls_back_the_whole_course_version(self) -> None:
        self.initialize()
        invalid = {
            "concepts": [
                {
                    "id": "advanced",
                    "prerequisites": ["missing"],
                }
            ]
        }
        code, stdout, stderr = self.command(
            "init-course",
            commit=COMMIT_B,
            extra=("--concepts-json", json.dumps(invalid)),
        )
        self.assertEqual((code, stdout), (learning_state.EXIT_USAGE, ""))
        self.assertIn("unknown prerequisites", stderr)
        with contextlib.closing(sqlite3.connect(self.db)) as connection, connection:
            versions = connection.execute(
                "SELECT commit_sha FROM course_versions ORDER BY commit_sha"
            ).fetchall()
            concepts = connection.execute(
                """
                SELECT COUNT(*)
                FROM concepts AS c
                JOIN course_versions AS v ON v.id = c.course_version_id
                WHERE v.commit_sha = ?
                """,
                (COMMIT_B,),
            ).fetchone()[0]
        self.assertEqual(versions, [(COMMIT_A,)])
        self.assertEqual(concepts, 0)

    def test_busy_database_returns_conflict_without_waiting(self) -> None:
        self.initialize()
        holder = sqlite3.connect(self.db, isolation_level=None)
        try:
            holder.execute("BEGIN IMMEDIATE")
            code, stdout, stderr = self.run_cli(
                "--db",
                str(self.db),
                "--busy-timeout-ms",
                "0",
                "status",
                "--remote",
                REMOTE,
                "--commit",
                COMMIT_A,
                "--at",
                AT,
            )
        finally:
            holder.execute("ROLLBACK")
            holder.close()
        self.assertEqual((code, stdout), (learning_state.EXIT_CONFLICT, ""))
        self.assertEqual(stderr, "error[conflict]: state database is busy\n")

    def test_concurrent_writers_are_serialized_by_busy_timeout(self) -> None:
        self.initialize()

        def write_attempt(index: int) -> str:
            parser = learning_state.build_parser()
            args = parser.parse_args(
                [
                    "--db",
                    str(self.db),
                    "--busy-timeout-ms",
                    "5000",
                    "record-attempt",
                    "--remote",
                    REMOTE,
                    "--commit",
                    COMMIT_A,
                    "--at",
                    f"2026-07-18T20:00:0{index}Z",
                    "--concept",
                    "basics",
                    "--outcome",
                    "failed",
                ]
            )
            return learning_state.execute(args).payload["outcome"]

        with ThreadPoolExecutor(max_workers=4) as executor:
            outcomes = list(executor.map(write_attempt, range(4)))
        self.assertEqual(outcomes, ["failed"] * 4)
        with contextlib.closing(sqlite3.connect(self.db)) as connection, connection:
            attempts = connection.execute(
                """
                SELECT COUNT(*) FROM attempts
                WHERE event_type = 'attempt'
                """
            ).fetchone()[0]
        self.assertEqual(attempts, 4)


if __name__ == "__main__":
    unittest.main()
