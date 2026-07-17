"""Milestone 2 starter: streaming CSV and JSON Lines sources.

Each adapter owns its UTF-8 file and exposes a one-shot iterator. Preserve
physical/source record numbering, translate source failures into the documented
content versus I/O classes, and close on exhaustion, parser failure, or explicit
iterator closure. Consumers own closure after partial use or downstream failure.
"""

from collections.abc import Iterator
from pathlib import Path

from .errors import incomplete
from .models import RawRecord


class CSVSource:
    """Own and stream the exact documented UTF-8 CSV dialect.

    Header validation precedes data records. Rows with the wrong field count or
    blank fields remain records for normalization diagnostics; malformed CSV
    syntax is a source-level failure. Do not materialize the file.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        """Yield one-based logical records under explicit iterator ownership.

        Resource lifetime follows generator lifetime. Exhaustion, source-side
        failure, or explicit close releases the file; a consumer abandoning
        partial iteration must close the iterator it owns.
        """

        # TODO(m2): validate the exact header and keep content errors distinct
        # from unreadable-source errors while preserving streaming cleanup.
        incomplete("milestone 2 CSV source")


class JSONLinesSource:
    """Own and stream non-blank physical UTF-8 JSON Lines records.

    Blank lines do not yield records but still affect the next physical line
    number.  Duplicate object members must survive parsing as shape diagnostics,
    while malformed JSON is a source-content failure.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def records(self) -> Iterator[RawRecord]:
        """Yield physical line numbers and detect duplicate object members.

        Keep parsing lazy and use the same explicit-closure contract as CSV.
        """

        # TODO(m2): choose a parsing seam that preserves duplicate-member evidence
        # long enough to produce the required invalid-shape diagnostic.
        incomplete("milestone 2 JSON Lines source")
