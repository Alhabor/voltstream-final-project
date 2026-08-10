import unittest

from voltstream.baseline import DeterministicBaseline
from voltstream.models import InputEnvelope, InputFormat, IssueSeverity


class BaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = DeterministicBaseline()

    def test_csv_and_aliases_are_parsed(self) -> None:
        rows, issues = self.baseline.parse_envelope(
            InputEnvelope("Site Ref,Connector Qty,Rated Output\nCE-104,4,7200 W", InputFormat.CSV)
        )
        self.assertEqual(issues, [])
        parsed = self.baseline.canonicalize(rows[0])
        self.assertEqual(parsed.record.station_id, "CE-104")
        self.assertEqual(parsed.record.port_count, 4)
        self.assertEqual(parsed.record.power_kw, 7.2)
        self.assertEqual(parsed.source_mappings["station_id"], "Site Ref")
        self.assertEqual(parsed.source_mappings["power_kw"], "Rated Output")

    def test_json_list_yields_multiple_rows(self) -> None:
        rows, issues = self.baseline.parse_envelope(
            InputEnvelope('[{"station_id":"A"},{"station_id":"B"}]', InputFormat.JSON)
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(issues, [])

    def test_key_value_text_is_supported_and_prose_is_preserved(self) -> None:
        rows, issues = self.baseline.parse_envelope(
            InputEnvelope("Station ID: CE-1\nPorts: 2", InputFormat.TEXT)
        )
        self.assertEqual(rows[0]["Station ID"], "CE-1")
        self.assertEqual(issues, [])

        rows, issues = self.baseline.parse_envelope(
            InputEnvelope("Site CE-1 contains two chargers.", InputFormat.TEXT)
        )
        self.assertEqual(issues, [])
        parsed = self.baseline.canonicalize(rows[0])
        self.assertEqual(parsed.unmapped_fields, ["unparsed line 1"])

    def test_invalid_numeric_value_is_not_silently_coerced(self) -> None:
        parsed = self.baseline.canonicalize({"station_id": "A", "ports": "four"})
        self.assertIsNone(parsed.record.port_count)
        self.assertEqual(parsed.issues[0].severity, IssueSeverity.REJECT)

    def test_unknown_field_is_retained_for_review(self) -> None:
        parsed = self.baseline.canonicalize({"station_id": "A", "installer comment": "ok"})
        self.assertEqual(parsed.unmapped_fields, ["installer comment"])
        self.assertIn("UNMAPPED_FIELDS", {issue.code for issue in parsed.issues})

    def test_duplicate_aliases_fill_blanks_but_flag_conflicts(self) -> None:
        filled = self.baseline.canonicalize({"station_id": "", "site ref": "CE-1"})
        self.assertEqual(filled.record.station_id, "CE-1")
        self.assertNotIn("DUPLICATE_CANONICAL_FIELD", {issue.code for issue in filled.issues})

        conflicted = self.baseline.canonicalize({"station_id": "CE-1", "site ref": "CE-2"})
        self.assertEqual(conflicted.record.station_id, "CE-1")
        self.assertIn("DUPLICATE_CANONICAL_FIELD", {issue.code for issue in conflicted.issues})
        self.assertIsNone(conflicted.source_mappings["station_id"])


if __name__ == "__main__":
    unittest.main()
