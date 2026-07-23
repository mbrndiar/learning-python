#!/usr/bin/env python3
"""Validate the Python learning path and project it into mentor state JSON."""

from __future__ import annotations

import argparse
import heapq
import json
import re
import shlex
import sys
import tomllib
from collections import Counter
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any, TextIO

SCRIPT_PATH = Path(__file__).resolve()
ADAPTER_DIR = SCRIPT_PATH.parents[1]
REPOSITORY_ROOT = ADAPTER_DIR.parents[2]
MANIFEST_PATH = ADAPTER_DIR / "course.toml"
SKILL_RELATIVE_PATH = Path(".agents/skills/python-learning-path/SKILL.md")

SUPPORTED_ADAPTER_PROTOCOL = "1"
SUPPORTED_MANIFEST_VERSION = 1
SUPPORTED_SCHEMA_VERSION = "1.0.0"
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
SELECTOR_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_INVALID_MANIFEST = 3
EXIT_IO = 4


class ManifestValidationError(ValueError):
    """Raised when the course manifest violates the adapter contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestValidationError(message)


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    with path.open("rb") as manifest_file:
        return tomllib.load(manifest_file)


def records(
    container: dict[str, Any],
    key: str,
    *,
    context: str = "manifest",
) -> list[dict[str, Any]]:
    value = container.get(key)
    require(isinstance(value, list), f"{context}.{key} must be an array")
    require(
        all(isinstance(item, dict) for item in value),
        f"{context}.{key} entries must be tables",
    )
    return value


def prerequisites(record: dict[str, Any], record_id: str) -> list[str]:
    value = record.get("prerequisites")
    require(
        isinstance(value, list)
        and all(isinstance(item, str) and item for item in value),
        f"{record_id} prerequisites must be string IDs",
    )
    require(
        len(value) == len(set(value)),
        f"{record_id} prerequisites must be unique",
    )
    require(record_id not in value, f"{record_id} cannot require itself")
    return value


def trackable_records(
    manifest: dict[str, Any],
) -> list[tuple[str, dict[str, Any], dict[str, Any] | None]]:
    result: list[tuple[str, dict[str, Any], dict[str, Any] | None]] = []
    for module in records(manifest, "modules"):
        result.append(("module", module, None))
        for concept in records(
            module,
            "concepts",
            context=str(module.get("id", "module")),
        ):
            result.append(("concept", concept, module))
    for project in records(manifest, "projects"):
        result.append(("project", project, None))
        for milestone in records(
            project,
            "milestones",
            context=str(project.get("id", "project")),
        ):
            result.append(("milestone", milestone, project))
    for capstone in records(manifest, "capstones"):
        result.append(("capstone", capstone, None))
        for milestone in records(
            capstone,
            "milestones",
            context=str(capstone.get("id", "capstone")),
        ):
            result.append(("milestone", milestone, capstone))
    return result


def validate_versions(manifest: dict[str, Any]) -> None:
    require(
        manifest.get("manifest_version") == SUPPORTED_MANIFEST_VERSION,
        f"unsupported manifest_version: {manifest.get('manifest_version')!r}",
    )
    require(
        manifest.get("schema_version") == SUPPORTED_SCHEMA_VERSION,
        f"unsupported schema_version: {manifest.get('schema_version')!r}",
    )
    course = manifest.get("course")
    require(isinstance(course, dict), "course must be a table")
    require(course.get("minimum_python") == "3.11", "minimum Python must be 3.11")
    require(course.get("maximum_python") == "3.14", "maximum Python must be 3.14")
    require(
        course.get("requires_python") == ">=3.11,<3.15",
        "requires_python must cover Python 3.11 through 3.14",
    )
    require(
        course.get("command_working_directory") == ".",
        "course commands must run from the repository root",
    )


def validate_trackable_ids_and_graph(manifest: dict[str, Any]) -> set[str]:
    entries = trackable_records(manifest)
    ids: list[str] = []
    expected_prefix = {
        "module": "module.",
        "concept": "concept.",
        "project": "project.",
        "milestone": "milestone.",
        "capstone": "capstone.",
    }
    for kind, record, _ in entries:
        record_id = record.get("id")
        require(
            isinstance(record_id, str) and ID_PATTERN.fullmatch(record_id) is not None,
            f"{kind} has an invalid id: {record_id!r}",
        )
        require(
            record_id.startswith(expected_prefix[kind]),
            f"{record_id} must use the {expected_prefix[kind]} prefix",
        )
        title = record.get("title")
        require(
            isinstance(title, str) and title.strip(),
            f"{record_id} must have a title",
        )
        prerequisites(record, record_id)
        ids.append(record_id)

    duplicates = sorted(
        record_id for record_id, count in Counter(ids).items() if count > 1
    )
    require(not duplicates, f"duplicate trackable IDs: {', '.join(duplicates)}")
    known_ids = set(ids)
    for _, record, _ in entries:
        record_id = record["id"]
        for prerequisite in prerequisites(record, record_id):
            require(
                prerequisite in known_ids,
                f"{record_id} has unknown prerequisite {prerequisite}",
            )

    modules = records(manifest, "modules")
    require(
        [module.get("ordinal") for module in modules]
        == list(range(1, len(modules) + 1)),
        "module ordinals must be unique, sequential, and manifest ordered",
    )
    for owner_kind in ("projects", "capstones"):
        for owner in records(manifest, owner_kind):
            milestones = records(
                owner,
                "milestones",
                context=str(owner["id"]),
            )
            require(
                [milestone.get("ordinal") for milestone in milestones]
                == list(range(1, len(milestones) + 1)),
                f"{owner['id']} milestone ordinals must be sequential",
            )

    course = manifest["course"]
    final_destinations = course.get("final_destinations")
    require(
        isinstance(final_destinations, list) and final_destinations,
        "course.final_destinations must be a non-empty array",
    )
    for destination in final_destinations:
        require(isinstance(destination, dict), "final destinations must be tables")
        destination_id = destination.get("id")
        require(
            destination_id in known_ids
            and isinstance(destination_id, str)
            and destination_id.startswith("capstone."),
            f"unknown final destination {destination_id!r}",
        )
        require(
            destination.get("required") is True,
            f"{destination_id} must be required",
        )
    return known_ids


def validate_required_outcomes(manifest: dict[str, Any]) -> None:
    for owner_kind in ("modules", "projects", "capstones"):
        for owner in records(manifest, owner_kind):
            owner_id = owner["id"]
            outcomes = owner.get("required_outcomes")
            require(
                isinstance(outcomes, list) and outcomes,
                f"{owner_id}.required_outcomes must be a non-empty list",
            )
            require(
                all(
                    isinstance(outcome, str) and outcome.strip() for outcome in outcomes
                ),
                f"{owner_id}.required_outcomes must contain non-empty strings",
            )
            normalized_outcomes = [outcome.strip() for outcome in outcomes]
            require(
                len(normalized_outcomes) == len(set(normalized_outcomes)),
                f"{owner_id}.required_outcomes must not contain duplicates",
            )

            if owner_kind == "modules":
                continue
            for milestone in records(owner, "milestones", context=owner_id):
                milestone_id = milestone["id"]
                outcome = milestone.get("required_outcome")
                require(
                    isinstance(outcome, str) and outcome.strip(),
                    f"{milestone_id}.required_outcome must be a non-empty string",
                )


def declared_paths(manifest: dict[str, Any]) -> Iterator[tuple[str, object]]:
    yield "schema_document", manifest.get("schema_document")
    course = manifest["course"]
    for key in ("learner_entry_point", "setup_guide", "command_working_directory"):
        yield f"course.{key}", course.get(key)
    for index, destination in enumerate(course["final_destinations"]):
        yield f"course.final_destinations[{index}].path", destination.get("path")

    for module in records(manifest, "modules"):
        module_id = module["id"]
        for key in ("lesson_readme", "exercise_starter", "exercise_solution"):
            yield f"{module_id}.{key}", module.get(key)
        solution_supplements = module.get("solution_supplements", [])
        require(
            isinstance(solution_supplements, list),
            f"{module_id}.solution_supplements must be an array",
        )
        for index, path in enumerate(solution_supplements):
            yield f"{module_id}.solution_supplements[{index}]", path
        review_questions = module.get("review_questions")
        require(
            isinstance(review_questions, dict),
            f"{module_id}.review_questions must be a table",
        )
        yield f"{module_id}.review_questions.path", review_questions.get("path")
        for concept in records(module, "concepts", context=module_id):
            yield f"{concept['id']}.lesson_file", concept.get("lesson_file")

    for owner_kind in ("projects", "capstones"):
        for owner in records(manifest, owner_kind):
            owner_id = owner["id"]
            for key in ("guide_path", "starter_root", "solution_root", "tests_root"):
                yield f"{owner_id}.{key}", owner.get(key)
            specification_paths = owner.get("specification_paths")
            require(
                isinstance(specification_paths, list) and specification_paths,
                f"{owner_id}.specification_paths must be a non-empty array",
            )
            for index, path in enumerate(specification_paths):
                yield f"{owner_id}.specification_paths[{index}]", path

    for lock in records(manifest, "solution_lock_groups"):
        lock_paths = lock.get("paths")
        require(
            isinstance(lock_paths, list) and lock_paths,
            f"{lock.get('id', 'solution lock')}.paths must be non-empty",
        )
        for index, path in enumerate(lock_paths):
            yield f"{lock['id']}.paths[{index}]", path


def path_declaration(label: str, value: object) -> tuple[str, str]:
    if isinstance(value, str):
        require(value != "", f"{label} must not be empty")
        return value, "repository"
    require(isinstance(value, dict), f"{label} must be a path string or table")
    path = value.get("path")
    availability = value.get("availability")
    require(isinstance(path, str) and path, f"{label}.path must be a string")
    require(
        availability in {"repository", "command-created"},
        f"{label}.availability is unsupported",
    )
    if availability == "command-created":
        require(
            isinstance(value.get("created_by"), str) and value["created_by"],
            f"{label}.created_by must name a command",
        )
    return path, availability


def validate_paths(manifest: dict[str, Any], root: Path = REPOSITORY_ROOT) -> None:
    resolved_root = root.resolve()
    for label, value in declared_paths(manifest):
        raw_path, availability = path_declaration(label, value)
        relative_path = Path(raw_path)
        require(not relative_path.is_absolute(), f"{label} must be repository relative")
        resolved_path = (resolved_root / relative_path).resolve()
        try:
            resolved_path.relative_to(resolved_root)
        except ValueError as error:
            raise ManifestValidationError(
                f"{label} escapes the repository root: {raw_path}"
            ) from error
        if availability == "repository":
            require(resolved_path.exists(), f"{label} does not exist: {raw_path}")

    for module in records(manifest, "modules"):
        review_questions = module["review_questions"]
        heading = review_questions.get("heading")
        require(
            isinstance(heading, str) and heading.strip(),
            f"{module['id']} review heading must be named",
        )
        review_path, _ = path_declaration(
            f"{module['id']}.review_questions.path",
            review_questions["path"],
        )
        review_text = (root / review_path).read_text(encoding="utf-8")
        require(
            any(
                line.startswith("#") and line.lstrip("#").strip() == heading
                for line in review_text.splitlines()
            ),
            f"{module['id']} review heading is missing from {review_path}",
        )


def validate_solution_locks(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lock_records = records(manifest, "solution_lock_groups")
    lock_ids = [lock.get("id") for lock in lock_records]
    require(
        all(
            isinstance(lock_id, str)
            and lock_id.startswith("solutions.")
            and ID_PATTERN.fullmatch(lock_id) is not None
            for lock_id in lock_ids
        ),
        "solution lock IDs are invalid",
    )
    duplicates = sorted(
        str(lock_id) for lock_id, count in Counter(lock_ids).items() if count > 1
    )
    require(not duplicates, f"duplicate solution lock IDs: {', '.join(duplicates)}")
    locks = {lock["id"]: lock for lock in lock_records}

    owners: list[tuple[dict[str, Any], list[str], str]] = []
    owners.extend(
        (
            module,
            [module["exercise_solution"], *module.get("solution_supplements", [])],
            "after-unit-validation",
        )
        for module in records(manifest, "modules")
    )
    for owner_kind in ("projects", "capstones"):
        owners.extend(
            (
                owner,
                [owner["solution_root"]],
                "after-matching-milestone-validation",
            )
            for owner in records(manifest, owner_kind)
        )

    referenced_locks: list[str] = []
    locked_paths: list[str] = []
    for owner, expected_paths, expected_policy in owners:
        owner_id = owner["id"]
        lock_id = owner.get("solution_lock_group")
        require(
            isinstance(lock_id, str) and lock_id in locks,
            f"{owner_id} references unknown solution lock {lock_id!r}",
        )
        referenced_locks.append(lock_id)
        lock = locks[lock_id]
        lock_paths = [
            path_declaration(f"{lock_id}.paths", path)[0] for path in lock["paths"]
        ]
        require(
            lock_paths == expected_paths,
            f"{lock_id} must lock exactly {', '.join(expected_paths)}",
        )
        locked_paths.extend(lock_paths)
        require(
            lock.get("unlock_policy") == expected_policy,
            f"{lock_id} has an invalid unlock_policy",
        )
        unlock_after = lock.get("solution_unlock_after")
        require(
            type(unlock_after) is int and 1 <= unlock_after <= 100,
            f"{lock_id} solution_unlock_after must be between 1 and 100",
        )

    require(
        len(referenced_locks) == len(set(referenced_locks)),
        "solution lock groups must not be shared by owners",
    )
    require(
        set(referenced_locks) == set(locks),
        "solution lock groups must be referenced exactly once",
    )
    require(
        len(locked_paths) == len(set(locked_paths)),
        "solution paths must belong to one lock group",
    )
    return locks


def validate_command_text(label: str, command: object) -> str:
    require(isinstance(command, str), f"{label} must be a string")
    require(command == command.strip() and command, f"{label} must not be blank")
    require(
        not any(character in command for character in ("\n", "\r", "\0")),
        f"{label} must be one line",
    )
    try:
        shlex.split(command)
    except ValueError as error:
        raise ManifestValidationError(f"{label} is not valid shell syntax") from error
    return command


def validate_commands_and_selectors(
    manifest: dict[str, Any],
    root: Path = REPOSITORY_ROOT,
) -> None:
    skill_text = (root / SKILL_RELATIVE_PATH).read_text(encoding="utf-8")
    for module in records(manifest, "modules"):
        module_id = module["id"]
        commands = module.get("validation_commands")
        expected_command = f"python {module['exercise_starter']}"
        require(
            commands == [expected_command],
            f"{module_id} validation command must target its exercise starter",
        )
        validate_command_text(f"{module_id}.validation_commands[0]", expected_command)
        require(
            f"`{expected_command}`" in skill_text,
            f"{module_id} validation command is not documented in SKILL.md",
        )
        for concept in records(module, "concepts", context=module_id):
            command = validate_command_text(
                f"{concept['id']}.run_command",
                concept.get("run_command"),
            )
            tokens = shlex.split(command)
            require(tokens[0] == "python", f"{concept['id']} must use python")
            require(
                concept["lesson_file"] in tokens,
                f"{concept['id']} run command must target its lesson file",
            )

    for owner_kind in ("projects", "capstones"):
        for owner in records(manifest, owner_kind):
            owner_id = owner["id"]
            selector = owner.get("implementation_selector")
            require(
                isinstance(selector, dict),
                f"{owner_id}.implementation_selector must be a table",
            )
            environment = selector.get("environment")
            learner_value = selector.get("learner_value")
            reference_value = selector.get("reference_value")
            default_value = selector.get("default_value")
            require(
                isinstance(environment, str)
                and SELECTOR_PATTERN.fullmatch(environment) is not None,
                f"{owner_id} selector environment is invalid",
            )
            require(
                (learner_value, reference_value, default_value)
                == ("starter", "solution", "solution"),
                f"{owner_id} selector values are unsupported",
            )
            require(
                owner["starter_root"].endswith(f"/{learner_value}")
                and owner["solution_root"].endswith(f"/{reference_value}"),
                f"{owner_id} selector values do not match implementation roots",
            )
            learner_assignment = f"{environment}={learner_value}"
            require(
                f"`{learner_assignment}`" in skill_text,
                f"{owner_id} learner selector is not documented in SKILL.md",
            )

            validation_commands = owner.get("validation_commands")
            require(
                isinstance(validation_commands, list) and validation_commands,
                f"{owner_id}.validation_commands must be non-empty",
            )
            for index, command in enumerate(validation_commands):
                validate_command_text(
                    f"{owner_id}.validation_commands[{index}]",
                    command,
                )
            require(
                any(
                    command.startswith(f"{learner_assignment} ")
                    for command in validation_commands
                ),
                f"{owner_id} must validate the learner-selected implementation",
            )

            for milestone in records(owner, "milestones", context=owner_id):
                command = validate_command_text(
                    f"{milestone['id']}.test_command",
                    milestone.get("test_command"),
                )
                require(
                    command.startswith(f"{learner_assignment} "),
                    f"{milestone['id']} must select learner code explicitly",
                )
                require(
                    owner["tests_root"] in command,
                    f"{milestone['id']} must target {owner['tests_root']}",
                )
                require(
                    f"`{command}`" in skill_text,
                    f"{milestone['id']} command is not documented in SKILL.md",
                )


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def flatten_state_projection(manifest: dict[str, Any]) -> dict[str, object]:
    locks = validate_solution_locks(manifest)
    nodes: list[dict[str, Any]] = []

    def add_node(
        record: dict[str, Any],
        *,
        inherited_prerequisites: list[str] | None = None,
        lock_id: str,
    ) -> None:
        inherited = [] if inherited_prerequisites is None else inherited_prerequisites
        node_prerequisites = unique([*inherited, *prerequisites(record, record["id"])])
        nodes.append(
            {
                "id": record["id"],
                "title": record["title"],
                "prerequisites": node_prerequisites,
                "solution_unlock_after": locks[lock_id]["solution_unlock_after"],
                "_rank": len(nodes),
            }
        )

    for module in sorted(
        records(manifest, "modules"), key=lambda item: item["ordinal"]
    ):
        inherited = prerequisites(module, module["id"])
        for concept in sorted(
            records(module, "concepts", context=module["id"]),
            key=lambda item: item["id"],
        ):
            add_node(
                concept,
                inherited_prerequisites=inherited,
                lock_id=module["solution_lock_group"],
            )
        add_node(module, lock_id=module["solution_lock_group"])

    for project in sorted(records(manifest, "projects"), key=lambda item: item["id"]):
        inherited = prerequisites(project, project["id"])
        for milestone in sorted(
            records(project, "milestones", context=project["id"]),
            key=lambda item: (item["ordinal"], item["id"]),
        ):
            add_node(
                milestone,
                inherited_prerequisites=inherited,
                lock_id=project["solution_lock_group"],
            )
        add_node(project, lock_id=project["solution_lock_group"])

    for capstone in sorted(records(manifest, "capstones"), key=lambda item: item["id"]):
        inherited = prerequisites(capstone, capstone["id"])
        for milestone in sorted(
            records(capstone, "milestones", context=capstone["id"]),
            key=lambda item: (item["ordinal"], item["id"]),
        ):
            add_node(
                milestone,
                inherited_prerequisites=inherited,
                lock_id=capstone["solution_lock_group"],
            )
        add_node(capstone, lock_id=capstone["solution_lock_group"])

    by_id = {node["id"]: node for node in nodes}
    require(len(by_id) == len(nodes), "projection contains duplicate trackable IDs")
    dependents: dict[str, list[str]] = {record_id: [] for record_id in by_id}
    indegrees: dict[str, int] = {}
    for node in nodes:
        node_id = node["id"]
        indegrees[node_id] = len(node["prerequisites"])
        for prerequisite in node["prerequisites"]:
            require(
                prerequisite in by_id,
                f"{node_id} has unknown prerequisite {prerequisite}",
            )
            dependents[prerequisite].append(node_id)

    ready = [
        (node["_rank"], node["id"]) for node in nodes if indegrees[node["id"]] == 0
    ]
    heapq.heapify(ready)
    ordered_ids: list[str] = []
    while ready:
        _, node_id = heapq.heappop(ready)
        ordered_ids.append(node_id)
        for dependent in dependents[node_id]:
            indegrees[dependent] -= 1
            if indegrees[dependent] == 0:
                dependent_node = by_id[dependent]
                heapq.heappush(ready, (dependent_node["_rank"], dependent))

    if len(ordered_ids) != len(nodes):
        cycle_ids = sorted(
            node_id for node_id, degree in indegrees.items() if degree > 0
        )
        raise ManifestValidationError(
            f"prerequisite cycle detected involving: {', '.join(cycle_ids)}"
        )

    projected: list[dict[str, object]] = []
    for index, node_id in enumerate(ordered_ids, start=1):
        node = by_id[node_id]
        projected.append(
            {
                "id": node_id,
                "title": node["title"],
                "order": index * 10,
                "prerequisites": node["prerequisites"],
                "solution_unlock_after": node["solution_unlock_after"],
            }
        )
    return {"concepts": projected}


def validate_manifest(
    manifest: dict[str, Any],
    root: Path = REPOSITORY_ROOT,
) -> dict[str, object]:
    try:
        validate_versions(manifest)
        validate_trackable_ids_and_graph(manifest)
        validate_required_outcomes(manifest)
        validate_paths(manifest, root)
        validate_solution_locks(manifest)
        validate_commands_and_selectors(manifest, root)
        return flatten_state_projection(manifest)
    except ManifestValidationError:
        raise
    except (KeyError, TypeError) as error:
        raise ManifestValidationError(
            f"missing or invalid required field: {error}"
        ) from error


def compact_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="course-adapter")

    def add_source_options(target: argparse.ArgumentParser) -> None:
        target.add_argument(
            "--manifest",
            type=Path,
            default=argparse.SUPPRESS,
            help="course manifest path",
        )
        target.add_argument(
            "--repository-root",
            type=Path,
            default=argparse.SUPPRESS,
            help="repository root used to resolve manifest paths",
        )

    add_source_options(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser(
        "validate",
        help="validate the course manifest",
    )
    projection_parser = subparsers.add_parser(
        "state-projection",
        help="emit state-helper concepts JSON",
    )
    add_source_options(validate_parser)
    add_source_options(projection_parser)
    return parser


def run(
    arguments: argparse.Namespace,
    *,
    stdout: TextIO,
) -> None:
    manifest_path = getattr(arguments, "manifest", MANIFEST_PATH)
    repository_root = getattr(arguments, "repository_root", REPOSITORY_ROOT)
    manifest = load_manifest(manifest_path)
    projection = validate_manifest(manifest, repository_root)
    if arguments.command == "validate":
        payload: object = {
            "adapter_protocol": SUPPORTED_ADAPTER_PROTOCOL,
            "manifest_version": manifest["manifest_version"],
            "schema_version": manifest["schema_version"],
            "status": "valid",
            "trackable_count": len(projection["concepts"]),
        }
    else:
        payload = projection
    stdout.write(f"{compact_json(payload)}\n")


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    output = sys.stdout if stdout is None else stdout
    errors = sys.stderr if stderr is None else stderr
    arguments = build_parser().parse_args(argv)
    try:
        run(arguments, stdout=output)
    except tomllib.TOMLDecodeError as error:
        print(f"course-adapter: invalid TOML: {error}", file=errors)
        return EXIT_INVALID_MANIFEST
    except ManifestValidationError as error:
        print(f"course-adapter: invalid manifest: {error}", file=errors)
        return EXIT_INVALID_MANIFEST
    except OSError as error:
        print(f"course-adapter: I/O error: {error}", file=errors)
        return EXIT_IO
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
