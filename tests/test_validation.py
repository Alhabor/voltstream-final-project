import unittest

from voltstream.models import CanonicalRecord, Issue, IssueSeverity, RouteDecision
from voltstream.validation import route_for_issues, validate_record


class ValidationTests(unittest.TestCase):
    def test_nonpositive_physical_values_are_rejected(self) -> None:
        issues = validate_record(CanonicalRecord(station_id="A", charger_level="L2", port_count=-1, power_kw=0))
        codes = {issue.code for issue in issues}
        self.assertIn("INVALID_PORT_COUNT", codes)
        self.assertIn("INVALID_POWER_VALUE", codes)

    def test_unknown_vocab_requires_review(self) -> None:
        issues = validate_record(
            CanonicalRecord(
                station_id="A",
                address="1 Test Way",
                charger_level="L2",
                port_count=2,
                power_kw=7.2,
                connector_type="MAGIC",
                source_record_id="ROW-A",
            )
        )
        self.assertEqual(route_for_issues(issues), RouteDecision.HUMAN_REVIEW)

    def test_route_precedence(self) -> None:
        issues = [
            Issue("A", IssueSeverity.WARNING, "warning"),
            Issue("B", IssueSeverity.REVIEW, "review"),
            Issue("C", IssueSeverity.REJECT, "reject"),
        ]
        self.assertEqual(route_for_issues(issues), RouteDecision.REJECT)
        self.assertEqual(route_for_issues(issues[:2]), RouteDecision.HUMAN_REVIEW)
        self.assertEqual(route_for_issues(issues[:1]), RouteDecision.ACCEPT)


if __name__ == "__main__":
    unittest.main()
