#!/usr/bin/env python3
"""Local, version-aware learner state for the learning tutor."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sqlite3
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

SCHEMA_VERSION = 1
DB_ENV_VAR = "COPILOT_LEARNING_TUTOR_DB"
BUSY_TIMEOUT_ENV_VAR = "COPILOT_LEARNING_TUTOR_BUSY_TIMEOUT_MS"
DEFAULT_BUSY_TIMEOUT_MS = 5_000

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NOT_FOUND = 3
EXIT_CONFLICT = 4
EXIT_STATE = 5
EXIT_IO = 6

MASTERY_LEVELS = {
    "not_started": 0,
    "in_progress": 1,
    "practiced": 2,
    "mastered": 3,
}
MASTERY_NAMES = {value: key for key, value in MASTERY_LEVELS.items()}
MASTERY_ALIASES = {
    "unseen": "not_started",
    "learning": "in_progress",
}
LOCAL_WARNING = "using explicit local fallback; state will not follow a Git remote"
CONCEPT_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")

REQUIRED_COLUMNS = {
    "schema_meta": {"key", "value"},
    "courses": {
        "id",
        "identity",
        "identity_kind",
        "normalized_remote",
        "local_fallback",
        "created_at",
        "updated_at",
    },
    "course_versions": {"id", "course_id", "commit_sha", "created_at"},
    "concepts": {
        "id",
        "course_version_id",
        "concept_key",
        "title",
        "ordinal",
        "prerequisites_json",
        "solution_unlock_after",
        "created_at",
        "updated_at",
    },
    "attempts": {
        "id",
        "course_id",
        "course_version_id",
        "concept_key",
        "event_type",
        "outcome",
        "score",
        "hint_level",
        "occurred_at",
    },
    "mastery": {
        "course_id",
        "concept_key",
        "level",
        "evidence_attempt_id",
        "updated_at",
    },
    "reviews": {
        "course_id",
        "concept_key",
        "due_at",
        "interval_days",
        "ease",
        "repetitions",
        "updated_at",
    },
    "solution_unlocks": {
        "course_version_id",
        "concept_key",
        "reason",
        "unlocked_at",
    },
    "sessions": {
        "id",
        "course_id",
        "course_version_id",
        "command",
        "started_at",
        "ended_at",
    },
}

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE schema_meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY,
        identity TEXT NOT NULL UNIQUE,
        identity_kind TEXT NOT NULL CHECK (identity_kind IN ('remote', 'local')),
        normalized_remote TEXT,
        local_fallback TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        CHECK (
            (identity_kind = 'remote' AND normalized_remote IS NOT NULL
                AND local_fallback IS NULL)
            OR
            (identity_kind = 'local' AND normalized_remote IS NULL
                AND local_fallback IS NOT NULL)
        )
    )
    """,
    """
    CREATE TABLE course_versions (
        id INTEGER PRIMARY KEY,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        commit_sha TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE (course_id, commit_sha),
        UNIQUE (id, course_id)
    )
    """,
    """
    CREATE TABLE concepts (
        id INTEGER PRIMARY KEY,
        course_version_id INTEGER NOT NULL
            REFERENCES course_versions(id) ON DELETE CASCADE,
        concept_key TEXT NOT NULL,
        title TEXT NOT NULL,
        ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
        prerequisites_json TEXT NOT NULL,
        solution_unlock_after INTEGER NOT NULL DEFAULT 1
            CHECK (solution_unlock_after >= 1),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE (course_version_id, concept_key)
    )
    """,
    """
    CREATE TABLE attempts (
        id INTEGER PRIMARY KEY,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        course_version_id INTEGER NOT NULL,
        concept_key TEXT NOT NULL,
        event_type TEXT NOT NULL CHECK (event_type IN ('attempt', 'hint')),
        outcome TEXT CHECK (
            outcome IS NULL OR outcome IN ('passed', 'failed', 'error', 'skipped')
        ),
        score REAL CHECK (score IS NULL OR (score >= 0.0 AND score <= 1.0)),
        hint_level INTEGER CHECK (
            hint_level IS NULL OR (hint_level >= 0 AND hint_level <= 4)
        ),
        occurred_at TEXT NOT NULL,
        FOREIGN KEY (course_version_id, course_id)
            REFERENCES course_versions(id, course_id) ON DELETE CASCADE,
        FOREIGN KEY (course_version_id, concept_key)
            REFERENCES concepts(course_version_id, concept_key) ON DELETE CASCADE,
        CHECK (
            (event_type = 'attempt' AND outcome IS NOT NULL AND hint_level IS NULL)
            OR
            (event_type = 'hint' AND outcome IS NULL AND score IS NULL
                AND hint_level IS NOT NULL)
        )
    )
    """,
    """
    CREATE TABLE mastery (
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        concept_key TEXT NOT NULL,
        level INTEGER NOT NULL CHECK (level BETWEEN 0 AND 3),
        evidence_attempt_id INTEGER REFERENCES attempts(id) ON DELETE SET NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (course_id, concept_key)
    )
    """,
    """
    CREATE TABLE reviews (
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        concept_key TEXT NOT NULL,
        due_at TEXT NOT NULL,
        interval_days INTEGER NOT NULL CHECK (interval_days >= 0),
        ease REAL NOT NULL CHECK (ease >= 1.3 AND ease <= 3.0),
        repetitions INTEGER NOT NULL CHECK (repetitions >= 0),
        updated_at TEXT NOT NULL,
        PRIMARY KEY (course_id, concept_key)
    )
    """,
    """
    CREATE TABLE solution_unlocks (
        course_version_id INTEGER NOT NULL,
        concept_key TEXT NOT NULL,
        reason TEXT NOT NULL CHECK (
            reason IN (
                'deterministic_success',
                'post_attempt_request',
                'already_unlocked'
            )
        ),
        unlocked_at TEXT NOT NULL,
        PRIMARY KEY (course_version_id, concept_key),
        FOREIGN KEY (course_version_id, concept_key)
            REFERENCES concepts(course_version_id, concept_key) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE sessions (
        id INTEGER PRIMARY KEY,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        course_version_id INTEGER NOT NULL,
        command TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT NOT NULL,
        FOREIGN KEY (course_version_id, course_id)
            REFERENCES course_versions(id, course_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX attempts_course_concept_idx
        ON attempts(course_id, concept_key, event_type, occurred_at)
    """,
    """
    CREATE INDEX reviews_due_idx ON reviews(course_id, due_at)
    """,
    """
    CREATE INDEX concepts_order_idx
        ON concepts(course_version_id, ordinal, concept_key)
    """,
)


