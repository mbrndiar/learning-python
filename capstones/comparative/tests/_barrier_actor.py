"""Wait for parent release, then replace this barrier actor with the real CLI.

The one-byte stdin protocol lets the harness create every actor before releasing
them.  ``exec`` preserves the actor PID and pipes while ensuring the observed
exit status and output belong to the CLI rather than to a Python wrapper.
"""

import os
import sys

if not sys.stdin.buffer.read(1):
    raise SystemExit("barrier closed before release")

# Forward the exact argument vector and environment selected by the harness.
os.execvpe(sys.argv[1], sys.argv[1:], os.environ)
