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
from typing import Any

TESTS_DIR = Path(__file__).resolve().parent
ADAPTER_DIR = TESTS_DIR.parent
REPOSITORY_ROOT = ADAPTER_DIR.parents[2]
MANIFEST_PATH = ADAPTER_DIR / "course.toml"
ADAPTER_SCRIPT = ADAPTER_DIR / "scripts" / "course_adapter.py"
STATE_SCRIPT = (
    REPOSITORY_ROOT
    / ".agents"
    / "skills"
    / "guided-learning"
    / "scripts"
    / "learning_state.py"
)
DESCRIPTOR_PATH = REPOSITORY_ROOT / ".learning-mentor.toml"
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


def manifest_owners(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every module, project, and capstone in manifest order."""

    return [
        owner
        for owner_kind in ("modules", "projects", "capstones")
        for owner in course_adapter.records(manifest, owner_kind)
    ]


def expected_trackable_count(manifest: dict[str, Any]) -> int:
    """Count every child concept/milestone and its owning container."""

    total = 0
    for owner_kind, child_kind in (
        ("modules", "concepts"),
        ("projects", "milestones"),
        ("capstones", "milestones"),
    ):
        for owner in course_adapter.records(manifest, owner_kind):
            total += len(course_adapter.records(owner, child_kind)) + 1
    return total


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
            course_adapter.SUPPORTED_ADAPTER_PROTOCOL,
            "1",
        )
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

    def test_descriptor_and_native_entrypoints_use_canonical_sources(self) -> None:
        with DESCRIPTOR_PATH.open("rb") as stream:
            descriptor = tomllib.load(stream)
        self.assertEqual(descriptor["schema_version"], 1)
        self.assertEqual(
            descriptor["adapter"],
            {
                "protocol": "1",
                "skill": ".agents/skills/python-learning-path/SKILL.md",
                "command": [
                    "python",
                    ".agents/skills/python-learning-path/scripts/course_adapter.py",
                ],
            },
        )
        self.assertEqual(
            descriptor["state"]["command"],
            [
                "python",
                ".agents/skills/guided-learning/scripts/learning_state.py",
            ],
        )

        links = {
            REPOSITORY_ROOT / ".agents" / "skills" / "guided-learning": (
                REPOSITORY_ROOT / ".learning-mentor" / "skills" / "guided-learning"
            ),
            REPOSITORY_ROOT / ".github" / "agents" / "learning-mentor.agent.md": (
                REPOSITORY_ROOT
                / ".learning-mentor"
                / "agents"
                / "learning-mentor.agent.md"
            ),
            REPOSITORY_ROOT / ".claude" / "agents" / "learning-mentor.md": (
                REPOSITORY_ROOT
                / ".learning-mentor"
                / "agents"
                / "learning-mentor.agent.md"
            ),
            REPOSITORY_ROOT / ".claude" / "skills" / "guided-learning": (
                REPOSITORY_ROOT / ".learning-mentor" / "skills" / "guided-learning"
            ),
            REPOSITORY_ROOT / ".claude" / "skills" / "python-learning-path": (
                REPOSITORY_ROOT / ".agents" / "skills" / "python-learning-path"
            ),
            REPOSITORY_ROOT / ".codex" / "agents" / "learning-mentor.toml": (
                REPOSITORY_ROOT
                / ".learning-mentor"
                / "integrations"
                / "codex"
                / "learning-mentor.toml"
            ),
        }
        for link, target in links.items():
            with self.subTest(link=link):
                self.assertTrue(link.is_symlink())
                self.assertEqual(
                    link.resolve(strict=True),
                    target.resolve(strict=True),
                )

    def test_all_declared_repository_paths_and_review_headings_exist(self) -> None:
        paths = list(course_adapter.declared_paths(self.manifest))
        self.assertGreater(len(paths), 100)
        self.assertEqual(len(paths), len({label for label, _ in paths}))
        course_adapter.validate_paths(self.manifest)

    def test_trackable_ids_are_unique_and_prerequisites_are_acyclic(self) -> None:
        known_ids = course_adapter.validate_trackable_ids_and_graph(self.manifest)
        projected_ids = {concept["id"] for concept in self.projection["concepts"]}
        self.assertEqual(projected_ids, known_ids)
        self.assertEqual(len(known_ids), expected_trackable_count(self.manifest))

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

        by_id = {concept["id"]: concept for concept in concepts}
        parent_positions = {
            concept["id"]: index for index, concept in enumerate(concepts)
        }
        for concept in concepts:
            self.assertTrue(
                all(
                    parent_positions[prerequisite] < parent_positions[concept["id"]]
                    for prerequisite in concept["prerequisites"]
                )
            )

        for module in course_adapter.records(self.manifest, "modules"):
            inherited = course_adapter.prerequisites(module, module["id"])
            for concept in course_adapter.records(
                module,
                "concepts",
                context=module["id"],
            ):
                expected = list(
                    dict.fromkeys(
                        [
                            *inherited,
                            *course_adapter.prerequisites(concept, concept["id"]),
                        ]
                    )
                )
                self.assertEqual(by_id[concept["id"]]["prerequisites"], expected)
            self.assertTrue(
                all(
                    parent_positions[concept["id"]] < parent_positions[module["id"]]
                    for concept in course_adapter.records(
                        module,
                        "concepts",
                        context=module["id"],
                    )
                )
            )
        for owner_kind in ("projects", "capstones"):
            for owner in course_adapter.records(self.manifest, owner_kind):
                inherited = course_adapter.prerequisites(owner, owner["id"])
                for milestone in course_adapter.records(
                    owner,
                    "milestones",
                    context=owner["id"],
                ):
                    expected = list(
                        dict.fromkeys(
                            [
                                *inherited,
                                *course_adapter.prerequisites(
                                    milestone,
                                    milestone["id"],
                                ),
                            ]
                        )
                    )
                    self.assertEqual(
                        by_id[milestone["id"]]["prerequisites"],
                        expected,
                    )
                self.assertTrue(
                    all(
                        parent_positions[milestone["id"]]
                        < parent_positions[owner["id"]]
                        for milestone in course_adapter.records(
                            owner,
                            "milestones",
                            context=owner["id"],
                        )
                    )
                )

    def test_solution_locks_match_declared_owners_and_policy(self) -> None:
        locks = course_adapter.validate_solution_locks(self.manifest)
        self.assertEqual(
            set(locks),
            {owner["solution_lock_group"] for owner in manifest_owners(self.manifest)},
        )
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
        containers = manifest_owners(self.manifest)
        milestones = [
            milestone
            for owner_kind in ("projects", "capstones")
            for owner in course_adapter.records(self.manifest, owner_kind)
            for milestone in course_adapter.records(
                owner,
                "milestones",
                context=owner["id"],
            )
        ]
        self.assertGreater(len(containers), 0)
        self.assertGreater(len(milestones), 0)

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
            "adapter_protocol": "1",
            "manifest_version": 1,
            "schema_version": "1.0.0",
            "status": "valid",
            "trackable_count": expected_trackable_count(self.manifest),
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
                        'lesson_readme = "lessons/01_python_fundamentals/README.md"',
                        'lesson_readme = "lessons/01_python_fundamentals/MISSING.md"',
                    ),
                ),
                "does not exist",
            ),
            (
                "duplicate ID",
                (
                    (
                        'id = "concept.python-fundamentals.conversion-and-truthiness"',
                        'id = "concept.python-fundamentals.running-scripts"',
                    ),
                ),
                "duplicate trackable IDs",
            ),
            (
                "dangling prerequisite",
                (
                    (
                        'prerequisites = ["concept.python-fundamentals.running-scripts"]',
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
                        'prerequisites = ["module.text-and-numbers"]',
                    ),
                ),
                "prerequisite cycle",
            ),
            (
                "unknown lock",
                (
                    (
                        'solution_lock_group = "solutions.module.python-fundamentals"',
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
                        'validation_commands = ["python exercises/01_python_fundamentals/exercises.py"]',
                        'validation_commands = ["python exercises/01_python_fundamentals/solutions.py"]',
                    ),
                ),
                "validation command",
            ),
        )
        for name, replacements, expected_message in cases:
            with self.subTest(name=name):
                self.assert_invalid_manifest_copy(replacements, expected_message)

    def test_invalid_pedagogical_outcomes_are_rejected(self) -> None:
        first_outcome = (
            '"Run a Python script from the repository root and read its output.",'
        )
        second_outcome = '"Recognize core scalar types (str, int, float, bool, None) and their literals.",'
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
            expected_count = expected_trackable_count(self.manifest)
            self.assertEqual(
                payload["concepts"],
                {"total": expected_count, "upserted": expected_count},
            )
            self.assertEqual(payload["course"]["kind"], "local")
            self.assertTrue(database.exists())
            self.assertIn("warning:", initialized.stderr)


if __name__ == "__main__":
    unittest.main()
