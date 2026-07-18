"""
Lesson 5.6: Directories and Paths

``pathlib.Path`` represents filesystem paths without changing the process's
working directory. This lesson keeps every filesystem change inside a
``TemporaryDirectory`` and prints only stable, relative names.
"""

import os
import shutil
import tempfile
from pathlib import Path


def relative_posix(path: Path, root: Path) -> str:
    """Return a path below *root* using a stable forward-slash representation."""
    return path.relative_to(root).as_posix()


if __name__ == "__main__":
    relative_path = Path("project") / "data" / "report.txt"

    # A relative path used for I/O is interpreted from Path.cwd(), which depends
    # on where the caller started Python. A path based on __file__ is anchored
    # to this script's location instead. Neither expression changes the cwd.
    cwd_based_path = Path.cwd() / relative_path
    file_based_path = Path(__file__).resolve().parent / relative_path
    print("Relative path:", relative_path.as_posix())
    print("cwd-based path is absolute:", cwd_based_path.is_absolute())
    print("__file__-based path is absolute:", file_based_path.is_absolute())

    with tempfile.TemporaryDirectory(prefix="paths_lesson_") as directory:
        root = Path(directory)
        project = root / "project"
        data = project / "data"
        archive = project / "archive"

        # parents=True creates missing ancestors; exist_ok=True permits reruns.
        data.mkdir(parents=True, exist_ok=True)
        archive.mkdir(parents=True, exist_ok=True)

        draft = data / "draft.txt"
        second = data / "second.txt"
        values = data / "values.csv"
        readme = archive / "readme.txt"
        notes = project / "notes.md"
        draft.write_text("alpha\n", encoding="utf-8")
        second.write_text("beta\n", encoding="utf-8")
        values.write_text("x,y\n1,2\n", encoding="utf-8")
        readme.write_text("archive\n", encoding="utf-8")
        notes.write_text("# Notes\n", encoding="utf-8")

        print("\nPath checks:")
        print("project exists:", project.exists())
        print("data is a directory:", data.is_dir())
        print("draft is a file:", draft.is_file())
        print("draft size in bytes:", draft.stat().st_size)

        # Filesystems do not promise iteration order. Sort whenever output,
        # comparisons, archives, or tests require deterministic ordering.
        children = sorted(path.name for path in project.iterdir())
        direct_text = sorted(path.name for path in data.glob("*.txt"))
        recursive_text = sorted(
            relative_posix(path, project) for path in project.rglob("*.txt")
        )
        print("\nSorted project children:", children)
        print("Sorted data/*.txt:", direct_text)
        print("Sorted recursive *.txt:", recursive_text)

        report = draft.rename(data / "report.txt")
        pending = data / "pending.txt"
        current = data / "current.txt"
        pending.write_text("new\n", encoding="utf-8")
        current.write_text("old\n", encoding="utf-8")

        # replace() explicitly replaces an existing destination. rename()
        # replacement details vary by operating system, so the rename above
        # deliberately used a destination that did not exist.
        pending.replace(current)
        print("\nAfter replace:", current.read_text(encoding="utf-8").strip())

        # copy2() copies file data and attempts to preserve basic stat metadata;
        # it is not a complete clone of ownership, ACLs, or every platform field.
        copied = Path(shutil.copy2(current, archive / "current-copy.txt"))
        moved = Path(shutil.move(report, archive / "report.txt"))
        print("Copied to:", relative_posix(copied, project))
        print("Moved to:", relative_posix(moved, project))
        print("Original report still exists:", report.exists())

        unresolved = Path("project") / "data" / ".." / "archive"
        lexically_normalized = Path(os.path.normpath(unresolved))
        resolved_archive = (root / unresolved).resolve(strict=True)
        print("\nUnresolved path:", unresolved.as_posix())
        print("Lexically normalized:", lexically_normalized.as_posix())
        print("Resolved existing path:", relative_posix(resolved_archive, root))

        # normpath() only normalizes path text. resolve() produces an absolute
        # path, removes "..", and resolves existing symlinks. Neither operation
        # grants authorization or by itself creates a secure containment
        # boundary. Even a resolve()/relative_to() check is only a snapshot and
        # can race with symlink changes. Security-sensitive code also needs a
        # strict input policy, OS permissions, and race-resistant file access.
        resolved_archive.relative_to(root.resolve(strict=True))

        try:
            (data / "missing.txt").stat()
        except FileNotFoundError:
            print("\nExpected error: cannot stat a missing file")

        try:
            project.rmdir()
        except OSError:
            print("Expected error: cannot rmdir a non-empty directory")

        scratch = root / "scratch"
        scratch.mkdir()
        marker = scratch / "marker.txt"
        marker.write_text("temporary\n", encoding="utf-8")
        marker.unlink()
        scratch.rmdir()
        print("Manual unlink/rmdir cleanup:", not scratch.exists())

    # TemporaryDirectory recursively removes everything that remains.
    print("Temporary tree removed:", not root.exists())
