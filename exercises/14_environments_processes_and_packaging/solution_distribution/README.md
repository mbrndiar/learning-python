# 📦 Solution distribution: console script entry point

The completed counterpart to `starter_distribution/`. Its `pyproject.toml`
declares the console entry point the task asks you to add:

```toml
[project.scripts]
timekeeper = "timekeeper_cli:main"
```

`solutions.py` verifies this distribution the same way `exercises.py` verifies
the starter: it parses `pyproject.toml` with `tomllib`, resolves the
`timekeeper` entry to `timekeeper_cli:main`, and confirms the callable exists.
