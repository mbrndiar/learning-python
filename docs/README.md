# 📚 Documentation

Supplementary documentation for the course, separate from the lessons
themselves.

- [`SETUP.md`](SETUP.md) - installing Python, cloning the repository,
  creating and activating a virtual environment, and installing the
  development tools used for testing and quality checks
  (`python -m pip install -r requirements-dev.txt`). Start here if you're new
  to Python or setting up a workspace for the first time.
- [`CAPSTONE_MIGRATION.md`](CAPSTONE_MIGRATION.md) - mapping the removed Task
  project concepts and commands to the two completed, equally required
  capstones, with instructions for inspecting the old source in Git history.
- [`../projects/tasks/`](../projects/tasks/README.md) - the current required
  applied project between Module 11 REST APIs/clients and Module 12 concurrency;
  it is separate from the historical Task source described by the migration
  guide.

Core teaching material lives in each module's `README.md` and runnable lesson
files. Start from the repository's [main course guide](../README.md), not this
directory.

Check repository-local Markdown links with:

```bash
python scripts/check_markdown_links.py
```
