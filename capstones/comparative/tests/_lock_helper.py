"""Hold one independent SQLite immediate transaction until released."""

import sqlite3
import sys
from pathlib import Path

database = sys.argv[1]
ready = Path(sys.argv[2])
connection = sqlite3.connect(database, timeout=10, isolation_level=None)
try:
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("BEGIN IMMEDIATE")
    ready.write_text("ready\n", encoding="utf-8")
    if not sys.stdin.buffer.read(1):
        raise SystemExit("release channel closed")
    connection.rollback()
finally:
    connection.close()
