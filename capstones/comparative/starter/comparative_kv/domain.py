"""Milestone 1 domain boundaries from SPEC sections 3, 4, and 7.

Keep these helpers storage-free.  Rejected input is an exit-2 ``KvError`` and
must not create a database.  Revisions used by expectations are positive safe
integers; zero is reserved for an empty store's global revision.
"""

from .errors import incomplete
from .models import DeleteExpectation, JsonValue, SetExpectation

MAX_SAFE_INTEGER = 9_007_199_254_740_991
MAX_VALUE_BYTES = 65_536
MAX_CONTAINER_DEPTH = 32


def validate_key(value: str) -> str:
    """Return an unchanged valid key or reject it.

    The whole value must match ``[A-Za-z0-9][A-Za-z0-9._/-]{0,127}``.
    Keys are opaque and case-sensitive: do not trim, normalize, or interpret
    slash-separated components.  ``fixtures/keys.json`` fixes the boundaries.
    """

    incomplete("comparative key validation")


def parse_set_expectation(value: str) -> SetExpectation:
    """Parse ``any``, ``absent``, or a canonical positive safe revision.

    Revision text is plain decimal with no sign, leading zero, fraction, or
    exponent.  Return symbolic expectations unchanged and exact revisions as
    integers; all other spellings share the specified ``expect`` error.
    """

    incomplete("comparative set expectation parsing")


def parse_delete_expectation(value: str) -> DeleteExpectation:
    """Parse ``any`` or a canonical positive safe revision.

    Delete deliberately excludes ``absent``.  Its remaining revision grammar
    and error shape are identical to the set expectation boundary.
    """

    incomplete("comparative delete expectation parsing")


def parse_json_value(text: str) -> JsonValue:
    """Parse one JSON text into the restricted, normalized semantic value.

    Enforce the UTF-8 byte limit before syntax parsing, then deterministic
    tree validation: container depth, Unicode scalar strings/names, and finite
    exactly-integral safe numbers.  Duplicate object names are last-wins before
    value traversal.  The accepted/rejected value fixtures pin error precedence
    without prescribing a parser or normalization algorithm.
    """

    incomplete("comparative restricted JSON parsing")


def normalized_json(value: JsonValue) -> str:
    """Encode an already-normalized value as compact valid JSON.

    Preserve semantic strings and array order and emit safe integers as JSON
    integers.  Object member order and escape spelling are intentionally not
    observable; insignificant whitespace is forbidden in persisted text.
    """

    incomplete("comparative normalized JSON encoding")
