"""Hold an independent SQLite write reservation until the parent releases it.

``BEGIN IMMEDIATE`` acquires SQLite's write transaction up front.  The ready
file is written only after that succeeds, so the parent can distinguish a held
lock from a helper process that merely started.  Stdin then provides an explicit
release handshake without changing the database.
"""

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
    # Rollback releases the reservation while preserving the fixture's state.
    connection.rollback()
finally:
    connection.close()
