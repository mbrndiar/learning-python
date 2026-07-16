"""Validate repository-local links and Markdown heading fragments."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_TREEISH = "5e616825a99d4f63fae54b6f768e9ec9b2cec526"
HISTORICAL_LINK_SOURCES = {
    Path("capstones/README.md"),
    Path("capstones/idiomatic/SPEC.md"),
}
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
EXPLICIT_ANCHOR = re.compile(
    r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
IGNORED_SCHEMES = {"http", "https", "mailto"}


def markdown_files() -> list[Path]:
    """Return tracked Markdown files, with a source-tree fallback outside Git."""

    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "*.md"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        result = None
    if result is not None and result.returncode == 0:
        return [
            ROOT / line
            for line in result.stdout.splitlines()
            if line and (ROOT / line).is_file()
        ]
    ignored = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv"}
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in ignored or part == "__pycache__" for part in path.parts)
    )


def heading_slug(text: str) -> str:
    """Approximate GitHub's stable heading IDs for local fragment checks."""

    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "").lower()
    text = re.sub(r"[^\w\-\s]", "", text)
    return re.sub(r"\s+", "-", text.strip())


def anchors(path: Path) -> set[str]:
    """Collect explicit and generated anchors from one Markdown file."""

    text = path.read_text(encoding="utf-8")
    found = set(EXPLICIT_ANCHOR.findall(text))
    duplicates: defaultdict[str, int] = defaultdict(int)
    for heading in HEADING.findall(text):
        base = heading_slug(heading)
        if not base:
            continue
        suffix = duplicates[base]
        found.add(base if suffix == 0 else f"{base}-{suffix}")
        duplicates[base] += 1
    return found


def destinations(text: str) -> list[str]:
    """Extract inline and reference-style Markdown destinations."""

    return INLINE_LINK.findall(text) + REFERENCE_LINK.findall(text)


def historical_target_exists(source: Path, target: Path) -> bool:
    """Return whether a protected capstone link names a pre-removal Git path."""

    source_relative = source.relative_to(ROOT)
    if source_relative not in HISTORICAL_LINK_SOURCES:
        return False
    target_relative = target.relative_to(ROOT)
    result = subprocess.run(
        [
            "git",
            "cat-file",
            "-e",
            f"{HISTORICAL_TREEISH}:{target_relative.as_posix()}",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def main() -> int:
    """Check local targets and Markdown fragments."""

    failures: list[str] = []
    checked = 0
    anchor_cache: dict[Path, set[str]] = {}
    files = markdown_files()
    for source in files:
        text = source.read_text(encoding="utf-8")
        for raw_destination in destinations(text):
            destination = raw_destination.strip("<>")
            split = urlsplit(destination)
            if split.scheme in IGNORED_SCHEMES:
                continue
            if split.scheme or split.netloc:
                failures.append(
                    f"{source.relative_to(ROOT)}: unsupported link {destination}"
                )
                continue

            checked += 1
            target = source if not split.path else source.parent / unquote(split.path)
            target = target.resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                failures.append(
                    f"{source.relative_to(ROOT)}: target leaves repository: {destination}"
                )
                continue
            if not target.exists():
                if not split.fragment and historical_target_exists(source, target):
                    continue
                failures.append(
                    f"{source.relative_to(ROOT)}: missing target: {destination}"
                )
                continue
            if not split.fragment:
                continue

            markdown_target = target / "README.md" if target.is_dir() else target
            if markdown_target.suffix.lower() != ".md":
                continue
            if markdown_target not in anchor_cache:
                anchor_cache[markdown_target] = anchors(markdown_target)
            fragment = unquote(split.fragment)
            if fragment not in anchor_cache[markdown_target]:
                failures.append(
                    f"{source.relative_to(ROOT)}: missing fragment "
                    f"#{fragment} in {markdown_target.relative_to(ROOT)}"
                )

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Checked {checked} local links across {len(files)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
