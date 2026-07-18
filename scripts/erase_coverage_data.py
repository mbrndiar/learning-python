"""Erase primary and parallel Coverage.py data files."""

from pathlib import Path

from coverage import Coverage

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DATA_FILE = ROOT / ".coverage-data" / "coverage"


def main() -> int:
    """Remove repository coverage data, including subprocess data files."""

    data = Coverage().get_data()
    configured_data_file = Path(data.data_filename()).resolve()
    if configured_data_file != EXPECTED_DATA_FILE:
        raise RuntimeError(
            "coverage data must use the repository's .coverage-data/coverage path"
        )
    data.erase(parallel=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
