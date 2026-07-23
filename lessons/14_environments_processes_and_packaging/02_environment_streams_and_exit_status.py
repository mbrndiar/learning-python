"""
Chapter 14, Lesson 2: Environment, Standard Streams, and Exit Status

Purpose: read process configuration from environment variables without
displaying secrets, understand the three standard streams (stdin, stdout,
stderr), and report success or failure through an integer exit status.

Prerequisites: Chapter 7 (exceptions) and Chapter 13 (argparse boundaries).
A process reads input from stdin, writes normal results to stdout, writes
diagnostics to stderr, and returns an integer status where zero means
success.

Run it from the repository root; it is noninteractive and does not read
stdin:

    python lessons/14_environments_processes_and_packaging/02_environment_streams_and_exit_status.py
"""

import os
import sys
from collections.abc import Mapping, Sequence

TOKEN_VARIABLE = "LEARNING_PYTHON_API_TOKEN"


# Step 1: environment variables are process configuration. Validate an
# optional secret WITHOUT returning or printing its value. The function
# reads from a supplied mapping, so a test can pass its own dict instead of
# mutating the real os.environ.
def token_is_configured(environment: Mapping[str, str]) -> bool:
    """Report whether a valid token is present, never revealing its value."""
    token = environment.get(TOKEN_VARIABLE)
    if token is None:
        return False
    if token != token.strip() or len(token) < 8:
        # The message names the variable and the rule, never the value.
        raise ValueError(f"{TOKEN_VARIABLE} must contain at least 8 characters")
    return True


# Step 2: an application boundary that maps outcomes to an exit status.
# stdout carries results a caller might parse; stderr carries diagnostics a
# human reads. Passing argv explicitly keeps the boundary testable.
def main(
    argv: Sequence[str] | None = None,
    *,
    environment: Mapping[str, str],
) -> int:
    """Run the lesson and return the process exit status."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments:
        # Usage errors are diagnostics: write to stderr, return status 2.
        print("usage: 02_environment_streams_and_exit_status.py", file=sys.stderr)
        return 2

    try:
        configured = token_is_configured(environment)
    except ValueError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2

    # Step 3: send each kind of output to the correct stream.
    print(f"{TOKEN_VARIABLE} configured: {configured}")
    print("stdin supplies input; this noninteractive lesson does not read it.")
    print("stdout carries normal program results.")
    print("stderr carries diagnostics.", file=sys.stderr)

    # Step 4: the return value becomes the process exit status. Zero means
    # success; a shell, CI job, or parent process reads it to decide what to
    # do next.
    print("Returning exit status 0 (zero means success).")
    return 0


def run_from_process(argv: Sequence[str] | None = None) -> int:
    """The real application boundary delegates with the ambient environment."""
    return main(argv, environment=os.environ)


if __name__ == "__main__":
    # Use a fixed mapping so the lesson's output and exit status cannot be
    # changed by an ambient variable on the learner's machine or in CI. A real
    # application would call run_from_process(); try that as an experiment.
    raise SystemExit(main(environment={}))
