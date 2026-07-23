# 📦 Starter distribution: console script entry point

A deliberately small `src/`-layout distribution for the Chapter 14 packaging
task. It exposes one public callable, `timekeeper_cli.main`.

Your job: edit `pyproject.toml` and add a `[project.scripts]` table that maps
the console command `timekeeper` to the callable `timekeeper_cli:main`. When
you do, the exercise evaluator (`python exercises/14_environments_processes_and_packaging/exercises.py`)
will parse the file with `tomllib`, resolve the entry point, and confirm the
callable exists.

You do not need to install or build anything; the evaluator verifies the
metadata offline.
