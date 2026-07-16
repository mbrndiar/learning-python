"""Wait for the parent barrier, then replace this process with the CLI."""

import os
import sys

if not sys.stdin.buffer.read(1):
    raise SystemExit("barrier closed before release")

os.execvpe(sys.argv[1], sys.argv[1:], os.environ)
