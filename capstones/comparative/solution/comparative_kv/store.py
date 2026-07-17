"""SQLite persistence for the comparative key/value store."""

from __future__ import annotations

import re
import sqlite3
import time
from collections.abc import Sequence
from os import PathLike
from typing import Protocol

from .domain import (
    MAX_SAFE_INTEGER,
    normalized_json,
    parse_json_value,
    parse_stored_json,
    validate_key,
)
from .errors import KvError
from .models import (
    DeleteExpectation,
    DeleteResult,
    Entry,
    JsonValue,
    ListResult,
    SetExpectation,
    SetResult,
)

BUSY_TIMEOUT_MS = 10_000
CREATE_METADATA = """
CREATE TABLE store_metadata (
    singleton       INTEGER PRIMARY KEY CHECK (singleton = 1),
    schema_version  INTEGER NOT NULL CHECK (schema_version = 1),
    global_revision INTEGER NOT NULL
                    CHECK (global_revision BETWEEN 0 AND 9007199254740991)
)
"""
CREATE_ENTRIES = """
CREATE TABLE entries (
    key        TEXT PRIMARY KEY COLLATE BINARY,
    value_json TEXT NOT NULL CHECK (json_valid(value_json)),
    revision   INTEGER NOT NULL
               CHECK (revision BETWEEN 1 AND 9007199254740991)
)
"""
INSERT_METADATA = """
INSERT INTO store_metadata(singleton, schema_version, global_revision)
VALUES (1, 1, 0)
"""
V0_ENTRIES = "createtableentries(keytextprimarykeycollatebinary,value_jsontextnotnull)"
V1_ENTRIES = (
    "createtableentries(keytextprimarykeycollatebinary,"
    "value_jsontextnotnullcheck(json_valid(value_json)),"
    "revisionintegernotnullcheck(revisionbetween1and9007199254740991))"
)
V1_METADATA = (
    "createtablestore_metadata(singletonintegerprimarykeycheck(singleton=1),"
    "schema_versionintegernotnullcheck(schema_version=1),"
    "global_revisionintegernotnullcheck("
    "global_revisionbetween0and9007199254740991))"
)


class Store(Protocol):
    """Operations required by the command boundary."""

    def set(
        self,
        key: str,
        value: JsonValue,
        expectation: SetExpectation = "any",
    ) -> SetResult: ...

    def get(self, key: str) -> Entry: ...

    def delete(
        self,
        key: str,
        expectation: DeleteExpectation = "any",
    ) -> DeleteResult: ...

    def list_entries(self) -> ListResult: ...

    def close(self) -> None: ...


