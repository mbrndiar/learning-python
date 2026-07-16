"""Versioned SQLite persistence for events, rejects, imports, and reports."""

import json
import sqlite3
from collections.abc import Iterable, Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from .errors import ApplicationError
from .models import (
    CategorySummary,
    Event,
    ImportResult,
    ImportState,
    RejectedRecord,
    RejectSummary,
    Report,
    ReportFilters,
    ReportTotals,
    SourceKind,
    Status,
    StatusSummary,
)
from .validation import validate_import_id

SCHEMA_VERSION = 1
APPLICATION_ID = 0x49525031
EXPECTED_COLUMNS = {
    "imports": {
        "import_id",
        "source_kind",
        "source_name",
        "started_at",
        "state",
        "accepted",
        "duplicates",
        "rejected",
        "failed_pages",
    },
    "events": {
        "source",
        "event_id",
        "occurred_at",
        "category",
        "duration_ms",
        "status",
        "import_id",
    },
    "rejects": {
        "reject_id",
        "import_id",
        "source_name",
        "record_number",
        "code",
        "field",
        "message",
        "raw_json",
    },
    "import_page_issues": {"import_id", "page_number", "code", "message"},
}


class SQLiteEventRepository:
    """Own short SQLite connections and atomic streaming imports."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        try:
            with closing(self._connect()) as connection:
                self._initialize_or_validate(connection)
        except ApplicationError:
            raise
        except sqlite3.Error as error:
            raise self._database_error(error) from error

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _database_error(error: BaseException | str) -> ApplicationError:
        return ApplicationError(
            "database_error",
            f"database operation failed: {error}",
            5,
        )

    @staticmethod
    def _table_names(connection: sqlite3.Connection) -> set[str]:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()
        return {str(row["name"]) for row in rows}

    def _initialize_or_validate(self, connection: sqlite3.Connection) -> None:
        check = connection.execute("PRAGMA quick_check").fetchone()
        if check is None or str(check[0]) != "ok":
            raise self._database_error("SQLite integrity check failed")
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        tables = self._table_names(connection)
        if version == 0 and not tables:
            self._create_schema(connection)
            return
        if version != SCHEMA_VERSION:
            raise ApplicationError(
                "unsupported_schema",
                f"database schema version {version} is unsupported; expected 1",
                5,
                {"found": version, "supported": SCHEMA_VERSION},
            )
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        if application_id != APPLICATION_ID:
            raise self._database_error("database application identifier is invalid")
        if tables != set(EXPECTED_COLUMNS):
            raise self._database_error("database schema tables are malformed")
        for table, expected in EXPECTED_COLUMNS.items():
            rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
            actual = {str(row["name"]) for row in rows}
            if actual != expected:
                raise self._database_error(
                    f"database schema for table {table!r} is malformed"
                )

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        with connection:
            connection.executescript(
                f"""
                CREATE TABLE imports (
                    import_id TEXT PRIMARY KEY,
                    source_kind TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    state TEXT NOT NULL CHECK (state IN ('complete', 'partial')),
                    accepted INTEGER NOT NULL,
                    duplicates INTEGER NOT NULL,
                    rejected INTEGER NOT NULL,
                    failed_pages TEXT NOT NULL
                );

                CREATE TABLE events (
                    source TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    import_id TEXT NOT NULL REFERENCES imports(import_id),
                    PRIMARY KEY (source, event_id)
                );

                CREATE TABLE rejects (
                    reject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_id TEXT NOT NULL REFERENCES imports(import_id),
                    source_name TEXT NOT NULL,
                    record_number INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    field TEXT,
                    message TEXT NOT NULL,
                    raw_json TEXT NOT NULL
                );

                CREATE TABLE import_page_issues (
                    import_id TEXT NOT NULL REFERENCES imports(import_id),
                    page_number INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    message TEXT NOT NULL,
                    PRIMARY KEY (import_id, page_number)
                );

                PRAGMA application_id = {APPLICATION_ID};
                PRAGMA user_version = {SCHEMA_VERSION};
                """
            )

    def _checked_connection(self) -> sqlite3.Connection:
        connection = self._connect()
        try:
            self._initialize_or_validate(connection)
        except BaseException:
            connection.close()
            raise
        return connection

    @staticmethod
    def _stored_time(value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ApplicationError(
                "database_error",
                "Clock.now() must return an offset-aware datetime",
                5,
            )
        return (
            value.astimezone(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )

    def import_records(
        self,
        *,
        import_id: str,
        source_kind: SourceKind,
        source_name: str,
        started_at: datetime,
        records: Iterable[Event | RejectedRecord],
        failed_pages: Sequence[int] = (),
    ) -> ImportResult:
        """Atomically store one import while preserving first event identity."""

        validate_import_id(import_id)
        pages = tuple(sorted(set(failed_pages)))
        state: ImportState = "partial" if pages else "complete"
        try:
            with closing(self._checked_connection()) as connection:
                connection.execute("BEGIN IMMEDIATE")
                try:
                    exists = connection.execute(
                        "SELECT 1 FROM imports WHERE import_id = ?",
                        (import_id,),
                    ).fetchone()
                    if exists is not None:
                        raise ApplicationError(
                            "import_exists",
                            f"import_id {import_id!r} already exists",
                            5,
                            {"import_id": import_id},
                        )
                    connection.execute(
                        """
                        INSERT INTO imports (
                            import_id, source_kind, source_name, started_at, state,
                            accepted, duplicates, rejected, failed_pages
                        ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?)
                        """,
                        (
                            import_id,
                            source_kind,
                            source_name,
                            self._stored_time(started_at),
                            state,
                            json.dumps(pages, separators=(",", ":")),
                        ),
                    )
                    accepted = duplicates = rejected = 0
                    for record in records:
                        if isinstance(record, Event):
                            cursor = connection.execute(
                                """
                                INSERT OR IGNORE INTO events (
                                    source, event_id, occurred_at, category,
                                    duration_ms, status, import_id
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    record.source,
                                    record.id,
                                    record.occurred_at,
                                    record.category,
                                    record.duration_ms,
                                    record.status,
                                    import_id,
                                ),
                            )
                            if cursor.rowcount == 1:
                                accepted += 1
                            else:
                                duplicates += 1
                        else:
                            connection.execute(
                                """
                                INSERT INTO rejects (
                                    import_id, source_name, record_number, code,
                                    field, message, raw_json
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    import_id,
                                    record.source_name,
                                    record.record_number,
                                    record.code,
                                    record.field,
                                    record.message,
                                    json.dumps(
                                        dict(record.raw),
                                        ensure_ascii=False,
                                        sort_keys=True,
                                        separators=(",", ":"),
                                    ),
                                ),
                            )
                            rejected += 1
                    for page in pages:
                        connection.execute(
                            """
                            INSERT INTO import_page_issues (
                                import_id, page_number, code, message
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (
                                import_id,
                                page,
                                "page_fetch_failed",
                                "HTTP page could not be imported",
                            ),
                        )
                    connection.execute(
                        """
                        UPDATE imports
                        SET accepted = ?, duplicates = ?, rejected = ?
                        WHERE import_id = ?
                        """,
                        (accepted, duplicates, rejected, import_id),
                    )
                    connection.commit()
                except BaseException:
                    connection.rollback()
                    raise
        except ApplicationError:
            raise
        except sqlite3.Error as error:
            raise self._database_error(error) from error
        return ImportResult(
            import_id,
            state,
            accepted,
            duplicates,
            rejected,
            pages,
        )

    def report(self, filters: ReportFilters) -> Report:
        """Query deterministic aggregates with inclusive AND-combined filters."""

        if (
            filters.from_timestamp is not None
            and filters.to_timestamp is not None
            and filters.from_timestamp > filters.to_timestamp
        ):
            raise ApplicationError(
                "invalid_filter",
                "from timestamp must not be later than to timestamp",
                2,
            )
        clauses: list[str] = []
        parameters: list[str] = []
        if filters.from_timestamp is not None:
            clauses.append("occurred_at >= ?")
            parameters.append(filters.from_timestamp)
        if filters.to_timestamp is not None:
            clauses.append("occurred_at <= ?")
            parameters.append(filters.to_timestamp)
        if filters.category is not None:
            clauses.append("category = ?")
            parameters.append(filters.category)
        if filters.status is not None:
            clauses.append("status = ?")
            parameters.append(filters.status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        try:
            with closing(self._checked_connection()) as connection:
                totals_row = connection.execute(
                    f"""
                    SELECT COUNT(*) AS events,
                           COALESCE(SUM(duration_ms), 0) AS duration_ms
                    FROM events {where}
                    """,
                    parameters,
                ).fetchone()
                category_rows = connection.execute(
                    f"""
                    SELECT category, COUNT(*) AS events,
                           COALESCE(SUM(duration_ms), 0) AS duration_ms
                    FROM events {where}
                    GROUP BY category
                    """,
                    parameters,
                ).fetchall()
                status_rows = connection.execute(
                    f"""
                    SELECT status, COUNT(*) AS events,
                           COALESCE(SUM(duration_ms), 0) AS duration_ms
                    FROM events {where}
                    GROUP BY status
                    """,
                    parameters,
                ).fetchall()
                reject_total = int(
                    connection.execute("SELECT COUNT(*) FROM rejects").fetchone()[0]
                )
                reject_rows = connection.execute(
                    "SELECT code, COUNT(*) AS count FROM rejects GROUP BY code"
                ).fetchall()
        except ApplicationError:
            raise
        except sqlite3.Error as error:
            raise self._database_error(error) from error

        assert totals_row is not None
        categories = sorted(
            (
                CategorySummary(
                    str(row["category"]),
                    int(row["events"]),
                    int(row["duration_ms"]),
                )
                for row in category_rows
            ),
            key=lambda item: item.category,
        )
        statuses = sorted(
            (
                StatusSummary(
                    cast(Status, str(row["status"])),
                    int(row["events"]),
                    int(row["duration_ms"]),
                )
                for row in status_rows
            ),
            key=lambda item: item.status,
        )
        rejects = sorted(
            (RejectSummary(str(row["code"]), int(row["count"])) for row in reject_rows),
            key=lambda item: item.code,
        )
        return Report(
            filters=filters,
            totals=ReportTotals(
                int(totals_row["events"]),
                int(totals_row["duration_ms"]),
                reject_total,
            ),
            by_category=tuple(categories),
            by_status=tuple(statuses),
            rejects_by_code=tuple(rejects),
        )
