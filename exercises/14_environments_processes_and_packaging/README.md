# 🧰 Exercises: Chapter 14 - Environments, Processes, and Packaging

Practice problems for
[`lessons/14_environments_processes_and_packaging/`](../../lessons/14_environments_processes_and_packaging/README.md):
environment configuration, standard streams and exit status, safe
subprocess ownership, the automated quality gates, and packaging a
distribution with a console entry point.

Install the development dependencies first by following
[`docs/SETUP.md`](../../docs/SETUP.md).

## 🧩 Tasks in `exercises.py`

- `parse_process_timeout(environment)` - validate a `PROCESS_TIMEOUT`
  configuration value (1-30, default 5) from a supplied mapping without
  mutating ambient process state.
- `build_child_command(message)` - keep untrusted text as one subprocess
  argument and invoke the current Python interpreter without a shell.
- `run_child_process(message, environment)` - run the child with
  owned stdin (`DEVNULL`), `check=True`, captured text output, a finite
  timeout, a copied environment, and no shell.

## 📦 Packaging task (a real change)

Edit
[`starter_distribution/pyproject.toml`](starter_distribution/pyproject.toml):
add a `[project.scripts]` table that maps the console command `timekeeper`
to the supplied callable `timekeeper_cli:main`. The evaluator parses the
file with `tomllib`, resolves the entry point, imports the module from
`starter_distribution/src/`, and confirms the callable exists. No install or
network is required.

## ▶️ How to work through it

1. Read [`lessons/14_environments_processes_and_packaging/`](../../lessons/14_environments_processes_and_packaging/README.md)
   first.
2. Implement each function marked `# TODO` in `exercises.py`, then make the
   packaging change above.
3. Run the evaluator from the repository root:

   ```bash
   python exercises/14_environments_processes_and_packaging/exercises.py
   ```

   It prints `All checks passed!` once every function is implemented and the
   console entry point is declared.
4. Compare with `solutions.py` and `solution_distribution/` if you get stuck.

## 🔧 Guided quality-tool lab

The tasks above practice program design. This lab practices the surrounding
developer flow with bounded targets, without leaving broken files in the
repository.

### 1. Run the narrowest relevant test

```bash
python -m pytest lessons/12_testing/03_pytest_assertions_parameterization_and_fixtures.py -v
```

Notice how [pytest](https://docs.pytest.org/en/stable/) reports each
parameterized case and supplies a separate `tmp_path` directory.

### 2. Apply and verify static checks on a bounded target

```bash
ruff format exercises/14_environments_processes_and_packaging
ruff check exercises/14_environments_processes_and_packaging
mypy
```

[Ruff](https://docs.astral.sh/ruff/) formats and lints the selected files.
[mypy](https://mypy.readthedocs.io/en/stable/) reads `pyproject.toml` and
checks the configured capstone and project packages; it does not check every
lesson or exercise.

### 3. Measure coverage on a bounded target

```bash
python scripts/erase_coverage_data.py
PROJECT_IMPLEMENTATION=solution coverage run -m pytest projects/tasks/tests -q
coverage report --include="projects/tasks/solution/**/*.py"
```

[Coverage.py](https://coverage.readthedocs.io/en/stable/) can reveal
unexecuted configured code, but you must still judge whether the tests
contain useful assertions.

### 4. Compare local checks with CI

Open [`.github/workflows/course.yml`](../../.github/workflows/course.yml) and
match each local command to the corresponding
[GitHub Actions](https://docs.github.com/en/actions) step. The goal is to
find problems before pushing, not to discover a different workflow after
opening a pull request.

### 5. Build and inspect the example distribution

The development requirements include
[build](https://build.pypa.io/en/stable/). Exercise the same isolated
packaging boundary that CI verifies, using the lesson's example
distribution:

```bash
python -m pip install -e lessons/14_environments_processes_and_packaging/example_distribution
python -m pydoc packaging_public_api_example
python -m build lessons/14_environments_processes_and_packaging/example_distribution
```

The editable install is for development. Inspect the generated wheel and
sdist under `dist/`, then remove generated `dist/`, `build/`, and
`*.egg-info` directories rather than committing them. The source of truth
remains `pyproject.toml` plus the package under `src/`.
