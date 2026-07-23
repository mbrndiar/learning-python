# 📦 Packaging public API example

This deliberately small distribution accompanies
[`05_distributions_builds_and_public_apis.py`](../05_distributions_builds_and_public_apis.py).
It uses a `src/` layout and exposes one documented public function:

```python
from packaging_public_api_example import greet

print(greet("Ada", excited=True))
```

From the repository root:

```bash
python -m pip install -e lessons/14_environments_processes_and_packaging/example_distribution
python -m build lessons/14_environments_processes_and_packaging/example_distribution
python -m pydoc packaging_public_api_example
```

The editable install is a development workflow. The wheel and source
distribution produced under `dist/` are generated artifacts and are ignored by
Git.