class SQLiteStore:
    """Own one configured SQLite connection implementing schema version 1.

    Autocommit mode keeps transaction ownership explicit below: each compound
    operation either commits as a unit or rolls back. Construction also closes
    the connection if configuration, validation, or migration fails, so a
    successfully constructed store is the only owner expected to call
    :meth:`close`.
    """

    def __init__(self, path: str | PathLike[str]):
        self.path = str(path)
        try:
            self.connection = sqlite3.connect(
                self.path,
                timeout=BUSY_TIMEOUT_MS / 1000,
                # Multi-statement guarantees below use explicit BEGIN/commit.
                isolation_level=None,
                uri=False,
            )
        except sqlite3.Error as error:
            raise _map_sql(error, "open") from error
        try:
            # The driver timeout and PRAGMA both ask SQLite to wait for ordinary
            # lock contention. Changing journal mode needs its own bounded retry
            # because competing openers can race while configuring the database.
            self.connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
            _configure_journal_mode(self.connection)
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as error:
            self.connection.close()
            raise _map_sql(error, "configure") from error
        except KvError:
            self.connection.close()
            raise

        try:
            self._prepare_schema()
        except BaseException:
            self.connection.close()
            raise

    def close(self) -> None:
        """Close the SQLite connection owned by this store."""

        self.connection.close()

    def set(
        self,
        key: str,
        value: JsonValue,
        expectation: SetExpectation = "any",
    ) -> SetResult:
        """Create or replace a value subject to a compare-and-set expectation.

        ``"any"`` performs no revision comparison, ``"absent"`` requires no
        current row, and an integer must exactly match the current revision.
        The comparison, row mutation, and global revision update share one
        transaction, so a losing comparison cannot partially write.
        """

        operation = "write"
        try:
            # Reserve the single SQLite writer before observing CAS state. This
            # prevents another writer from changing the row or revision counter
            # between the comparison and mutation; it does not promise fairness.
            self.connection.execute("BEGIN IMMEDIATE")
            row = self.connection.execute(
                "SELECT revision FROM entries WHERE key = ? COLLATE BINARY",
                (key,),
            ).fetchone()
            current = None if row is None else _stored_int(row[0])
            if expectation == "absent" and current is not None:
                raise KvError(
                    "conflict",
                    {"key": key, "expected": "absent", "actual": current},
                    3,
                )
            if isinstance(expectation, int) and current != expectation:
                raise KvError(
                    "conflict",
                    {"key": key, "expected": expectation, "actual": current},
                    3,
                )
            revision = self._next_revision()
            self.connection.execute(
                """
                INSERT INTO entries(key, value_json, revision)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json = excluded.value_json,
                    revision = excluded.revision
                """,
                (key, normalized_json(value), revision),
            )
            self._update_global_revision(revision)
            operation = "commit"
            self.connection.commit()
            return SetResult(Entry(key, value, revision), current is None)
        except KvError:
            self._rollback()
            raise
        except sqlite3.Error as error:
            self._rollback()
            raise _map_sql(error, operation) from error

    def get(self, key: str) -> Entry:
        try:
            row = self.connection.execute(
                """
                SELECT value_json, revision
                FROM entries
                WHERE key = ? COLLATE BINARY
                """,
                (key,),
            ).fetchone()
        except sqlite3.Error as error:
            raise _map_sql(error, "read") from error
        if row is None:
            raise KvError("not_found", {"key": key}, 4)
        try:
            value = parse_stored_json(_stored_text(row[0]))
            revision = _positive_revision(row[1])
        except KvError as error:
            if error.category == "invalid_value":
                raise KvError(
                    "invalid_storage",
                    {"reason": "invalid_value", "key": key},
                    5,
                ) from error
            raise
        return Entry(key, value, revision)

    def delete(
        self,
        key: str,
        expectation: DeleteExpectation = "any",
    ) -> DeleteResult:
        """Delete an existing value with optional exact-revision CAS.

        ``"any"`` accepts whichever existing revision is read; an integer must
        match it exactly. Unlike ``set(..., "absent")``, deletion always requires
        a row, so a missing key is ``not_found`` rather than a CAS success.
        """

        operation = "write"
        try:
            # As in set(), acquire the writer before reading the compared value.
            self.connection.execute("BEGIN IMMEDIATE")
            row = self.connection.execute(
                "SELECT revision FROM entries WHERE key = ? COLLATE BINARY",
                (key,),
            ).fetchone()
            if row is None:
                raise KvError("not_found", {"key": key}, 4)
            current = _positive_revision(row[0])
            if isinstance(expectation, int) and current != expectation:
                raise KvError(
                    "conflict",
                    {"key": key, "expected": expectation, "actual": current},
                    3,
                )
            revision = self._next_revision()
            self.connection.execute(
                "DELETE FROM entries WHERE key = ? COLLATE BINARY",
                (key,),
            )
            self._update_global_revision(revision)
            operation = "commit"
            self.connection.commit()
            return DeleteResult(key, current, revision)
        except KvError:
            self._rollback()
            raise
        except sqlite3.Error as error:
            self._rollback()
            raise _map_sql(error, operation) from error

    def list_entries(self) -> ListResult:
        try:
            # One explicit read transaction keeps the metadata revision and entry
            # rows on the same SQLite snapshot if another process commits between
            # the two SELECT statements.
            self.connection.execute("BEGIN")
            metadata = self.connection.execute(
                """
                SELECT global_revision
                FROM store_metadata
                WHERE singleton = 1
                """
            ).fetchone()
            if metadata is None:
                raise _malformed_schema()
            global_revision = _stored_int(metadata[0])
            rows = self.connection.execute(
                """
                SELECT key, value_json, revision
                FROM entries
                ORDER BY key COLLATE BINARY
                """
            ).fetchall()
            entries = tuple(self._entry_from_row(row) for row in rows)
            self.connection.commit()
            return ListResult(entries, global_revision)
        except KvError:
            self._rollback()
            raise
        except sqlite3.Error as error:
            self._rollback()
            raise _map_sql(error, "read") from error

    def _entry_from_row(self, row: Sequence[object]) -> Entry:
        key = _stored_text(row[0])
        try:
            value = parse_stored_json(_stored_text(row[1]))
        except KvError as error:
            raise KvError(
                "invalid_storage",
                {"reason": "invalid_value", "key": key},
                5,
            ) from error
        return Entry(key, value, _positive_revision(row[2]))

    def _prepare_schema(self) -> None:
        """Validate and prepare exactly one recognized on-disk schema.

        The immediate transaction serializes initialization or migration with
        other writers. A limited future-version probe precedes the integrity
        check; integrity is checked before migration or acceptance of a supported
        schema. Object definitions and reserved PRAGMAs then distinguish a
        supported layout from a merely queryable but incompatible database.
        """

        operation = "initialize"
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            objects = self._application_objects()
            # Probe a readable metadata table first so a future version gets the
            # more precise unsupported_schema error. Strict shape validation
            # still follows; a failed or ambiguous probe grants no compatibility.
            future = self._future_schema_version(objects)
            if future is not None and future > 1:
                raise KvError(
                    "unsupported_schema",
                    {"found": future, "supported": 1},
                    5,
                )
            self._ensure_integrity()
            kind = _schema_kind(objects)
            self._validate_default_pragmas()
            if kind == "fresh":
                self._initialize()
            elif kind == "v0":
                operation = "migrate"
                self._migrate_v0()
            elif kind == "v1":
                operation = "read"
                self._validate_v1()
            else:
                raise _malformed_schema()
            operation = "commit"
            self.connection.commit()
        except KvError:
            self._rollback()
            raise
        except sqlite3.Error as error:
            self._rollback()
            raise _map_sql(error, operation) from error

    def _application_objects(self) -> list[tuple[str, str, str | None]]:
        """Return every non-internal object used for strict schema recognition."""

        rows = self.connection.execute(
            """
            SELECT type, name, sql
            FROM sqlite_schema
            WHERE name NOT LIKE 'sqlite_%'
            ORDER BY type COLLATE BINARY, name COLLATE BINARY
            """
        ).fetchall()
        return [
            (str(row[0]), str(row[1]), None if row[2] is None else str(row[2]))
            for row in rows
        ]

    def _future_schema_version(
        self,
        objects: Sequence[tuple[str, str, str | None]],
    ) -> int | None:
        if not any(
            kind == "table" and name == "store_metadata" for kind, name, _ in objects
        ):
            return None
        try:
            row = self.connection.execute(
                "SELECT schema_version FROM store_metadata LIMIT 1"
            ).fetchone()
        except sqlite3.Error:
            return None
        if row is None or not isinstance(row[0], int):
            return None
        return row[0]

    def _ensure_integrity(self) -> None:
        """Require SQLite's full database integrity check to report only ``ok``."""

        rows = self.connection.execute("PRAGMA integrity_check").fetchall()
        if [str(row[0]) for row in rows] != ["ok"]:
            raise KvError(
                "invalid_storage",
                {"reason": "integrity_check_failed"},
                5,
            )

    def _validate_default_pragmas(self) -> None:
        """Reject files using version/application markers outside this format."""

        user_version = self.connection.execute("PRAGMA user_version").fetchone()
        application_id = self.connection.execute("PRAGMA application_id").fetchone()
        if (
            user_version is None
            or application_id is None
            or user_version[0] != 0
            or application_id[0] != 0
        ):
            raise _malformed_schema()

    def _initialize(self) -> None:
        self.connection.execute(CREATE_METADATA)
        self.connection.execute(CREATE_ENTRIES)
        self.connection.execute(INSERT_METADATA)

    def _migrate_v0(self) -> None:
        """Atomically replace the recognized v0 table with the v1 schema.

        Every legacy key/value is validated before DDL begins. Values are parsed
        and serialized again into the current compact normalized JSON form, then
        keys in binary order receive revisions ``1..N``. The sole metadata row
        records schema version 1 and global revision ``N``.

        All rename/create/copy/drop steps run inside the caller's SQLite
        transaction, so an aborted transaction that rolls back does not expose
        a half-migration. The guarantee covers this database only, not external
        files or cross-filesystem work.
        """

        rows = self.connection.execute(
            """
            SELECT key, value_json
            FROM entries
            ORDER BY key COLLATE BINARY
            """
        ).fetchall()
        normalized: list[tuple[str, str]] = []
        for row in rows:
            key = _stored_text(row[0])
            try:
                validate_key(key)
            except KvError as error:
                raise KvError(
                    "invalid_storage",
                    {"reason": "invalid_key", "key": key},
                    5,
                ) from error
            try:
                value = parse_json_value(_stored_text(row[1]))
            except KvError as error:
                raise KvError(
                    "invalid_storage",
                    {"reason": "invalid_value", "key": key},
                    5,
                ) from error
            normalized.append((key, normalized_json(value)))

        self.connection.execute("ALTER TABLE entries RENAME TO entries_v0_migration")
        self.connection.execute(CREATE_METADATA)
        self.connection.execute(CREATE_ENTRIES)
        self.connection.execute(INSERT_METADATA)
        for revision, (key, value_json) in enumerate(normalized, start=1):
            self.connection.execute(
                """
                INSERT INTO entries(key, value_json, revision)
                VALUES (?, ?, ?)
                """,
                (key, value_json, revision),
            )
        self.connection.execute(
            """
            UPDATE store_metadata
            SET global_revision = ?
            WHERE singleton = 1
            """,
            (len(normalized),),
        )
        self.connection.execute("DROP TABLE entries_v0_migration")

    def _validate_v1(self) -> None:
        """Check metadata cardinality and all persisted v1 value/revision rules.

        The singleton metadata row is the database-wide revision authority.
        Live entry revisions must be positive, unique, and no newer than that
        counter; deleted revisions are intentionally absent from ``entries``.
        """

        metadata_rows = self.connection.execute(
            """
            SELECT singleton, schema_version, global_revision
            FROM store_metadata
            """
        ).fetchall()
        if len(metadata_rows) != 1:
            raise _malformed_schema()
        singleton, schema_version, stored_global = metadata_rows[0]
        if singleton != 1 or schema_version != 1:
            raise _malformed_schema()
        if not isinstance(stored_global, int) or not (
            0 <= stored_global <= MAX_SAFE_INTEGER
        ):
            raise _revision_invariant()
        global_revision = stored_global

        seen_revisions: set[int] = set()
        rows = self.connection.execute(
            """
            SELECT key, value_json, revision
            FROM entries
            ORDER BY key COLLATE BINARY
            """
        ).fetchall()
        for row in rows:
            key = _stored_text(row[0])
            try:
                validate_key(key)
            except KvError as error:
                raise KvError(
                    "invalid_storage",
                    {"reason": "invalid_key", "key": key},
                    5,
                ) from error
            try:
                parse_stored_json(_stored_text(row[1]))
            except KvError as error:
                raise KvError(
                    "invalid_storage",
                    {"reason": "invalid_value", "key": key},
                    5,
                ) from error
            revision = _stored_int(row[2])
            if not 1 <= revision <= global_revision or revision in seen_revisions:
                raise _revision_invariant()
            seen_revisions.add(revision)

    def _next_revision(self) -> int:
        """Return the next database-wide mutation revision.

        Callers hold an IMMEDIATE write transaction, so SQLite serializes this
        read with other writers. Successful mutations therefore publish a
        strictly increasing order across sets and deletes in this database.
        This database lock is not a general-purpose process synchronizer.

        The safe-integer ceiling is checked before mutation, so conflicts and
        exhaustion consume nothing. Later failures use best-effort rollback;
        when SQLite rolls the transaction back, neither the row change nor its
        revision is counted. No stronger accounting guarantee is possible if
        SQLite cannot roll back or the commit outcome itself is indeterminate.
        """

        row = self.connection.execute(
            """
            SELECT global_revision
            FROM store_metadata
            WHERE singleton = 1
            """
        ).fetchone()
        if row is None:
            raise _malformed_schema()
        current = _stored_int(row[0])
        if current >= MAX_SAFE_INTEGER:
            raise KvError(
                "revision_exhausted",
                {"maximum": MAX_SAFE_INTEGER},
                5,
            )
        return current + 1

    def _update_global_revision(self, revision: int) -> None:
        """Publish an allocated revision through the required singleton row."""

        cursor = self.connection.execute(
            """
            UPDATE store_metadata
            SET global_revision = ?
            WHERE singleton = 1
            """,
            (revision,),
        )
        if cursor.rowcount != 1:
            raise _malformed_schema()

    def _rollback(self) -> None:
        """Best-effort rollback without replacing the operation's real error."""

        if self.connection.in_transaction:
            try:
                self.connection.rollback()
            except sqlite3.Error:
                pass