class TutorError(Exception):
    """An expected CLI failure with a stable category and exit code."""

    def __init__(self, message: str, category: str, exit_code: int) -> None:
        super().__init__(message)
        self.category = category
        self.exit_code = exit_code


class UsageError(TutorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "usage", EXIT_USAGE)


class NotFoundError(TutorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "not-found", EXIT_NOT_FOUND)


class ConflictError(TutorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "conflict", EXIT_CONFLICT)


class StateError(TutorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "state", EXIT_STATE)


class StateIOError(TutorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "io", EXIT_IO)


class TutorArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


@dataclass(frozen=True, slots=True)
class CourseIdentity:
    identity: str
    kind: str
    normalized_remote: str | None
    local_fallback: str | None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CourseContext:
    course_id: int
    version_id: int
    identity: CourseIdentity
    commit_sha: str


@dataclass(frozen=True, slots=True)
class CommandResult:
    payload: dict[str, Any]
    context: CourseContext


def compact_json(value: Any) -> str:
    """Serialize JSON predictably for adapters and tests."""
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def default_db_path(env: dict[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    if explicit := values.get(DB_ENV_VAR):
        return Path(explicit).expanduser()
    data_home = values.get("XDG_DATA_HOME")
    root = Path(data_home).expanduser() if data_home else Path.home() / ".local/share"
    return root / "copilot-learning-tutor/state.sqlite3"


def normalize_remote_url(remote: str) -> str:
    """Normalize common HTTPS, SSH, git, SCP, and file Git remote forms."""
    value = remote.strip()
    if not value:
        raise UsageError("remote URL must not be empty")

    scp_match = re.fullmatch(
        r"(?:[^/@:\s]+@)?(?P<host>[^/:\s]+):(?P<path>[^:]+)",
        value,
    )
    if scp_match and "://" not in value:
        host = scp_match.group("host").lower()
        path = _normalize_remote_path(scp_match.group("path"))
        if not path:
            raise UsageError("remote URL must identify a repository")
        return f"{host}/{path}"

    candidate = value
    if "://" not in candidate:
        candidate = f"ssh://{candidate}"
    parsed = urlsplit(candidate)

    if parsed.scheme.lower() == "file":
        path = Path(unquote(parsed.path)).expanduser().resolve()
        normalized_path = _strip_dot_git(path.as_posix().rstrip("/"))
        if not normalized_path:
            raise UsageError("remote URL must identify a repository")
        return f"file://{normalized_path}"

    host = parsed.hostname
    if not host:
        raise UsageError("remote URL must include a host")
    path = _normalize_remote_path(parsed.path)
    if not path:
        raise UsageError("remote URL must identify a repository")

    host_part = host.lower()
    try:
        port = parsed.port
    except ValueError as exc:
        raise UsageError("remote URL has an invalid port") from exc
    scheme = parsed.scheme.lower()
    if port is not None and not (
        (scheme == "ssh" and port == 22)
        or (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
        or (scheme == "git" and port == 9418)
    ):
        host_part = f"{host_part}:{port}"
    return f"{host_part}/{path}"


def _normalize_remote_path(path: str) -> str:
    normalized = re.sub(r"/+", "/", unquote(path).strip().strip("/"))
    return _strip_dot_git(normalized)


def _strip_dot_git(value: str) -> str:
    return value[:-4] if value.lower().endswith(".git") else value


def resolve_course_identity(
    remote: str | None,
    local_fallback: str | None,
) -> CourseIdentity:
    if remote and local_fallback:
        raise UsageError("provide either --remote or --local-fallback, not both")
    if remote:
        normalized = normalize_remote_url(remote)
        return CourseIdentity(
            identity=f"remote:{normalized}",
            kind="remote",
            normalized_remote=normalized,
            local_fallback=None,
        )
    if not local_fallback or not local_fallback.strip():
        raise UsageError("a remote URL or explicit --local-fallback path is required")
    fallback = str(Path(local_fallback).expanduser().resolve())
    return CourseIdentity(
        identity=f"local:{fallback}",
        kind="local",
        normalized_remote=None,
        local_fallback=fallback,
        warnings=(LOCAL_WARNING,),
    )


def normalize_commit(commit_sha: str) -> str:
    value = commit_sha.strip().lower()
    if not COMMIT_RE.fullmatch(value):
        raise UsageError("commit must be a 7-64 character hexadecimal Git SHA")
    return value


def parse_timestamp(value: str | None) -> datetime:
    if value is None:
        return datetime.now(UTC).replace(microsecond=0)
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise UsageError("timestamp must be valid ISO 8601") from exc
    if parsed.tzinfo is None:
        raise UsageError("timestamp must include a UTC offset")
    return parsed.astimezone(UTC).replace(microsecond=0)


def format_timestamp(value: datetime) -> str:
    return (
        value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def connect_database(path: Path, busy_timeout_ms: int) -> sqlite3.Connection:
    if busy_timeout_ms < 0 or busy_timeout_ms > 600_000:
        raise UsageError("busy timeout must be between 0 and 600000 milliseconds")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            path,
            isolation_level=None,
            timeout=busy_timeout_ms / 1000,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {busy_timeout_ms}")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        return connection
    except OSError as exc:
        raise StateIOError(f"cannot prepare state database: {exc}") from exc
    except sqlite3.Error as exc:
        raise _translate_sqlite_error(exc) from exc


@contextlib.contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[None]:
    try:
        connection.execute("BEGIN IMMEDIATE")
        yield
        connection.execute("COMMIT")
    except Exception:
        with contextlib.suppress(sqlite3.Error):
            connection.execute("ROLLBACK")
        raise


def ensure_schema(
    connection: sqlite3.Connection,
    *,
    allow_create: bool,
) -> None:
    try:
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        tables = {
            row["name"]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
            )
        }
        if version == 0:
            if tables:
                raise StateError("database has tables but no supported schema version")
            if not allow_create:
                raise StateError("state database is not initialized")
            for statement in SCHEMA_STATEMENTS:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_meta(key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION)),
            )
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        elif version != SCHEMA_VERSION:
            raise StateError(
                f"unsupported schema version {version}; expected {SCHEMA_VERSION}"
            )
        _validate_schema(connection)
    except sqlite3.Error as exc:
        raise _translate_sqlite_error(exc) from exc


def _validate_schema(connection: sqlite3.Connection) -> None:
    for table, required in REQUIRED_COLUMNS.items():
        columns = {
            row["name"] for row in connection.execute(f'PRAGMA table_info("{table}")')
        }
        if not columns:
            raise StateError(f"state schema is missing table {table}")
        missing = required - columns
        if missing:
            joined = ", ".join(sorted(missing))
            raise StateError(f"state schema table {table} is missing: {joined}")

    meta = connection.execute(
        "SELECT value FROM schema_meta WHERE key = ?",
        ("schema_version",),
    ).fetchone()
    if meta is None or meta["value"] != str(SCHEMA_VERSION):
        raise StateError("state schema metadata is missing or inconsistent")
    check = connection.execute("PRAGMA quick_check").fetchone()
    if check is None or check[0] != "ok":
        detail = "unknown" if check is None else str(check[0])
        raise StateError(f"state database integrity check failed: {detail}")
    violation = connection.execute("PRAGMA foreign_key_check").fetchone()
    if violation is not None:
        raise StateError("state database contains foreign-key violations")


def _translate_sqlite_error(error: sqlite3.Error) -> TutorError:
    message = str(error)
    lowered = message.lower()
    if "locked" in lowered or "busy" in lowered:
        return ConflictError("state database is busy")
    if (
        "not a database" in lowered
        or "malformed" in lowered
        or "corrupt" in lowered
        or "schema" in lowered
    ):
        return StateError(f"invalid state database: {message}")
    if "unable to open" in lowered or "readonly" in lowered:
        return StateIOError(f"cannot access state database: {message}")
    return StateError(f"state database error: {message}")


def load_concepts(
    concepts_path: str | None,
    concepts_json: str | None,
) -> list[dict[str, Any]]:
    if concepts_path and concepts_json:
        raise UsageError("provide either --concepts or --concepts-json, not both")
    if not concepts_path and concepts_json is None:
        return []
    try:
        if concepts_json is not None:
            raw = concepts_json
        elif concepts_path == "-":
            raw = sys.stdin.read()
        else:
            raw = Path(str(concepts_path)).read_text(encoding="utf-8")
        parsed = json.loads(raw)
    except OSError as exc:
        raise StateIOError(f"cannot read concepts: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise UsageError(
            f"concepts JSON is invalid at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if isinstance(parsed, dict):
        parsed = parsed.get("concepts")
    if not isinstance(parsed, list):
        raise UsageError("concepts JSON must be a list or an object with concepts")

    concepts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise UsageError(f"concept {index} must be an object")
        key = item.get("id", item.get("key"))
        if not isinstance(key, str) or not CONCEPT_KEY_RE.fullmatch(key):
            raise UsageError(f"concept {index} has an invalid id")
        if key in seen:
            raise UsageError(f"duplicate concept id: {key}")
        seen.add(key)

        title = item.get("title", key)
        if not isinstance(title, str) or not title.strip() or len(title) > 256:
            raise UsageError(f"concept {key} has an invalid title")
        prerequisites = item.get("prerequisites", item.get("requires", []))
        if (
            not isinstance(prerequisites, list)
            or not all(isinstance(value, str) for value in prerequisites)
            or len(prerequisites) != len(set(prerequisites))
        ):
            raise UsageError(f"concept {key} prerequisites must be unique string ids")
        if key in prerequisites:
            raise UsageError(f"concept {key} cannot require itself")
        ordinal = item.get("order", item.get("ordinal", index))
        unlock_after = item.get("solution_unlock_after", 1)
        if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 0:
            raise UsageError(f"concept {key} order must be a non-negative integer")
        if (
            not isinstance(unlock_after, int)
            or isinstance(unlock_after, bool)
            or not 1 <= unlock_after <= 100
        ):
            raise UsageError(
                f"concept {key} solution_unlock_after must be between 1 and 100"
            )
        concepts.append(
            {
                "key": key,
                "title": title.strip(),
                "ordinal": ordinal,
                "prerequisites": prerequisites,
                "solution_unlock_after": unlock_after,
            }
        )
    return concepts


def init_course(
    connection: sqlite3.Connection,
    identity: CourseIdentity,
    commit_sha: str,
    concepts: list[dict[str, Any]],
    now: datetime,
) -> CommandResult:
    timestamp = format_timestamp(now)
    row = connection.execute(
        "SELECT id FROM courses WHERE identity = ?",
        (identity.identity,),
    ).fetchone()
    course_created = row is None
    if row is None:
        cursor = connection.execute(
            """
            INSERT INTO courses(
                identity, identity_kind, normalized_remote, local_fallback,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                identity.identity,
                identity.kind,
                identity.normalized_remote,
                identity.local_fallback,
                timestamp,
                timestamp,
            ),
        )
        course_id = int(cursor.lastrowid)
    else:
        course_id = int(row["id"])
        connection.execute(
            "UPDATE courses SET updated_at = ? WHERE id = ?",
            (timestamp, course_id),
        )

    version = connection.execute(
        """
        SELECT id FROM course_versions
        WHERE course_id = ? AND commit_sha = ?
        """,
        (course_id, commit_sha),
    ).fetchone()
    version_created = version is None
    if version is None:
        cursor = connection.execute(
            """
            INSERT INTO course_versions(course_id, commit_sha, created_at)
            VALUES (?, ?, ?)
            """,
            (course_id, commit_sha, timestamp),
        )
        version_id = int(cursor.lastrowid)
    else:
        version_id = int(version["id"])

    for concept in concepts:
        connection.execute(
            """
            INSERT INTO concepts(
                course_version_id, concept_key, title, ordinal,
                prerequisites_json, solution_unlock_after, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(course_version_id, concept_key) DO UPDATE SET
                title = excluded.title,
                ordinal = excluded.ordinal,
                prerequisites_json = excluded.prerequisites_json,
                solution_unlock_after = excluded.solution_unlock_after,
                updated_at = excluded.updated_at
            """,
            (
                version_id,
                concept["key"],
                concept["title"],
                concept["ordinal"],
                compact_json(concept["prerequisites"]),
                concept["solution_unlock_after"],
                timestamp,
                timestamp,
            ),
        )
    _validate_concept_graph(connection, version_id)
    total = int(
        connection.execute(
            "SELECT COUNT(*) FROM concepts WHERE course_version_id = ?",
            (version_id,),
        ).fetchone()[0]
    )

    context = CourseContext(course_id, version_id, identity, commit_sha)
    return CommandResult(
        payload={
            "commit": commit_sha,
            "concepts": {"total": total, "upserted": len(concepts)},
            "course": {
                "identity": identity.identity,
                "kind": identity.kind,
                "normalized_remote": identity.normalized_remote,
            },
            "created": {
                "course": course_created,
                "version": version_created,
            },
            "schema_version": SCHEMA_VERSION,
            "warnings": list(identity.warnings),
        },
        context=context,
    )


def _validate_concept_graph(
    connection: sqlite3.Connection,
    version_id: int,
) -> None:
    rows = connection.execute(
        """
        SELECT concept_key, prerequisites_json
        FROM concepts
        WHERE course_version_id = ?
        """,
        (version_id,),
    ).fetchall()
    graph = {
        row["concept_key"]: _decode_prerequisites(
            row["concept_key"], row["prerequisites_json"]
        )
        for row in rows
    }
    for key, prerequisites in graph.items():
        missing = sorted(set(prerequisites) - graph.keys())
        if missing:
            raise UsageError(
                f"concept {key} has unknown prerequisites: {', '.join(missing)}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> None:
        if key in visiting:
            raise UsageError("concept prerequisites contain a cycle")
        if key in visited:
            return
        visiting.add(key)
        for prerequisite in graph[key]:
            visit(prerequisite)
        visiting.remove(key)
        visited.add(key)

    for concept_key in sorted(graph):
        visit(concept_key)


def _decode_prerequisites(key: str, raw: str) -> list[str]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise StateError(f"concept {key} has corrupt prerequisites") from exc
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise StateError(f"concept {key} has corrupt prerequisites")
    return value


def lookup_context(
    connection: sqlite3.Connection,
    identity: CourseIdentity,
    commit_sha: str,
) -> CourseContext:
    row = connection.execute(
        """
        SELECT c.id AS course_id, v.id AS version_id
        FROM courses AS c
        JOIN course_versions AS v ON v.course_id = c.id
        WHERE c.identity = ? AND v.commit_sha = ?
        """,
        (identity.identity, commit_sha),
    ).fetchone()
    if row is None:
        raise NotFoundError("course or commit version is not initialized")
    return CourseContext(
        int(row["course_id"]),
        int(row["version_id"]),
        identity,
        commit_sha,
    )


def _concept_rows(
    connection: sqlite3.Connection,
    context: CourseContext,
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
            c.concept_key,
            c.title,
            c.ordinal,
            c.prerequisites_json,
            c.solution_unlock_after,
            COALESCE(m.level, 0) AS mastery_level,
            m.updated_at AS mastery_updated_at,
            r.due_at,
            r.interval_days,
            r.ease,
            r.repetitions,
            EXISTS(
                SELECT 1
                FROM solution_unlocks AS u
                WHERE u.course_version_id = c.course_version_id
                  AND u.concept_key = c.concept_key
            ) AS solution_unlocked,
            (
                SELECT COUNT(*)
                FROM attempts AS a
                WHERE a.course_id = ?
                  AND a.concept_key = c.concept_key
                  AND a.event_type = 'attempt'
            ) AS attempt_count,
            (
                SELECT COUNT(*)
                FROM attempts AS a
                WHERE a.course_id = ?
                  AND a.concept_key = c.concept_key
                  AND a.event_type = 'attempt'
                  AND a.outcome = 'failed'
            ) AS failed_attempt_count,
            (
                SELECT COUNT(*)
                FROM attempts AS a
                WHERE a.course_id = ?
                  AND a.concept_key = c.concept_key
                  AND a.event_type = 'hint'
            ) AS hint_count
        FROM concepts AS c
        LEFT JOIN mastery AS m
          ON m.course_id = ? AND m.concept_key = c.concept_key
        LEFT JOIN reviews AS r
          ON r.course_id = ? AND r.concept_key = c.concept_key
        WHERE c.course_version_id = ?
        ORDER BY c.ordinal, c.concept_key
        """,
        (
            context.course_id,
            context.course_id,
            context.course_id,
            context.course_id,
            context.course_id,
            context.version_id,
        ),
    ).fetchall()


def status(
    connection: sqlite3.Connection,
    context: CourseContext,
) -> CommandResult:
    rows = _concept_rows(connection, context)
    concepts = [_concept_payload(row) for row in rows]
    complete = bool(concepts) and all(
        item["mastery"] == "mastered" for item in concepts
    )
    return CommandResult(
        payload={
            "commit": context.commit_sha,
            "complete": complete,
            "concepts": concepts,
            "course": {
                "identity": context.identity.identity,
                "kind": context.identity.kind,
            },
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def _concept_payload(row: sqlite3.Row) -> dict[str, Any]:
    review = None
    if row["due_at"] is not None:
        review = {
            "due_at": row["due_at"],
            "ease": row["ease"],
            "interval_days": row["interval_days"],
            "repetitions": row["repetitions"],
        }
    return {
        "attempts": int(row["attempt_count"]),
        "failed_attempts": int(row["failed_attempt_count"]),
        "hints": int(row["hint_count"]),
        "id": row["concept_key"],
        "mastery": MASTERY_NAMES[int(row["mastery_level"])],
        "order": int(row["ordinal"]),
        "prerequisites": _decode_prerequisites(
            row["concept_key"], row["prerequisites_json"]
        ),
        "review": review,
        "solution": {
            "attempts_required_for_request": int(row["solution_unlock_after"]),
            "unlocked": bool(row["solution_unlocked"]),
        },
        "title": row["title"],
    }


def next_objective(
    connection: sqlite3.Connection,
    context: CourseContext,
) -> CommandResult:
    rows = _concept_rows(connection, context)
    levels = {row["concept_key"]: int(row["mastery_level"]) for row in rows}
    blocked: list[dict[str, Any]] = []
    practiced: list[sqlite3.Row] = []
    objective: dict[str, Any] | None = None
    for row in rows:
        current_level = int(row["mastery_level"])
        if current_level == MASTERY_LEVELS["mastered"]:
            continue
        if current_level == MASTERY_LEVELS["practiced"]:
            practiced.append(row)
            continue
        prerequisites = _decode_prerequisites(
            row["concept_key"], row["prerequisites_json"]
        )
        unmet = [
            key
            for key in prerequisites
            if levels.get(key, 0) < MASTERY_LEVELS["practiced"]
        ]
        if not unmet and objective is None:
            objective = {
                "id": row["concept_key"],
                "mastery": MASTERY_NAMES[int(row["mastery_level"])],
                "prerequisites": prerequisites,
                "reason": "first_available_in_course_order",
                "title": row["title"],
            }
            break
        blocked.append({"id": row["concept_key"], "unmet_prerequisites": unmet})

    if objective is None and practiced:
        row = practiced[0]
        objective = {
            "id": row["concept_key"],
            "mastery": "practiced",
            "prerequisites": _decode_prerequisites(
                row["concept_key"], row["prerequisites_json"]
            ),
            "reason": "strengthen_practiced_concept",
            "title": row["title"],
        }

    if objective is not None:
        reason = "objective_available"
    elif rows and all(
        int(row["mastery_level"]) == MASTERY_LEVELS["mastered"] for row in rows
    ):
        reason = "course_complete"
    elif not rows:
        reason = "no_concepts"
    else:
        reason = "blocked_by_prerequisites"
    return CommandResult(
        payload={
            "blocked": blocked if objective is None else [],
            "commit": context.commit_sha,
            "objective": objective,
            "reason": reason,
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def _require_concept(
    connection: sqlite3.Connection,
    context: CourseContext,
    concept_key: str,
) -> sqlite3.Row:
    row = connection.execute(
        """
        SELECT concept_key, title, solution_unlock_after
        FROM concepts
        WHERE course_version_id = ? AND concept_key = ?
        """,
        (context.version_id, concept_key),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"concept is not defined for this commit: {concept_key}")
    return row


def _mark_learning(
    connection: sqlite3.Connection,
    context: CourseContext,
    concept_key: str,
    timestamp: str,
    evidence_attempt_id: int,
) -> None:
    connection.execute(
        """
        INSERT INTO mastery(
            course_id, concept_key, level, evidence_attempt_id, updated_at
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(course_id, concept_key) DO UPDATE SET
            level = MAX(mastery.level, excluded.level),
            evidence_attempt_id = CASE
                WHEN mastery.level < ? THEN excluded.evidence_attempt_id
                ELSE mastery.evidence_attempt_id
            END,
            updated_at = CASE
                WHEN mastery.level < ? THEN excluded.updated_at
                ELSE mastery.updated_at
            END
        """,
        (
            context.course_id,
            concept_key,
            MASTERY_LEVELS["in_progress"],
            evidence_attempt_id,
            timestamp,
            MASTERY_LEVELS["mastered"],
            MASTERY_LEVELS["mastered"],
        ),
    )


def record_attempt(
    connection: sqlite3.Connection,
    context: CourseContext,
    concept_key: str,
    outcome: str,
    score: float | None,
    now: datetime,
) -> CommandResult:
    _require_concept(connection, context, concept_key)
    aliases = {
        "pass": "passed",
        "success": "passed",
        "fail": "failed",
        "failure": "failed",
    }
    normalized_outcome = aliases.get(outcome, outcome)
    if normalized_outcome not in {"passed", "failed", "error", "skipped"}:
        raise UsageError("outcome must be passed, failed, error, or skipped")
    if score is not None and not 0.0 <= score <= 1.0:
        raise UsageError("score must be between 0 and 1")
    timestamp = format_timestamp(now)
    cursor = connection.execute(
        """
        INSERT INTO attempts(
            course_id, course_version_id, concept_key, event_type,
            outcome, score, hint_level, occurred_at
        ) VALUES (?, ?, ?, 'attempt', ?, ?, NULL, ?)
        """,
        (
            context.course_id,
            context.version_id,
            concept_key,
            normalized_outcome,
            score,
            timestamp,
        ),
    )
    _mark_learning(
        connection,
        context,
        concept_key,
        timestamp,
        int(cursor.lastrowid),
    )
    attempt_count, failed_count = _attempt_counts(
        connection, context.course_id, concept_key
    )
    return CommandResult(
        payload={
            "attempt_id": int(cursor.lastrowid),
            "attempts": attempt_count,
            "concept": concept_key,
            "failed_attempts": failed_count,
            "mastery": _mastery_name(connection, context.course_id, concept_key),
            "outcome": normalized_outcome,
            "recorded_at": timestamp,
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def _attempt_counts(
    connection: sqlite3.Connection,
    course_id: int,
    concept_key: str,
) -> tuple[int, int]:
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS attempts,
            SUM(CASE WHEN outcome = 'failed' THEN 1 ELSE 0 END) AS failed
        FROM attempts
        WHERE course_id = ? AND concept_key = ? AND event_type = 'attempt'
        """,
        (course_id, concept_key),
    ).fetchone()
    return int(row["attempts"]), int(row["failed"] or 0)


def _mastery_name(
    connection: sqlite3.Connection,
    course_id: int,
    concept_key: str,
) -> str:
    row = connection.execute(
        "SELECT level FROM mastery WHERE course_id = ? AND concept_key = ?",
        (course_id, concept_key),
    ).fetchone()
    return MASTERY_NAMES[0 if row is None else int(row["level"])]


def record_hint(
    connection: sqlite3.Connection,
    context: CourseContext,
    concept_key: str,
    hint_level: int,
    now: datetime,
) -> CommandResult:
    _require_concept(connection, context, concept_key)
    if not 0 <= hint_level <= 4:
        raise UsageError("hint level must be between 0 and 4")
    timestamp = format_timestamp(now)
    cursor = connection.execute(
        """
        INSERT INTO attempts(
            course_id, course_version_id, concept_key, event_type,
            outcome, score, hint_level, occurred_at
        ) VALUES (?, ?, ?, 'hint', NULL, NULL, ?, ?)
        """,
        (
            context.course_id,
            context.version_id,
            concept_key,
            hint_level,
            timestamp,
        ),
    )
    _mark_learning(
        connection,
        context,
        concept_key,
        timestamp,
        int(cursor.lastrowid),
    )
    hint_count = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM attempts
            WHERE course_id = ? AND concept_key = ? AND event_type = 'hint'
            """,
            (context.course_id, concept_key),
        ).fetchone()[0]
    )
    return CommandResult(
        payload={
            "concept": concept_key,
            "hint_level": hint_level,
            "hint_id": int(cursor.lastrowid),
            "hints": hint_count,
            "mastery": _mastery_name(connection, context.course_id, concept_key),
            "recorded_at": timestamp,
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def record_mastery(
    connection: sqlite3.Connection,
    context: CourseContext,
    concept_key: str,
    level_name: str,
    review_in_days: int | None,
    review_result: str | None,
    now: datetime,
) -> CommandResult:
    _require_concept(connection, context, concept_key)
    level_name = MASTERY_ALIASES.get(level_name, level_name)
    if level_name not in MASTERY_LEVELS:
        raise UsageError(
            "mastery level must be not_started, in_progress, practiced, or mastered"
        )
    level = MASTERY_LEVELS[level_name]
    if review_in_days is not None and not 0 <= review_in_days <= 36_500:
        raise UsageError("review interval must be between 0 and 36500 days")
    if review_in_days is not None and review_result is not None:
        raise UsageError("review interval and review result cannot be combined")
    if review_result is not None and review_result not in {
        "again",
        "hard",
        "good",
        "easy",
    }:
        raise UsageError("review result must be again, hard, good, or easy")
    if level < MASTERY_LEVELS["practiced"] and (
        review_in_days is not None or review_result is not None
    ):
        raise UsageError("review scheduling requires practiced or mastered level")

    timestamp = format_timestamp(now)
    evidence = connection.execute(
        """
        SELECT id
        FROM attempts
        WHERE course_id = ? AND concept_key = ? AND event_type = 'attempt'
        ORDER BY id DESC
        LIMIT 1
        """,
        (context.course_id, concept_key),
    ).fetchone()
    evidence_id = None if evidence is None else int(evidence["id"])
    connection.execute(
        """
        INSERT INTO mastery(
            course_id, concept_key, level, evidence_attempt_id, updated_at
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(course_id, concept_key) DO UPDATE SET
            level = excluded.level,
            evidence_attempt_id = excluded.evidence_attempt_id,
            updated_at = excluded.updated_at
        """,
        (
            context.course_id,
            concept_key,
            level,
            evidence_id,
            timestamp,
        ),
    )

    if level < MASTERY_LEVELS["practiced"]:
        connection.execute(
            "DELETE FROM reviews WHERE course_id = ? AND concept_key = ?",
            (context.course_id, concept_key),
        )
    else:
        _schedule_review(
            connection,
            context.course_id,
            concept_key,
            review_in_days,
            review_result,
            now,
        )
    review = _review_payload(connection, context.course_id, concept_key)
    return CommandResult(
        payload={
            "concept": concept_key,
            "mastery": level_name,
            "recorded_at": timestamp,
            "review": review,
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def _schedule_review(
    connection: sqlite3.Connection,
    course_id: int,
    concept_key: str,
    review_in_days: int | None,
    review_result: str | None,
    now: datetime,
) -> None:
    existing = connection.execute(
        """
        SELECT due_at, interval_days, ease, repetitions
        FROM reviews
        WHERE course_id = ? AND concept_key = ?
        """,
        (course_id, concept_key),
    ).fetchone()
    if existing is not None and review_in_days is None and review_result is None:
        return

    ease = 2.5 if existing is None else float(existing["ease"])
    repetitions = 0 if existing is None else int(existing["repetitions"])
    interval = 1 if existing is None else int(existing["interval_days"])
    if review_in_days is not None:
        interval = review_in_days
    elif review_result is None:
        interval = 1
    elif review_result == "again":
        interval = 1
        repetitions = 0
        ease = max(1.3, ease - 0.2)
    elif review_result == "hard":
        interval = max(1, round(interval * 1.2))
        repetitions += 1
        ease = max(1.3, ease - 0.15)
    elif review_result == "good":
        interval = (
            1
            if repetitions == 0
            else (3 if repetitions == 1 else max(1, round(interval * ease)))
        )
        repetitions += 1
    elif review_result == "easy":
        interval = 3 if repetitions == 0 else max(1, round(interval * (ease + 0.15)))
        repetitions += 1
        ease = min(3.0, ease + 0.15)

    timestamp = format_timestamp(now)
    due_at = format_timestamp(now + timedelta(days=interval))
    connection.execute(
        """
        INSERT INTO reviews(
            course_id, concept_key, due_at, interval_days,
            ease, repetitions, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id, concept_key) DO UPDATE SET
            due_at = excluded.due_at,
            interval_days = excluded.interval_days,
            ease = excluded.ease,
            repetitions = excluded.repetitions,
            updated_at = excluded.updated_at
        """,
        (
            course_id,
            concept_key,
            due_at,
            interval,
            ease,
            repetitions,
            timestamp,
        ),
    )


def _review_payload(
    connection: sqlite3.Connection,
    course_id: int,
    concept_key: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT due_at, interval_days, ease, repetitions
        FROM reviews
        WHERE course_id = ? AND concept_key = ?
        """,
        (course_id, concept_key),
    ).fetchone()
    if row is None:
        return None
    return {
        "due_at": row["due_at"],
        "ease": row["ease"],
        "interval_days": row["interval_days"],
        "repetitions": row["repetitions"],
    }


def due_reviews(
    connection: sqlite3.Connection,
    context: CourseContext,
    now: datetime,
    limit: int,
) -> CommandResult:
    if not 1 <= limit <= 1_000:
        raise UsageError("limit must be between 1 and 1000")
    timestamp = format_timestamp(now)
    rows = connection.execute(
        """
        SELECT c.concept_key, c.title, r.due_at, r.interval_days,
               r.ease, r.repetitions
        FROM reviews AS r
        JOIN concepts AS c
          ON c.course_version_id = ?
         AND c.concept_key = r.concept_key
        WHERE r.course_id = ? AND r.due_at <= ?
        ORDER BY r.due_at, c.ordinal, c.concept_key
        LIMIT ?
        """,
        (context.version_id, context.course_id, timestamp, limit),
    ).fetchall()
    reviews = [
        {
            "due_at": row["due_at"],
            "ease": row["ease"],
            "id": row["concept_key"],
            "interval_days": row["interval_days"],
            "repetitions": row["repetitions"],
            "title": row["title"],
        }
        for row in rows
    ]
    return CommandResult(
        payload={
            "as_of": timestamp,
            "commit": context.commit_sha,
            "count": len(reviews),
            "reviews": reviews,
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def unlock_solution(
    connection: sqlite3.Connection,
    context: CourseContext,
    concept_key: str,
    now: datetime,
) -> CommandResult:
    concept = _require_concept(connection, context, concept_key)
    existing = connection.execute(
        """
        SELECT reason, unlocked_at
        FROM solution_unlocks
        WHERE course_version_id = ? AND concept_key = ?
        """,
        (context.version_id, concept_key),
    ).fetchone()
    newly_unlocked = existing is None
    if existing is not None:
        reason = "already_unlocked"
        unlocked_at = existing["unlocked_at"]
    else:
        outcome_counts = connection.execute(
            """
            SELECT
                SUM(CASE
                    WHEN outcome IN ('passed', 'failed', 'error') THEN 1
                    ELSE 0
                END) AS meaningful,
                SUM(CASE WHEN outcome = 'passed' THEN 1 ELSE 0 END) AS passed
            FROM attempts
            WHERE course_version_id = ?
              AND concept_key = ?
              AND event_type = 'attempt'
            """,
            (context.version_id, concept_key),
        ).fetchone()
        meaningful_count = int(outcome_counts["meaningful"] or 0)
        passed_count = int(outcome_counts["passed"] or 0)
        required = int(concept["solution_unlock_after"])
        if passed_count:
            stored_reason = "deterministic_success"
        elif meaningful_count >= required:
            stored_reason = "post_attempt_request"
        else:
            raise ConflictError(
                "solution is locked: pass the deterministic check or make "
                f"{required} genuine attempts before requesting unlock "
                f"({meaningful_count} recorded)"
            )
        unlocked_at = format_timestamp(now)
        connection.execute(
            """
            INSERT INTO solution_unlocks(
                course_version_id, concept_key, reason, unlocked_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                context.version_id,
                concept_key,
                stored_reason,
                unlocked_at,
            ),
        )
        reason = stored_reason
    return CommandResult(
        payload={
            "concept": concept_key,
            "newly_unlocked": newly_unlocked,
            "reason": reason,
            "unlocked": True,
            "unlocked_at": unlocked_at,
            "warnings": list(context.identity.warnings),
        },
        context=context,
    )


def record_session(
    connection: sqlite3.Connection,
    context: CourseContext,
    command: str,
    now: datetime,
) -> None:
    timestamp = format_timestamp(now)
    connection.execute(
        """
        INSERT INTO sessions(
            course_id, course_version_id, command, started_at, ended_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            context.course_id,
            context.version_id,
            command,
            timestamp,
            timestamp,
        ),
    )


def build_parser() -> TutorArgumentParser:
    parser = TutorArgumentParser(prog="learning-state")
    parser.add_argument("--db", default=argparse.SUPPRESS)
    parser.add_argument(
        "--busy-timeout-ms",
        type=int,
        default=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_runtime_options(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--db", default=argparse.SUPPRESS)
        command_parser.add_argument(
            "--busy-timeout-ms",
            type=int,
            default=argparse.SUPPRESS,
        )

    def add_context_options(
        command_parser: argparse.ArgumentParser,
    ) -> None:
        add_runtime_options(command_parser)
        identity_group = command_parser.add_mutually_exclusive_group(required=True)
        identity_group.add_argument("--remote")
        identity_group.add_argument("--local-fallback")
        command_parser.add_argument("--commit", required=True)
        command_parser.add_argument("--at")

    init_parser = subparsers.add_parser("init-course")
    add_context_options(init_parser)
    init_parser.add_argument("--concepts", "--concepts-file", dest="concepts")
    init_parser.add_argument("--concepts-json")

    for name in ("status", "next-objective"):
        add_context_options(subparsers.add_parser(name))

    attempt_parser = subparsers.add_parser("record-attempt")
    add_context_options(attempt_parser)
    attempt_parser.add_argument("--concept", required=True)
    attempt_parser.add_argument("--outcome", required=True)
    attempt_parser.add_argument("--score", type=float)

    hint_parser = subparsers.add_parser("record-hint")
    add_context_options(hint_parser)
    hint_parser.add_argument("--concept", required=True)
    hint_parser.add_argument("--hint-level", type=int, default=1)

    mastery_parser = subparsers.add_parser("record-mastery")
    add_context_options(mastery_parser)
    mastery_parser.add_argument("--concept", required=True)
    mastery_group = mastery_parser.add_mutually_exclusive_group(required=True)
    mastery_group.add_argument(
        "--level",
        choices=tuple((*MASTERY_LEVELS, *MASTERY_ALIASES)),
    )
    mastery_group.add_argument(
        "--mastered",
        action="store_const",
        const="mastered",
        dest="level_flag",
    )
    mastery_group.add_argument(
        "--learning",
        action="store_const",
        const="in_progress",
        dest="level_flag",
    )
    mastery_group.add_argument(
        "--practiced",
        action="store_const",
        const="practiced",
        dest="level_flag",
    )
    mastery_group.add_argument(
        "--reset",
        action="store_const",
        const="not_started",
        dest="level_flag",
    )
    mastery_parser.add_argument("--review-in-days", type=int)
    mastery_parser.add_argument("--review-result")

    reviews_parser = subparsers.add_parser("due-reviews")
    add_context_options(reviews_parser)
    reviews_parser.add_argument("--limit", type=int, default=50)

    unlock_parser = subparsers.add_parser("unlock-solution")
    add_context_options(unlock_parser)
    unlock_parser.add_argument("--concept", required=True)
    return parser


def _database_path(args: argparse.Namespace) -> Path:
    explicit = getattr(args, "db", None)
    return Path(explicit).expanduser() if explicit else default_db_path()


def _busy_timeout(args: argparse.Namespace) -> int:
    explicit = getattr(args, "busy_timeout_ms", None)
    if explicit is not None:
        return explicit
    raw = os.environ.get(
        BUSY_TIMEOUT_ENV_VAR,
        str(DEFAULT_BUSY_TIMEOUT_MS),
    )
    try:
        return int(raw)
    except ValueError as exc:
        raise UsageError(f"{BUSY_TIMEOUT_ENV_VAR} must be an integer") from exc


def execute(args: argparse.Namespace) -> CommandResult:
    identity = resolve_course_identity(args.remote, args.local_fallback)
    commit_sha = normalize_commit(args.commit)
    now = parse_timestamp(args.at)
    path = _database_path(args)
    connection = connect_database(path, _busy_timeout(args))
    try:
        with transaction(connection):
            ensure_schema(
                connection,
                allow_create=args.command == "init-course",
            )
            if args.command == "init-course":
                result = init_course(
                    connection,
                    identity,
                    commit_sha,
                    load_concepts(args.concepts, args.concepts_json),
                    now,
                )
            else:
                context = lookup_context(
                    connection,
                    identity,
                    commit_sha,
                )
                if args.command == "status":
                    result = status(connection, context)
                elif args.command == "next-objective":
                    result = next_objective(connection, context)
                elif args.command == "record-attempt":
                    result = record_attempt(
                        connection,
                        context,
                        args.concept,
                        args.outcome,
                        args.score,
                        now,
                    )
                elif args.command == "record-hint":
                    result = record_hint(
                        connection,
                        context,
                        args.concept,
                        args.hint_level,
                        now,
                    )
                elif args.command == "record-mastery":
                    level = args.level or args.level_flag
                    result = record_mastery(
                        connection,
                        context,
                        args.concept,
                        level,
                        args.review_in_days,
                        args.review_result,
                        now,
                    )
                elif args.command == "due-reviews":
                    result = due_reviews(
                        connection,
                        context,
                        now,
                        args.limit,
                    )
                elif args.command == "unlock-solution":
                    result = unlock_solution(
                        connection,
                        context,
                        args.concept,
                        now,
                    )
                else:
                    raise UsageError(f"unknown command: {args.command}")
            record_session(connection, result.context, args.command, now)
            return result
    except sqlite3.Error as exc:
        raise _translate_sqlite_error(exc) from exc
    finally:
        connection.close()


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        result = execute(args)
        for warning in result.context.identity.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        print(compact_json(result.payload))
        return EXIT_OK
    except TutorError as exc:
        print(f"error[{exc.category}]: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
