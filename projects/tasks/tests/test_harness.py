"""Smoke tests for source selection and matching public boundaries."""

import json
import os
import subprocess
import sys
import textwrap
from importlib import import_module
from pathlib import Path

from implementation import IMPLEMENTATION, SOURCE_ROOT
from support import PROJECT_ROOT, REPOSITORY_ROOT, load_json_fixture

PUBLIC_MODULES = (
    "tasks_core",
    "tasks_core.domain",
    "tasks_core.errors",
    "tasks_core.service",
    "tasks_core.repositories",
    "tasks_core.repositories.protocol",
    "tasks_core.repositories.sqlite",
    "tasks_core.repositories.markdown",
    "tasks_api",
    "tasks_api.bootstrap",
    "tasks_api.stdlib",
    "tasks_api.stdlib.app",
    "tasks_api.stdlib.__main__",
    "tasks_api.flask",
    "tasks_api.flask.app",
    "tasks_api.flask.__main__",
    "tasks_api.fastapi",
    "tasks_api.fastapi.app",
    "tasks_api.fastapi.__main__",
    "tasks_cli",
    "tasks_cli.application",
    "tasks_cli.transport",
    "tasks_cli.urllib",
    "tasks_cli.urllib.adapter",
    "tasks_cli.urllib.__main__",
    "tasks_cli.requests",
    "tasks_cli.requests.adapter",
    "tasks_cli.requests.__main__",
    "tasks_cli.httpx",
    "tasks_cli.httpx.adapter",
    "tasks_cli.httpx.__main__",
)


def _public_manifest(source_root: Path) -> object:
    script = textwrap.dedent(
        f"""
        import importlib
        import inspect
        import json

        modules = {PUBLIC_MODULES!r}
        manifest = {{}}
        for module_name in modules:
            module = importlib.import_module(module_name)
            names = list(module.__all__)
            signatures = {{}}
            for name in names:
                value = getattr(module, name)
                try:
                    signatures[name] = str(inspect.signature(value))
                except (TypeError, ValueError):
                    signatures[name] = None
            manifest[module_name] = {{"names": names, "signatures": signatures}}
        print(json.dumps(manifest, sort_keys=True))
        """
    )
    existing_pythonpath = os.environ.get("PYTHONPATH")
    pythonpath = str(source_root)
    if existing_pythonpath:
        pythonpath = os.pathsep.join((pythonpath, existing_pythonpath))
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPOSITORY_ROOT,
        env={**os.environ, "PYTHONPATH": pythonpath},
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return json.loads(result.stdout)


def test_selected_source_root_owns_every_public_module() -> None:
    assert IMPLEMENTATION in ("starter", "solution")
    for module_name in PUBLIC_MODULES:
        module = import_module(module_name)
        module_file = module.__file__
        assert module_file is not None
        assert Path(module_file).resolve().is_relative_to(SOURCE_ROOT.resolve())


def test_starter_and_solution_public_imports_and_signatures_match() -> None:
    assert _public_manifest(PROJECT_ROOT / "starter") == _public_manifest(
        PROJECT_ROOT / "solution"
    )


def test_deterministic_fixtures_are_readable() -> None:
    assert load_json_fixture("http", "task.json") == {
        "id": 1,
        "title": "Learn REST",
        "completed": False,
    }
    assert (PROJECT_ROOT / "tests" / "fixtures" / "markdown" / "empty-v1.md").read_text(
        encoding="utf-8"
    ) == "<!-- rest-task-api:v1 next-id=1 -->\n# Tasks\n"
