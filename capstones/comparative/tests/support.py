"""Fixture-driven conformance support for the frozen comparative contract.

Sequential scenarios apply an ordered series of commands and database checks to
one isolated store.  Multiprocess scenarios instead coordinate independently
owned children and assert aggregate outcomes that remain valid across permitted
nondeterministic interleavings.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import time
import unittest
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from implementation import SOURCE_ROOT

TEST_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TEST_ROOT.parents[2]
SPEC_ROOT = TEST_ROOT.parent / "spec"
FIXTURE_ROOT = SPEC_ROOT / "fixtures"
SCENARIO_ROOT = FIXTURE_ROOT / "scenarios"
SPEC_VERSION = (SPEC_ROOT / "SPEC_VERSION").read_text(encoding="utf-8").strip()
BARRIER_ACTOR = TEST_ROOT / "_barrier_actor.py"
LOCK_HELPER = TEST_ROOT / "_lock_helper.py"
SAFE_INTEGER_MAXIMUM = 9_007_199_254_740_991


@dataclass(frozen=True, slots=True)
class ProcessResult:
    """A completed process observation, including elapsed wall-clock time.

    ``duration_ms`` includes launch, waiting, and teardown seen by the parent; it
    is not child CPU time and is used only for explicit timing contracts.
    """

    args: tuple[str, ...]
    stdout: bytes
    stderr: bytes
    exit_code: int
    duration_ms: float


@dataclass(slots=True)
class RunningProcess:
    """A child process owned by the harness until awaited or terminated.

    Keeping the arguments and start/release timestamp beside ``Popen`` lets every
    completion path produce the same diagnostic and wall-clock result.
    """

    args: tuple[str, ...]
    process: subprocess.Popen[bytes]
    started: float


def load_fixture(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain one JSON object")
    if value.get("spec_version") != SPEC_VERSION:
        raise AssertionError(f"{path} does not target spec {SPEC_VERSION}")
    return value


@contextmanager
def test_directory() -> Iterator[Path]:
    """Give one scenario an isolated cwd-independent database location.

    Repository-local storage keeps child-process paths predictable, while a new
    directory per use prevents database, journal, or ready files leaking between
    fixture cases.
    """

    with TemporaryDirectory(prefix=".comparative-test-", dir=TEST_ROOT) as directory:
        yield Path(directory)


def generated_value(case: Mapping[str, object]) -> tuple[str, object]:
    generator = case.get("input_generator")
    if generator is None:
        return str(case["input_json"]), case.get("normalized")
    if not isinstance(generator, dict):
        raise AssertionError("input_generator must be an object")
    kind = generator.get("kind")
    if kind == "nested_arrays":
        depth = int(generator["depth"])
        leaf = generator.get("leaf")
        text = "[" * depth + json.dumps(leaf, separators=(",", ":")) + "]" * depth
        value: object = leaf
        for _ in range(depth):
            value = [value]
        return text, value
    if kind == "ascii_string_total_bytes":
        total = int(generator["total_bytes"])
        character = str(generator["character"])
        text = '"' + character * (total - 2) + '"'
        if len(text.encode("utf-8")) != total:
            raise AssertionError("generated JSON did not have its claimed byte length")
        return text, character * (total - 2)
    raise AssertionError(f"unknown value generator {kind!r}")


def generated_key(case: Mapping[str, object]) -> str:
    generator = case.get("key_generator")
    if generator is None:
        return str(case["key"])
    if not isinstance(generator, dict) or generator.get("kind") != "repeat_suffix":
        raise AssertionError("unknown key generator")
    return str(generator["prefix"]) + str(generator["character"]) * int(
        generator["count"]
    )


def run_cli(args: Sequence[str], timeout: float = 15.0) -> ProcessResult:
    """Run one CLI with the suite's fixed working directory and environment."""

    command = [*_program(), *args]
    started = time.monotonic()
    try:
        process = subprocess.run(
            command,
            # A stable cwd ensures behavior cannot depend on the test runner's
            # launch directory; explicit database paths still isolate storage.
            cwd=REPOSITORY_ROOT,
            # In particular, PYTHONPATH selects the same implementation root as
            # the in-process imports and PYTHONIOENCODING fixes wire encoding.
            env=_environment(),
            check=False,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise AssertionError(f"CLI timed out for {list(args)!r}") from error
    return ProcessResult(
        tuple(args),
        process.stdout,
        process.stderr,
        process.returncode,
        (time.monotonic() - started) * 1000,
    )


def assert_process(
    case: unittest.TestCase,
    result: ProcessResult,
    expected: Mapping[str, object],
) -> dict[str, object]:
    case.assertEqual(result.exit_code, expected["exit"], result)
    case.assertEqual(result.stderr, str(expected.get("stderr", "")).encode())
    envelope = decode_stdout(case, result.stdout)
    if "stdout" in expected:
        case.assertEqual(envelope, expected["stdout"])
    return envelope


def decode_stdout(
    case: unittest.TestCase,
    stdout: bytes,
) -> dict[str, object]:
    """Decode the exact one-line, compact, restricted-JSON output contract."""

    case.assertFalse(stdout.startswith(b"\xef\xbb\xbf"))
    case.assertTrue(stdout.endswith(b"\n"), stdout)
    case.assertEqual(stdout.count(b"\n"), 1, stdout)
    text = stdout[:-1].decode("utf-8")
    _assert_compact_json(case, text)

    def parse_integer(token: str) -> int:
        value = int(token)
        case.assertLessEqual(abs(value), SAFE_INTEGER_MAXIMUM)
        case.assertEqual(token, str(value))
        return value

    def reject_number(token: str) -> object:
        raise AssertionError(f"output contained non-integral number {token!r}")

    value = json.loads(
        text,
        parse_int=parse_integer,
        parse_float=reject_number,
        parse_constant=reject_number,
    )
    case.assertIsInstance(value, dict)
    return value


def _assert_compact_json(case: unittest.TestCase, text: str) -> None:
    """Reject insignificant whitespace without rejecting whitespace in strings."""

    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        else:
            case.assertNotIn(character, " \t\r\n")


def run_sequential_fixture(case: unittest.TestCase, name: str) -> None:
    """Run fixture steps in order against a fresh store per scenario.

    This path proves command-to-command conformance and persistent transitions;
    process contention is intentionally delegated to the multiprocess runner.
    """

    fixture = load_fixture(SCENARIO_ROOT / name)
    case.assertEqual(fixture["kind"], "sequential_scenarios")
    scenarios = fixture["scenarios"]
    assert isinstance(scenarios, list)
    for scenario_value in scenarios:
        assert isinstance(scenario_value, dict)
        with case.subTest(scenario=scenario_value["id"]):
            _run_sequential_scenario(case, scenario_value)


def _run_sequential_scenario(
    case: unittest.TestCase,
    scenario: Mapping[str, object],
) -> None:
    with test_directory() as directory:
        database = directory / "store.db"
        missing_parent = directory / "missing" / "store.db"
        if scenario["database"] == "sqlite_setup":
            setup = scenario["setup"]
            assert isinstance(setup, dict)
            _sqlite_setup(database, setup)
        steps = scenario["steps"]
        assert isinstance(steps, list)
        for step in steps:
            assert isinstance(step, dict)
            if "run" in step:
                run = step["run"]
                expected = step["expect"]
                assert isinstance(run, dict) and isinstance(expected, dict)
                args = _substitute_args(
                    run["args"],
                    database,
                    missing_parent,
                )
                assert_process(case, run_cli(args), expected)
            elif "sqlite_assert" in step:
                assertion = step["sqlite_assert"]
                assert isinstance(assertion, dict)
                _assert_sqlite(case, database, assertion)
            elif "fixture_references" in step:
                references = step["fixture_references"]
                assert isinstance(references, list)
                for reference in references:
                    _run_reference_fixture(case, str(reference))
            else:
                raise AssertionError(f"unknown sequential step {step!r}")
        _assert_integrity(case, database)
        _cleanup_database(database)


def _run_reference_fixture(case: unittest.TestCase, reference: str) -> None:
    name = Path(reference).name
    if name == "keys.json":
        run_key_fixtures(case)
    elif name == "values-accepted.json":
        run_accepted_value_fixtures(case)
    elif name == "values-rejected.json":
        run_rejected_value_fixtures(case)
    else:
        raise AssertionError(f"unknown fixture reference {reference!r}")


def run_key_fixtures(case: unittest.TestCase) -> None:
    fixture = load_fixture(FIXTURE_ROOT / "keys.json")
    accepted = fixture["accepted"]
    rejected = fixture["rejected"]
    ordering = fixture["ordering"]
    assert isinstance(accepted, list)
    assert isinstance(rejected, list)
    assert isinstance(ordering, list)
    for item in accepted:
        assert isinstance(item, dict)
        with case.subTest(key_case=item["id"]):
            with test_directory() as directory:
                database = directory / "store.db"
                key = generated_key(item)
                set_result = run_cli(
                    [
                        "--db",
                        str(database),
                        "set",
                        key,
                        "--value-json",
                        "null",
                        "--expect",
                        "absent",
                    ]
                )
                envelope = assert_process(
                    case,
                    set_result,
                    {
                        "exit": 0,
                        "stderr": "",
                        "stdout": {
                            "ok": True,
                            "result": {
                                "key": key,
                                "value": None,
                                "revision": 1,
                                "created": True,
                            },
                        },
                    },
                )
                case.assertTrue(envelope["ok"])
                assert_process(
                    case,
                    run_cli(["--db", str(database), "get", key]),
                    {
                        "exit": 0,
                        "stderr": "",
                        "stdout": {
                            "ok": True,
                            "result": {
                                "key": key,
                                "value": None,
                                "revision": 1,
                            },
                        },
                    },
                )
                _cleanup_database(database)
    for item in rejected:
        assert isinstance(item, dict)
        with case.subTest(key_case=item["id"]):
            with test_directory() as directory:
                database = directory / "store.db"
                key = generated_key(item)
                assert_process(
                    case,
                    run_cli(["--db", str(database), "get", key]),
                    {
                        "exit": 2,
                        "stderr": "",
                        "stdout": {
                            "ok": False,
                            "error": {
                                "category": "invalid_argument",
                                "details": {"field": "key", "reason": "format"},
                            },
                        },
                    },
                )
                case.assertFalse(database.exists())

    with test_directory() as directory:
        database = directory / "store.db"
        for key_value in reversed(ordering):
            key = str(key_value)
            result = run_cli(
                [
                    "--db",
                    str(database),
                    "set",
                    key,
                    "--value-json",
                    json.dumps(key),
                ]
            )
            case.assertEqual(result.exit_code, 0, result)
        listed = assert_process(
            case,
            run_cli(["--db", str(database), "list"]),
            {"exit": 0, "stderr": ""},
        )
        result = listed["result"]
        assert isinstance(result, dict)
        entries = result["entries"]
        assert isinstance(entries, list)
        case.assertEqual([entry["key"] for entry in entries], ordering)
        _cleanup_database(database)


def run_accepted_value_fixtures(case: unittest.TestCase) -> None:
    fixture = load_fixture(FIXTURE_ROOT / "values-accepted.json")
    cases = fixture["cases"]
    assert isinstance(cases, list)
    for item in cases:
        assert isinstance(item, dict)
        with case.subTest(value_case=item["id"]):
            text, generated_normalized = generated_value(item)
            normalized = (
                item["normalized"] if "normalized" in item else generated_normalized
            )
            with test_directory() as directory:
                database = directory / "store.db"
                expected_entry = {
                    "key": "value",
                    "value": normalized,
                    "revision": 1,
                }
                assert_process(
                    case,
                    run_cli(
                        [
                            "--db",
                            str(database),
                            "set",
                            "value",
                            "--value-json",
                            text,
                            "--expect",
                            "absent",
                        ]
                    ),
                    {
                        "exit": 0,
                        "stderr": "",
                        "stdout": {
                            "ok": True,
                            "result": {**expected_entry, "created": True},
                        },
                    },
                )
                assert_process(
                    case,
                    run_cli(["--db", str(database), "get", "value"]),
                    {
                        "exit": 0,
                        "stderr": "",
                        "stdout": {"ok": True, "result": expected_entry},
                    },
                )
                _cleanup_database(database)


def run_rejected_value_fixtures(case: unittest.TestCase) -> None:
    fixture = load_fixture(FIXTURE_ROOT / "values-rejected.json")
    cases = fixture["cases"]
    assert isinstance(cases, list)
    for item in cases:
        assert isinstance(item, dict)
        with case.subTest(value_case=item["id"]):
            text, _ = generated_value(item)
            with test_directory() as directory:
                database = directory / "store.db"
                assert_process(
                    case,
                    run_cli(
                        [
                            "--db",
                            str(database),
                            "set",
                            "value",
                            "--value-json",
                            text,
                        ]
                    ),
                    {
                        "exit": item["exit"],
                        "stderr": "",
                        "stdout": {
                            "ok": False,
                            "error": {
                                "category": item["category"],
                                "details": item["details"],
                            },
                        },
                    },
                )
                case.assertFalse(database.exists())


def run_multiprocess_fixture(case: unittest.TestCase) -> None:
    """Run and repeat contention scenarios without prescribing a winner.

    Repeated cases broaden coverage of naturally variable interleavings.  Their
    assertions describe allowed aggregates and final state rather than claiming
    deterministic scheduling or fairness.
    """

    fixture = load_fixture(SCENARIO_ROOT / "multiprocess.json")
    case.assertEqual(fixture["kind"], "multiprocess_scenarios")
    scenarios = fixture["scenarios"]
    assert isinstance(scenarios, list)
    for scenario_value in scenarios:
        assert isinstance(scenario_value, dict)
        for repeat in range(int(scenario_value.get("repeat", 1))):
            with case.subTest(scenario=scenario_value["id"], repeat=repeat + 1):
                _run_multiprocess_scenario(case, scenario_value)


def _run_multiprocess_scenario(
    case: unittest.TestCase,
    scenario: Mapping[str, object],
) -> None:
    with test_directory() as directory:
        database = directory / "store.db"
        missing_parent = directory / "missing" / "store.db"
        if scenario["database"] == "sqlite_setup":
            setup = scenario["setup"]
            assert isinstance(setup, dict)
            _sqlite_setup(database, setup)
        running: dict[str, RunningProcess] = {}
        helpers: dict[str, RunningProcess] = {}
        ready_files: list[Path] = []
        # Named ownership maps make fixture start/release/await operations
        # explicit and leave every still-owned child available to ``finally``.
        try:
            operations = scenario["operations"]
            assert isinstance(operations, list)
            for operation in operations:
                assert isinstance(operation, dict)
                if "parallel" in operation:
                    parallel = operation["parallel"]
                    assert isinstance(parallel, dict)
                    _run_parallel(case, parallel, database, missing_parent)
                elif "run_assert" in operation:
                    item = operation["run_assert"]
                    assert isinstance(item, dict)
                    _run_assert(case, item, database, missing_parent)
                elif "start_lock_helper" in operation:
                    item = operation["start_lock_helper"]
                    assert isinstance(item, dict)
                    identifier = str(item["id"])
                    ready = directory / f"{identifier}.ready"
                    helper = subprocess.Popen(
                        [sys.executable, str(LOCK_HELPER), str(database), str(ready)],
                        cwd=REPOSITORY_ROOT,
                        env=_environment(),
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    helpers[identifier] = RunningProcess(
                        (str(database),),
                        helper,
                        time.monotonic(),
                    )
                    ready_files.append(ready)
                    # The helper publishes readiness only after BEGIN IMMEDIATE,
                    # so subsequent fixture operations really contend on a lock.
                    _wait_for_ready(helper, ready)
                elif "start_cli" in operation:
                    item = operation["start_cli"]
                    assert isinstance(item, dict)
                    identifier = str(item["id"])
                    args = _substitute_args(item["args"], database, missing_parent)
                    process = subprocess.Popen(
                        [*_program(), *args],
                        cwd=REPOSITORY_ROOT,
                        env=_environment(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    running[identifier] = RunningProcess(
                        tuple(args),
                        process,
                        time.monotonic(),
                    )
                elif "sleep_ms" in operation:
                    time.sleep(int(operation["sleep_ms"]) / 1000)
                elif "release_lock_helper" in operation:
                    item = operation["release_lock_helper"]
                    assert isinstance(item, dict)
                    identifier = str(item["id"])
                    _release_helper(case, helpers.pop(identifier))
                elif "await_cli" in operation:
                    item = operation["await_cli"]
                    assert isinstance(item, dict)
                    identifier = str(item["id"])
                    result = _await_process(running.pop(identifier), 20)
                    expected = item["expect"]
                    assert isinstance(expected, dict)
                    assert_process(case, result, expected)
                    assertion = item.get("assert")
                    if isinstance(assertion, dict):
                        _assert_duration(case, result, assertion)
                else:
                    raise AssertionError(f"unknown process operation {operation!r}")
            case.assertFalse(running)
            case.assertFalse(helpers)
            _assert_integrity(case, database)
        finally:
            # A failed assertion must not strand children or SQLite sidecars for
            # later scenarios.  Killing here is cleanup, not a durability test.
            for owned in (*running.values(), *helpers.values()):
                _terminate_owned(owned.process)
            for ready in ready_files:
                ready.unlink(missing_ok=True)
            _cleanup_database(database)


def _run_parallel(
    case: unittest.TestCase,
    parallel: Mapping[str, object],
    database: Path,
    missing_parent: Path,
) -> None:
    """Create indexed actors, release their start barriers, and assert totals."""

    generator = parallel["actors_generator"]
    assertion = parallel["assert"]
    assert isinstance(generator, dict) and isinstance(assertion, dict)
    case.assertEqual(generator["kind"], "indexed_commands")
    actors: list[RunningProcess] = []
    for index in range(int(generator["count"])):
        # Index substitution gives each actor a distinct key/value while keeping
        # the scenario compact enough to audit as fixture data.
        args = _indexed_args(
            generator["args"],
            database,
            missing_parent,
            index,
            int(generator.get("pad_width", 0)),
        )
        process = subprocess.Popen(
            [sys.executable, str(BARRIER_ACTOR), *_program(), *args],
            cwd=REPOSITORY_ROOT,
            env=_environment(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        actors.append(RunningProcess(tuple(args), process, 0.0))
    # All actors now block on stdin.  Releasing them in this loop narrows their
    # start window but does not make OS scheduling simultaneous or deterministic.
    released = time.monotonic()
    for actor in actors:
        assert actor.process.stdin is not None
        actor.process.stdin.write(b"x")
        actor.process.stdin.close()
        actor.process.stdin = None
        actor.started = released
    results: list[ProcessResult] = []
    # Use remaining time from one shared 30-second target rather than a fresh
    # 30 seconds per actor; the 100 ms floor is a small per-actor grace.
    deadline = released + 30
    try:
        for actor in actors:
            results.append(_await_process(actor, max(0.1, deadline - time.monotonic())))
    finally:
        # The harness retains ownership until every actor has been reaped, even
        # when one completion or assertion path raises.
        for actor in actors:
            _terminate_owned(actor.process)
    _assert_parallel(case, results, assertion, database)


def _assert_parallel(
    case: unittest.TestCase,
    results: Sequence[ProcessResult],
    assertion: Mapping[str, object],
    database: Path,
) -> None:
    """Check cohort-wide invariants and the winning value, when applicable.

    Aggregate counts and revision sets accept any permitted winner while still
    detecting lost updates, duplicate revisions, or unexpected error classes.
    """

    envelopes: list[dict[str, object]] = []
    for result in results:
        case.assertEqual(result.stderr, b"", result)
        envelopes.append(decode_stdout(case, result.stdout))
    if "all_exit" in assertion:
        case.assertEqual(
            [result.exit_code for result in results],
            [assertion["all_exit"]] * len(results),
            [
                (result, envelope)
                for result, envelope in zip(results, envelopes, strict=True)
            ],
        )
    if "all_ok" in assertion:
        case.assertTrue(
            all(envelope["ok"] == assertion["all_ok"] for envelope in envelopes)
        )
    if "stdout_semantic_all" in assertion:
        case.assertTrue(
            all(envelope == assertion["stdout_semantic_all"] for envelope in envelopes)
        )

    successes = [
        (result, envelope)
        for result, envelope in zip(results, envelopes, strict=True)
        if envelope["ok"] is True
    ]
    failures = [envelope for envelope in envelopes if envelope["ok"] is False]
    if "success_count" in assertion:
        case.assertEqual(len(successes), assertion["success_count"])
    if "category_counts" in assertion:
        categories = Counter(_error_category(envelope) for envelope in failures)
        case.assertEqual(dict(categories), assertion["category_counts"])
    if "not_found_count" in assertion:
        case.assertEqual(
            sum(_error_category(envelope) == "not_found" for envelope in failures),
            assertion["not_found_count"],
        )
    if "result_revision_set" in assertion:
        expected_range = assertion["result_revision_set"]
        assert isinstance(expected_range, dict)
        revisions = sorted(_result_revision(envelope) for _, envelope in successes)
        case.assertEqual(
            revisions,
            list(
                range(
                    int(expected_range["from"]),
                    int(expected_range["to"]) + 1,
                )
            ),
        )
    if "success_revision" in assertion:
        case.assertTrue(
            all(
                _result_revision(envelope) == assertion["success_revision"]
                for _, envelope in successes
            )
        )
    if "conflict_actual" in assertion:
        for envelope in failures:
            if _error_category(envelope) == "conflict":
                error = envelope["error"]
                assert isinstance(error, dict)
                details = error["details"]
                assert isinstance(details, dict)
                case.assertEqual(details["actual"], assertion["conflict_actual"])
    if assertion.get("winner_value_matches_final"):
        case.assertEqual(len(successes), 1)
        winner_result, winner_envelope = successes[0]
        key = winner_result.args[3]
        final = assert_process(
            case,
            run_cli(["--db", str(database), "get", key]),
            {"exit": 0, "stderr": ""},
        )
        winner_payload = winner_envelope["result"]
        final_payload = final["result"]
        assert isinstance(winner_payload, dict) and isinstance(final_payload, dict)
        case.assertEqual(final_payload["value"], winner_payload["value"])


def _run_assert(
    case: unittest.TestCase,
    item: Mapping[str, object],
    database: Path,
    missing_parent: Path,
) -> dict[str, object]:
    args = _substitute_args(item["args"], database, missing_parent)
    expected = item["expect"]
    assert isinstance(expected, dict)
    result = run_cli(args)
    envelope = assert_process(case, result, expected)
    assertion = item.get("assert")
    if isinstance(assertion, dict):
        _assert_structure(case, envelope, assertion)
        _assert_duration(case, result, assertion)
    return envelope


def _assert_structure(
    case: unittest.TestCase,
    envelope: Mapping[str, object],
    assertion: Mapping[str, object],
) -> None:
    result = envelope["result"]
    assert isinstance(result, dict)
    entries_value = result.get("entries", [])
    assert isinstance(entries_value, list)
    entries = entries_value
    if "keys_in_order" in assertion:
        case.assertEqual(
            [entry["key"] for entry in entries], assertion["keys_in_order"]
        )
    if "global_revision" in assertion:
        case.assertEqual(result["global_revision"], assertion["global_revision"])
    if "entry_count" in assertion:
        case.assertEqual(len(entries), assertion["entry_count"])
    if "entry_revision_set" in assertion:
        expected_range = assertion["entry_revision_set"]
        assert isinstance(expected_range, dict)
        case.assertEqual(
            sorted(entry["revision"] for entry in entries),
            list(
                range(
                    int(expected_range["from"]),
                    int(expected_range["to"]) + 1,
                )
            ),
        )
    if "values_by_key" in assertion:
        case.assertEqual(
            {entry["key"]: entry["value"] for entry in entries},
            assertion["values_by_key"],
        )
    if "revision_by_key" in assertion:
        case.assertEqual(
            {entry["key"]: entry["revision"] for entry in entries},
            assertion["revision_by_key"],
        )


def _assert_duration(
    case: unittest.TestCase,
    result: ProcessResult,
    assertion: Mapping[str, object],
) -> None:
    """Apply fixture timing bounds to observed parent wall-clock duration.

    These bounds check busy-timeout behavior; passing them does not establish
    fairness or prove that no race exists outside the sampled executions.
    """

    if "duration_less_than_ms" in assertion:
        case.assertLess(result.duration_ms, assertion["duration_less_than_ms"])
    if "duration_at_least_ms" in assertion:
        case.assertGreaterEqual(result.duration_ms, assertion["duration_at_least_ms"])


def _sqlite_setup(database: Path, setup: Mapping[str, object]) -> None:
    statements = setup["statements"]
    assert isinstance(statements, list)
    with closing(sqlite3.connect(database)) as connection:
        for statement in statements:
            connection.execute(str(statement))
        connection.commit()


def _assert_sqlite(
    case: unittest.TestCase,
    database: Path,
    assertion: Mapping[str, object],
) -> None:
    queries = assertion["queries"]
    assert isinstance(queries, list)
    with closing(sqlite3.connect(database)) as connection:
        for query in queries:
            assert isinstance(query, dict)
            rows = connection.execute(str(query["sql"])).fetchall()
            case.assertEqual([list(row) for row in rows], query["rows"])


def _assert_integrity(case: unittest.TestCase, database: Path) -> None:
    if not database.exists():
        return
    try:
        with closing(sqlite3.connect(database)) as connection:
            rows = connection.execute("PRAGMA integrity_check").fetchall()
    except sqlite3.DatabaseError:
        return
    case.assertEqual(rows, [("ok",)])


def _cleanup_database(database: Path) -> None:
    """Remove the database and every SQLite sidecar after children are closed."""

    for suffix in ("", "-wal", "-shm", "-journal"):
        path = Path(str(database) + suffix)
        path.unlink(missing_ok=True)
        if path.exists():
            raise AssertionError(f"could not remove closed SQLite file {path}")


def _substitute_args(
    raw_args: object,
    database: Path,
    missing_parent: Path,
) -> list[str]:
    assert isinstance(raw_args, list)
    return [
        str(value)
        .replace("${DB}", str(database))
        .replace("${MISSING_PARENT}", str(missing_parent.parent))
        for value in raw_args
    ]


def _indexed_args(
    raw_args: object,
    database: Path,
    missing_parent: Path,
    index: int,
    pad_width: int,
) -> list[str]:
    number = index + 1
    return [
        value.replace("${i}", str(index))
        .replace("${n}", str(number))
        .replace("${padded_n}", str(number).zfill(pad_width))
        for value in _substitute_args(raw_args, database, missing_parent)
    ]


def _wait_for_ready(process: subprocess.Popen[bytes], ready: Path) -> None:
    """Wait until the lock helper confirms its immediate transaction is held."""

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if ready.exists():
            return
        if process.poll() is not None:
            _, stderr = process.communicate()
            raise AssertionError(f"lock helper failed before ready: {stderr!r}")
        time.sleep(0.01)
    _terminate_owned(process)
    raise AssertionError("lock helper did not become ready")


def _release_helper(
    case: unittest.TestCase,
    helper: RunningProcess,
) -> None:
    """Release a held lock, then await and validate the owned helper."""

    process = helper.process
    assert process.stdin is not None
    process.stdin.write(b"x")
    process.stdin.close()
    process.stdin = None
    result = _await_process(helper, 15)
    case.assertEqual(result.exit_code, 0, result.stderr)
    case.assertEqual(result.stderr, b"")


def _await_process(owned: RunningProcess, timeout: float) -> ProcessResult:
    """Reap an owned child or terminate it when its explicit deadline expires."""

    try:
        stdout, stderr = owned.process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        _terminate_owned(owned.process)
        raise AssertionError(f"owned process timed out: {owned.args!r}") from error
    return ProcessResult(
        owned.args,
        stdout,
        stderr,
        owned.process.returncode,
        (time.monotonic() - owned.started) * 1000,
    )


def _terminate_owned(process: subprocess.Popen[bytes]) -> None:
    """Ensure a child owned by the harness is no longer running and is reaped."""

    if process.poll() is None:
        process.kill()
        process.communicate(timeout=30)


def _error_category(envelope: Mapping[str, object]) -> str:
    error = envelope["error"]
    assert isinstance(error, dict)
    return str(error["category"])


def _result_revision(envelope: Mapping[str, object]) -> int:
    result = envelope["result"]
    assert isinstance(result, dict)
    return int(result["revision"])


def _program() -> list[str]:
    if os.environ.get("CAPSTONE_SUBPROCESS_COVERAGE") == "1":
        return [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--parallel-mode",
            "-m",
            "comparative_kv",
        ]
    return [sys.executable, "-m", "comparative_kv"]


def _environment() -> dict[str, str]:
    """Build the isolated import and text-I/O environment inherited by children."""

    return {
        **os.environ,
        "PYTHONPATH": str(SOURCE_ROOT),
        "PYTHONIOENCODING": "utf-8",
    }
