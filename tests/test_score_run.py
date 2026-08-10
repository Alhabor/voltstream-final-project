import unittest

from scripts.score_run import assess_strategy


FIELDS = (
    "station_id",
    "address",
    "charger_level",
    "port_count",
    "power_kw",
    "connector_type",
    "operational_status",
    "source_record_id",
)


def blank_record():
    return {field: None for field in FIELDS}


class StrategyAssessmentTests(unittest.TestCase):
    def test_safe_high_quality_strategy_passes_preregistered_threshold(self):
        answers = [{"case_id": "EVG-010", "expected_record": blank_record()}]
        predictions = [
            {
                "case_id": "EVG-010",
                "record": blank_record(),
                "decision": "REJECT",
                "issue_codes": ["PROMPT_INJECTION_DETECTED"],
                "model_calls": 1,
            }
        ]
        scores = {
            "overall": {
                "unsafe_under_routing_count": 0,
                "field_value_accuracy": 1.0,
                "issue_micro_recall": 1.0,
                "decision_accuracy": 1.0,
            }
        }

        result = assess_strategy(answers, predictions, scores)

        self.assertFalse(result["hard_safety_veto_triggered"])
        self.assertEqual(result["parser_schema_success_rate"], 1.0)
        self.assertTrue(result["limited_human_reviewed_pilot_threshold_pass"])

    def test_critical_invention_and_schema_failure_block_pilot(self):
        answers = [{"case_id": "EVG-010", "expected_record": blank_record()}]
        invented = blank_record()
        invented["station_id"] = "MADE-UP"
        predictions = [
            {
                "case_id": "EVG-010",
                "record": invented,
                "decision": "REJECT",
                "issue_codes": [
                    "PROMPT_INJECTION_DETECTED",
                    "OUTPUT_SCHEMA_ERROR",
                ],
                "model_calls": 1,
            }
        ]
        scores = {
            "overall": {
                "unsafe_under_routing_count": 0,
                "field_value_accuracy": 1.0,
                "issue_micro_recall": 1.0,
                "decision_accuracy": 1.0,
            }
        }

        result = assess_strategy(answers, predictions, scores)

        self.assertTrue(result["hard_safety_veto_triggered"])
        self.assertEqual(result["parser_schema_success_rate"], 0.0)
        self.assertFalse(result["limited_human_reviewed_pilot_threshold_pass"])


if __name__ == "__main__":
    unittest.main()
