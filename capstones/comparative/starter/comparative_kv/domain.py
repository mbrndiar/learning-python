"""Guided milestone boundaries for keys, expectations, and restricted JSON."""

from .errors import incomplete
from .models import DeleteExpectation, JsonValue, SetExpectation

MAX_SAFE_INTEGER = 9_007_199_254_740_991
MAX_VALUE_BYTES = 65_536
MAX_CONTAINER_DEPTH = 32


def validate_key(value: str) -> str:
    """TODO(m1): enforce the frozen ASCII key grammar."""

    incomplete("comparative key validation")


def parse_set_expectation(value: str) -> SetExpectation:
    """TODO(m1): accept any, absent, or one canonical safe revision."""

    incomplete("comparative set expectation parsing")


def parse_delete_expectation(value: str) -> DeleteExpectation:
    """TODO(m1): accept any or one canonical safe revision."""

    incomplete("comparative delete expectation parsing")


def parse_json_value(text: str) -> JsonValue:
    """TODO(m1): parse and normalize the restricted JSON value model."""

    incomplete("comparative restricted JSON parsing")


def normalized_json(value: JsonValue) -> str:
    """TODO(m1): encode a normalized value as compact JSON."""

    incomplete("comparative normalized JSON encoding")
