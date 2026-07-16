"""Milestone 1: keys, expectations, restricted JSON, and normalization."""

import unittest
from importlib import import_module

from implementation import IMPLEMENTATION
from support import (
    FIXTURE_ROOT,
    generated_key,
    generated_value,
    load_fixture,
)

comparative_kv = import_module("comparative_kv")
KvError = comparative_kv.KvError
parse_delete_expectation = comparative_kv.parse_delete_expectation
parse_json_value = comparative_kv.parse_json_value
parse_set_expectation = comparative_kv.parse_set_expectation
validate_key = comparative_kv.validate_key


class DomainTests(unittest.TestCase):
    def test_local_constants_match_the_frozen_contract(self):
        fixture = load_fixture(FIXTURE_ROOT / "contract.json")
        self.assertEqual(fixture["spec_id"], "comparative-kv")
        self.assertEqual(comparative_kv.MAX_SAFE_INTEGER, fixture["safe_integer_max"])
        self.assertEqual(
            comparative_kv.MAX_VALUE_BYTES, fixture["value_input_max_utf8_bytes"]
        )
        self.assertEqual(
            comparative_kv.MAX_CONTAINER_DEPTH,
            fixture["max_container_depth"],
        )

    def test_key_fixture_boundaries(self):
        self.assertIn(IMPLEMENTATION, ("starter", "solution"))
        fixture = load_fixture(FIXTURE_ROOT / "keys.json")
        for item in fixture["accepted"]:
            with self.subTest(case=item["id"]):
                key = generated_key(item)
                self.assertEqual(validate_key(key), key)
        for item in fixture["rejected"]:
            with self.subTest(case=item["id"]):
                with self.assertRaises(KvError) as caught:
                    validate_key(generated_key(item))
                self.assertEqual(
                    (caught.exception.category, caught.exception.details),
                    (
                        "invalid_argument",
                        {"field": "key", "reason": "format"},
                    ),
                )

    def test_accepted_value_fixtures_normalize_exactly(self):
        fixture = load_fixture(FIXTURE_ROOT / "values-accepted.json")
        for item in fixture["cases"]:
            with self.subTest(case=item["id"]):
                text, generated_normalized = generated_value(item)
                expected = item.get("normalized", generated_normalized)
                self.assertEqual(parse_json_value(text), expected)

    def test_rejected_value_fixtures_select_exact_errors(self):
        fixture = load_fixture(FIXTURE_ROOT / "values-rejected.json")
        for item in fixture["cases"]:
            with self.subTest(case=item["id"]):
                text, _ = generated_value(item)
                with self.assertRaises(KvError) as caught:
                    parse_json_value(text)
                self.assertEqual(caught.exception.exit_code, item["exit"])
                self.assertEqual(caught.exception.category, item["category"])
                self.assertEqual(caught.exception.details, item["details"])

    def test_expectations_are_canonical_and_command_specific(self):
        self.assertEqual(parse_set_expectation("any"), "any")
        self.assertEqual(parse_set_expectation("absent"), "absent")
        self.assertEqual(parse_set_expectation("9007199254740991"), 9007199254740991)
        self.assertEqual(parse_delete_expectation("any"), "any")
        self.assertEqual(parse_delete_expectation("7"), 7)
        for parser, values in (
            (parse_set_expectation, ("", "0", "01", "+1", "9007199254740992")),
            (parse_delete_expectation, ("", "absent", "1.0", "-1")),
        ):
            for value in values:
                with self.subTest(parser=parser.__name__, value=value):
                    with self.assertRaises(KvError):
                        parser(value)

    def test_last_member_wins_before_value_traversal(self):
        self.assertEqual(
            parse_json_value('{"ignored":1.5,"ignored":2,"after":3}'),
            {"ignored": 2, "after": 3},
        )
        with self.assertRaises(KvError) as caught:
            parse_json_value('{"ignored":2,"ignored":1.5,"after":3}')
        self.assertEqual(caught.exception.details, {"reason": "non_integral_number"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