def open_store(path: str | PathLike[str]) -> Store:
    """Open, configure, initialize or migrate, and validate one SQLite store."""

    return SQLiteStore(path)


def _schema_kind(objects: Sequence[tuple[str, str, str | None]]) -> str:
    """Classify schemas after the limited ``_canonical_sql`` normalization.

    Fresh means no application objects at all. Known v0/v1 definitions must
    normalize to the expected templates; extra objects and other definitions are
    malformed. This is not byte-exact or a full semantic DDL validation.
    """

    if not objects:
        return "fresh"
    if len(objects) == 1:
        kind, name, sql = objects[0]
        if (
            kind == "table"
            and name == "entries"
            and sql is not None
            and _canonical_sql(sql) == V0_ENTRIES
        ):
            return "v0"
    if len(objects) == 2:
        by_name = {name: (kind, sql) for kind, name, sql in objects}
        entries = by_name.get("entries")
        metadata = by_name.get("store_metadata")
        if (
            entries is not None
            and metadata is not None
            and entries[0] == metadata[0] == "table"
            and entries[1] is not None
            and metadata[1] is not None
            and _canonical_sql(entries[1]) == V1_ENTRIES
            and _canonical_sql(metadata[1]) == V1_METADATA
        ):
            return "v1"
    return "malformed"


