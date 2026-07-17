"""Translate the CLI's returned status into the process exit status."""

from .cli import main

# Keeping process termination here lets ``cli.main`` remain directly testable
# without raising, while ``python -m ingest_report`` still exposes exact exits.
raise SystemExit(main())
