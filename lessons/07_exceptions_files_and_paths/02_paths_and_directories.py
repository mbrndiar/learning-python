"""
Chapter 7, Lesson 2: Paths and Directories

Purpose: represent filesystem locations with `pathlib.Path`, distinguish
relative from absolute paths, iterate a directory tree, read metadata, and
use a temporary directory so a lesson script leaves nothing behind.

Prerequisites: Lesson 1 (exception flow) and Chapters 1-6. This lesson
introduces `Path` before Lesson 3 uses it to open files, and before
Lesson 4 uses it inside a context manager.

Read this file top to bottom, predict each output, then run it:

    python lessons/07_exceptions_files_and_paths/02_paths_and_directories.py
"""

import tempfile
from pathlib import Path


def relative_posix(path: Path, root: Path) -> str:
    """Return *path* below *root* using a stable forward-slash string."""
    return path.relative_to(root).as_posix()


# Step 1: Path represents a filesystem location as a value -- building one
# does not touch the filesystem or change the process's current working
# directory. `/` between Path segments joins them, unrelated to division.
relative_path = Path("project") / "data" / "report.txt"
print("Relative path:", relative_path.as_posix())
print("Is it absolute?", relative_path.is_absolute())

# Step 2: a relative path used for I/O is interpreted against Path.cwd(),
# which depends on where the caller started Python. A path anchored to
# __file__ instead depends on this script's own location. Building either
# expression still does not touch the filesystem or change the cwd.
cwd_based_path = Path.cwd() / relative_path
file_based_path = Path(__file__).resolve().parent / relative_path
print("cwd-based path is absolute:", cwd_based_path.is_absolute())
print("__file__-based path is absolute:", file_based_path.is_absolute())

# Step 3: everything below happens inside a TemporaryDirectory, so this
# lesson creates and removes its own files without touching anything else
# on disk. This lesson owns cleanup explicitly with try/finally; Lesson 4
# introduces `with` as the concise form of the same guarantee.
temporary = tempfile.TemporaryDirectory(prefix="paths_lesson_")
try:
    directory = temporary.name
    root = Path(directory)
    project = root / "project"
    data = project / "data"

    # parents=True creates missing ancestors; exist_ok=True permits reruns
    # without raising if the directory already exists.
    data.mkdir(parents=True, exist_ok=True)

    draft = data / "draft.txt"
    values = data / "values.csv"
    notes = project / "notes.md"
    draft.write_text("alpha\n", encoding="utf-8")
    values.write_text("x,y\n1,2\n", encoding="utf-8")
    notes.write_text("# Notes\n", encoding="utf-8")

    # Step 4: metadata. exists()/is_dir()/is_file() classify a path;
    # stat() exposes details like st_size (byte count) and timestamps.
    print("\nPath checks:")
    print("project exists:", project.exists())
    print("data is a directory:", data.is_dir())
    print("draft is a file:", draft.is_file())
    print("draft size in bytes:", draft.stat().st_size)

    # Step 5: iteration. iterdir() lists immediate children only; glob()
    # matches a pattern in one directory; rglob() matches recursively.
    # Filesystems make no ordering promise, so sort whenever output,
    # comparisons, or tests need a deterministic order.
    children = sorted(path.name for path in project.iterdir())
    direct_text = sorted(path.name for path in data.glob("*.txt"))
    recursive_text = sorted(
        relative_posix(path, project) for path in project.rglob("*.txt")
    )
    print("\nSorted project children:", children)
    print("Sorted data/*.txt:", direct_text)
    print("Sorted recursive *.txt:", recursive_text)

    # Step 6: a missing path raises the same kind of error Lesson 1
    # covered -- Path itself does not silently return a placeholder value.
    try:
        (data / "missing.txt").stat()
    except FileNotFoundError:
        print("\nExpected error: cannot stat a missing file")
finally:
    temporary.cleanup()

# Step 7: cleanup() removed the directory and everything inside it. The
# finally clause guaranteed that cleanup ran even if an earlier step failed.
print("\nTemporary tree removed:", not root.exists())

# --- One-variable experiment -------------------------------------------
# Change `data.glob("*.txt")` to `data.glob("*.csv")` and predict the new
# sorted list. glob() matches only the given directory; rglob() would also
# find a same-named file nested one level deeper.