def _canonical_sql(sql: str) -> str:
    """Normalize superficial formatting for comparison with known schema SQL.

    Case, whitespace, and SQLite identifier quoting are ignored. This is a
    narrow comparison against fixed CREATE TABLE templates, not a general SQL
    parser or a claim that arbitrary statements are semantically equivalent.
    """

    return re.sub(r"""[\s"'`\[\]]+""", "", sql).lower()


def _stored_text(value: object) -> str:
    if not isinstance(value, str):
        raise _malformed_schema()
    return value


def _stored_int(value: object) -> int:
    if not isinstance(value, int):
        raise _revision_invariant()
    return value


def _positive_revision(value: object) -> int:
    revision = _stored_int(value)
    if not 1 <= revision <= MAX_SAFE_INTEGER:
        raise _revision_invariant()
    return revision


def _storage_error(operation: str) -> KvError:
    return KvError(
        "storage_error",
        {"operation": operation, "reason": "storage_failure"},
        5,
    )


def _malformed_schema() -> KvError:
    return KvError("invalid_storage", {"reason": "malformed_schema"}, 5)


def _revision_invariant() -> KvError:
    return KvError("invalid_storage", {"reason": "revision_invariant"}, 5)


def _map_sql(error: sqlite3.Error, operation: str) -> KvError:
    """Map stable SQLite codes, with messages as compatibility fallbacks.

    BUSY/LOCKED contention becomes the public ``busy`` category. Ordinary BUSY
    handling may wait via ``busy_timeout``; journal-mode setup additionally has
    its explicit deadline. Recognized corruption/not-a-database failures become
    ``invalid_storage``; all other SQLite failures retain only the coarse
    operation name, avoiding dependence on unstable engine text.
    """

    code = getattr(error, "sqlite_errorcode", None)
    corrupt_codes = {
        sqlite3.SQLITE_CORRUPT,
        sqlite3.SQLITE_NOTADB,
    }
    message = str(error).lower()
    if _is_busy(error):
        return KvError("busy", {"timeout_ms": BUSY_TIMEOUT_MS}, 5)
    if code in corrupt_codes or "not a database" in message or "malformed" in message:
        return KvError(
            "invalid_storage",
            {"reason": "integrity_check_failed"},
            5,
        )
    return _storage_error(operation)


def _configure_journal_mode(connection: sqlite3.Connection) -> None:
    """Request WAL mode, retrying only recognized contention until the deadline.

    WAL permits readers and a writer to overlap more often, but SQLite still has
    one writer and offers no fairness guarantee. This verifies the mode SQLite
    reports; it does not strengthen crash durability beyond the database's
    synchronous setting and filesystem behavior.
    """

    deadline = time.monotonic() + BUSY_TIMEOUT_MS / 1000
    while True:
        try:
            row = connection.execute("PRAGMA journal_mode = WAL").fetchone()
            if row is None or str(row[0]).lower() != "wal":
                raise _storage_error("configure")
            return
        except sqlite3.Error as error:
            if not _is_busy(error) or time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


def _is_busy(error: sqlite3.Error) -> bool:
    """Recognize lock contention by SQLite code or legacy driver message."""

    code = getattr(error, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or (
        "database is locked" in str(error).lower()
    )
