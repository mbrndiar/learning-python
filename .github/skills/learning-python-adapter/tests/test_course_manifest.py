from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ADAPTER_DIR = TESTS_DIR.parent
REPOSITORY_ROOT = ADAPTER_DIR.parents[2]
MANIFEST_PATH = ADAPTER_DIR / "course.toml"
ADAPTER_SCRIPT = ADAPTER_DIR / "scripts" / "course_adapter.py"
STATE_SCRIPT = (
    REPOSITORY_ROOT
    / ".github"
    / "skills"
    / "learning-tutor-core"
    / "scripts"
    / "learning_state.py"
)
TEST_COMMIT = "c" * 40

SPEC = importlib.util.spec_from_file_location("course_adapter", ADAPTER_SCRIPT)
assert SPEC is not None and SPEC.loader is not None
course_adapter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = course_adapter
SPEC.loader.exec_module(course_adapter)


@contextmanager
def invalid_manifest_copy(
    *replacements: tuple[str, str],
) -> Iterator[Path]:
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in manifest_text:
            raise AssertionError(f"test replacement not found: {old}")
        manifest_text = manifest_text.replace(old, new, 1)
    with tempfile.TemporaryDirectory(
        prefix=".invalid-course-manifest-",
        dir=TESTS_DIR,
    ) as temporary:
        path = Path(temporary) / "course.toml"
        path.write_text(manifest_text, encoding="utf-8")
        yield path


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ADAPTER_SCRIPT), *arguments],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class CourseManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = course_adapter.load_manifest()
        cls.projection = course_adapter.validate_manifest(cls.manifest)

    def assert_invalid_manifest_copy(
        self,
        replacements: tuple[tuple[str, str], ...],
        expected_message: str,
    ) -> None:
        with invalid_manifest_copy(*replacements) as path:
            with self.assertRaisesRegex(
                course_adapter.ManifestValidationError,
                expected_message,
            ):
                course_adapter.validate_manifest(course_adapter.load_manifest(path))

            result = run_cli(
                "validate",
                "--manifest",
                str(path),
                "--repository-root",
                str(REPOSITORY_ROOT),
            )
            self.assertEqual(
                result.returncode,
                course_adapter.EXIT_INVALID_MANIFEST,
            )
            self.assertEqual(result.stdout, "")
            self.assertIn(expected_message, result.stderr)
            self.assertEqual(len(result.stderr.splitlines()), 1)

    def test_toml_and_schema_versions_are_supported(self) -> None:
        self.assertEqual(
            self.manifest["manifest_version"],
            course_adapter.SUPPORTED_MANIFEST_VERSION,
        )
        self.assertEqual(
            self.manifest["schema_version"],
            course_adapter.SUPPORTED_SCHEMA_VERSION,
        )
        schema_path = REPOSITORY_ROOT / self.manifest["schema_document"]
        schema_heading = schema_path.read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(schema_heading, "# Course manifest schema 1.0")

    def test_all_declared_repository_paths_and_review_headings_exist(self) -> None:
        paths = list(course_adapter.declared_paths(self.manifest))
        self.assertGreater(len(paths), 100)
        self.assertEqual(len(paths), len({label for label, _ in paths}))
        course_adapter.validate_paths(self.manifest)

    def test_trackable_ids_are_unique_and_prerequisites_are_acyclic(self) -> None:
        known_ids = course_adapter.validate_trackable_ids_and_graph(self.manifest)
        projected_ids = {concept["id"] for concept in self.projection["concepts"]}
        self.assertEqual(projected_ids, known_ids)
        self.assertEqual(len(known_ids), 76)

    def test_flattened_state_projection_is_complete_and_deterministic(self) -> None:
        repeated = course_adapter.flatten_state_projection(
            course_adapter.load_manifest()
        )
        self.assertEqual(
            course_adapter.compact_json(self.projection),
            course_adapter.compact_json(repeated),
        )
        concepts = self.projection["concepts"]
        self.assertEqual(
            [concept["order"] for concept in concepts],
            list(range(10, 10 * (len(concepts) + 1), 10)),
        )

        expected_ids: list[str] = []
        modules = sorted(
            course_adapter.records(self.manifest, "modules"),
            key=lambda item: item["ordinal"],
        )
        for module in modules[:11]:
            expected_ids.extend(concept["id"] for concept in module["concepts"])
            expected_ids.append(module["id"])
        project = self.manifest["projects"][0]
        expected_ids.extend(milestone["id"] for milestone in project["milestones"])
        expected_ids.append(project["id"])
        expected_ids.extend(concept["id"] for concept in modules[11]["concepts"])
        expected_ids.append(modules[11]["id"])
        for capstone in self.manifest["capstones"]:
            expected_ids.extend(milestone["id"] for milestone in capstone["milestones"])
            expected_ids.append(capstone["id"])
        self.assertEqual(
            [concept["id"] for concept in concepts],
            expected_ids,
        )

        by_id = {concept["id"]: concept for concept in concepts}
        self.assertEqual(
            by_id["concept.control-flow.conditionals"]["prerequisites"],
            ["module.basics"],
        )
        self.assertEqual(
            by_id["milestone.tasks.domain-and-contracts"]["prerequisites"],
            ["module.sql-and-sqlite", "module.rest-apis-and-clients"],
        )
        self.assertEqual(
            by_id["milestone.tasks.persistence"]["prerequisites"],
            [
                "module.sql-and-sqlite",
                "module.rest-apis-and-clients",
                "milestone.tasks.domain-and-contracts",
            ],
        )
        parent_positions = {
            concept["id"]: index for index, concept in enumerate(concepts)
        }
        for module in self.manifest["modules"]:
            self.assertTrue(
                all(
                    parent_positions[concept["id"]] < parent_positions[module["id"]]
                    for concept in module["concepts"]
                )
            )
        for owner_kind in ("projects", "capstones"):
            for owner in self.manifest[owner_kind]:
                self.assertTrue(
                    all(
                        parent_positions[milestone["id"]]
                        < parent_positions[owner["id"]]
                        for milestone in owner["milestones"]
                    )
                )

    def test_solution_locks_match_declared_owners_and_policy(self) -> None:
        locks = course_adapter.validate_solution_locks(self.manifest)
        self.assertEqual(len(locks), 15)
        self.assertEqual(
            {lock["unlock_policy"] for lock in locks.values()},
            {
                "after-unit-validation",
                "after-matching-milestone-validation",
            },
        )
        self.assertEqual(
            {
                concept["solution_unlock_after"]
                for concept in self.projection["concepts"]
            },
            {1},
        )

    def test_required_outcomes_cover_every_container_and_milestone(self) -> None:
        course_adapter.validate_required_outcomes(self.manifest)
        containers = [
            owner
            for owner_kind in ("modules", "projects", "capstones")
            for owner in self.manifest[owner_kind]
        ]
        milestones = [
            milestone
            for owner_kind in ("projects", "capstones")
            for owner in self.manifest[owner_kind]
            for milestone in owner["milestones"]
        ]
        self.assertEqual(len(containers), 15)
        self.assertEqual(len(milestones), 15)

    def test_commands_and_selectors_match_the_documented_contract(self) -> None:
        course_adapter.validate_commands_and_selectors(self.manifest)
        selectors = [
            owner["implementation_selector"]
            for kind in ("projects", "capstones")
            for owner in self.manifest[kind]
        ]
        self.assertEqual(
            {selector["environment"] for selector in selectors},
            {"PROJECT_IMPLEMENTATION", "CAPSTONE_IMPLEMENTATION"},
        )

    def test_validate_cli_emits_compact_deterministic_json(self) -> None:
        result = run_cli("validate")
        expected = {
            "manifest_version": 1,
            "schema_version": "1.0.0",
            "status": "valid",
            "trackable_count": 76,
        }
        self.assertEqual(result.returncode, course_adapter.EXIT_OK)
        self.assertEqual(result.stdout, f"{course_adapter.compact_json(expected)}\n")
        self.assertEqual(result.stderr, "")

    def test_state_projection_cli_matches_production_function(self) -> None:
        first = run_cli("state-projection")
        second = run_cli("state-projection")
        expected = f"{course_adapter.compact_json(self.projection)}\n"
        self.assertEqual(first.returncode, course_adapter.EXIT_OK)
        self.assertEqual(first.stdout, expected)
        self.assertEqual(first.stderr, "")
        self.assertEqual(second.stdout, first.stdout)

    def test_cli_has_stable_invalid_usage_and_io_exit_categories(self) -> None:
        usage = run_cli("unknown-command")
        self.assertEqual(usage.returncode, course_adapter.EXIT_USAGE)
        self.assertEqual(usage.stdout, "")
        self.assertIn("invalid choice", usage.stderr)

        missing = run_cli(
            "validate",
            "--manifest",
            str(TESTS_DIR / "missing-course.toml"),
            "--repository-root",
            str(REPOSITORY_ROOT),
        )
        self.assertEqual(missing.returncode, course_adapter.EXIT_IO)
        self.assertEqual(missing.stdout, "")
        self.assertTrue(missing.stderr.startswith("course-adapter: I/O error:"))
        self.assertEqual(len(missing.stderr.splitlines()), 1)

    def test_invalid_toml_copy_is_rejected_by_function_and_cli(self) -> None:
        with invalid_manifest_copy(
            ("manifest_version = 1", "manifest_version = ["),
        ) as path:
            with self.assertRaises(tomllib.TOMLDecodeError):
                course_adapter.load_manifest(path)
            result = run_cli(
                "validate",
                "--manifest",
                str(path),
                "--repository-root",
                str(REPOSITORY_ROOT),
            )
            self.assertEqual(
                result.returncode,
                course_adapter.EXIT_INVALID_MANIFEST,
            )
            self.assertEqual(result.stdout, "")
            self.assertTrue(result.stderr.startswith("course-adapter: invalid TOML:"))
            self.assertEqual(len(result.stderr.splitlines()), 1)

    def test_invalid_manifest_copies_are_rejected(self) -> None:
        cases = (
            (
                "schema version",
                (('schema_version = "1.0.0"', 'schema_version = "2.0.0"'),),
                "schema_version",
            ),
            (
                "missing path",
                (
                    (
                        'lesson_readme = "lessons/01_basics/README.md"',
                        'lesson_readme = "lessons/01_basics/MISSING.md"',
                    ),
                ),
                "does not exist",
            ),
            (
                "duplicate ID",
                (
                    (
                        'id = "concept.basics.numeric-types-and-conversions"',
                        'id = "concept.basics.hello-world"',
                    ),
                ),
                "duplicate trackable IDs",
            ),
            (
                "dangling prerequisite",
                (
                    (
                        'prerequisites = ["concept.basics.hello-world"]',
                        'prerequisites = ["concept.missing"]',
                    ),
                ),
                "unknown prerequisite",
            ),
            (
                "prerequisite cycle",
                (
                    (
                        "prerequisites = []",
                        'prerequisites = ["module.control-flow"]',
                    ),
                ),
                "prerequisite cycle",
            ),
            (
                "unknown lock",
                (
                    (
                        'solution_lock_group = "solutions.module.basics"',
                        'solution_lock_group = "solutions.missing"',
                    ),
                ),
                "unknown solution lock",
            ),
            (
                "invalid lock policy",
                (
                    (
                        'unlock_policy = "after-unit-validation"',
                        'unlock_policy = "always"',
                    ),
                ),
                "unlock_policy",
            ),
            (
                "unsupported selector",
                (
                    (
                        'learner_value = "starter"',
                        'learner_value = "solution"',
                    ),
                ),
                "selector values",
            ),
            (
                "wrong module command",
                (
                    (
                        'validation_commands = ["python exercises/01_basics/exercises.py"]',
                        'validation_commands = ["python exercises/01_basics/solutions.py"]',
                    ),
                ),
                "validation command",
            ),
        )
        for name, replacements, expected_message in cases:
            with self.subTest(name=name):
                self.assert_invalid_manifest_copy(replacements, expected_message)

    def test_invalid_pedagogical_outcomes_are_rejected(self) -> None:
        first_outcome = '"Run a Python script and bind values to names.",'
        second_outcome = '"Recognize core scalar types and convert input explicitly.",'
        first_milestone = (
            'required_outcome = "Implement Task validation, errors, '
            'service/repository contracts, and the client transport protocol."'
        )
        cases = (
            (
                "missing container outcomes",
                (("required_outcomes = [", "unexpected_outcomes = ["),),
                "required_outcomes must be a non-empty list",
            ),
            (
                "empty container outcomes",
                (
                    (
                        "required_outcomes = [",
                        "required_outcomes = []\nunexpected_outcomes = [",
                    ),
                ),
                "required_outcomes must be a non-empty list",
            ),
            (
                "wrong container field type",
                (
                    (
                        "required_outcomes = [",
                        "required_outcomes = true\nunexpected_outcomes = [",
                    ),
                ),
                "required_outcomes must be a non-empty list",
            ),
            (
                "blank container outcome",
                ((first_outcome, '"   ",'),),
                "required_outcomes must contain non-empty strings",
            ),
            (
                "boolean container outcome",
                ((first_outcome, "true,"),),
                "required_outcomes must contain non-empty strings",
            ),
            (
                "duplicate container outcome",
                ((second_outcome, first_outcome),),
                "required_outcomes must not contain duplicates",
            ),
            (
                "missing milestone outcome",
                (
                    (
                        first_milestone,
                        first_milestone.replace(
                            "required_outcome",
                            "unexpected_outcome",
                            1,
                        ),
                    ),
                ),
                "required_outcome must be a non-empty string",
            ),
            (
                "empty milestone outcome",
                ((first_milestone, 'required_outcome = ""'),),
                "required_outcome must be a non-empty string",
            ),
            (
                "blank milestone outcome",
                ((first_milestone, 'required_outcome = "   "'),),
                "required_outcome must be a non-empty string",
            ),
            (
                "boolean milestone outcome",
                ((first_milestone, "required_outcome = true"),),
                "required_outcome must be a non-empty string",
            ),
        )
        for name, replacements, expected_message in cases:
            with self.subTest(name=name):
                self.assert_invalid_manifest_copy(replacements, expected_message)

    def test_projection_pipes_into_learning_state_init_course(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".course-adapter-pipeline-",
            dir=TESTS_DIR,
        ) as temporary:
            temporary_root = Path(temporary)
            database = temporary_root / "state.sqlite3"
            identity = temporary_root / "course-identity"
            identity.mkdir()

            projection = run_cli("state-projection")
            self.assertEqual(projection.returncode, course_adapter.EXIT_OK)
            initialized = subprocess.run(
                [
                    sys.executable,
                    str(STATE_SCRIPT),
                    "init-course",
                    "--db",
                    str(database),
                    "--local-fallback",
                    str(identity),
                    "--commit",
                    TEST_COMMIT,
                    "--concepts",
                    "-",
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
                input=projection.stdout,
                capture_output=True,
                text=True,
            )

            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            payload = json.loads(initialized.stdout)
            self.assertEqual(payload["concepts"], {"total": 76, "upserted": 76})
            self.assertEqual(payload["course"]["kind"], "local")
            self.assertTrue(database.exists())
            self.assertIn("warning:", initialized.stderr)


if __name__ == "__main__":
    unittest.main()
