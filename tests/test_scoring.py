import json
import tempfile
import unittest
from pathlib import Path

from evaluation.scoring import CANONICAL_FIELDS, aggregate_scores, load_jsonl, score_case


def record(**overrides):
    base = {
        "station_id": "SITE-1",
        "address": "1 Example Ave",
        "charger_level": "L2",
        "port_count": 2,
        "power_kw": 7.2,
        "connector_type": "J1772",
        "operational_status": "operational",
        "source_record_id": "ROW-1",
    }
    base.update(overrides)
    return base


def answer(case_id="EVG-001", **overrides):
    base = {
        "case_id": case_id,
        "expected_record": record(),
        "expected_decision": "ACCEPT",
        "expected_issue_codes": [],
    }
    base.update(overrides)
    return base


def prediction(case_id="EVG-001", **overrides):
    base = {
        "case_id": case_id,
        "record": record(),
        "decision": "ACCEPT",
        "issue_codes": [],
        "source_mappings": {field: field for field in CANONICAL_FIELDS},
        "latency_ms": 10.0,
        "input_tokens": 100,
        "output_tokens": 20,
        "estimated_cost_usd": 0.001,
    }
    base.update(overrides)
    return base


class ScoreCaseTests(unittest.TestCase):
    def test_perfect_case_scores_all_eligible_dimensions(self):
        expected_mapping = {field: field for field in CANONICAL_FIELDS}
        result = score_case(answer(), prediction(), expected_mapping)

        self.assertEqual(result["field_value_correct"], 8)
        self.assertEqual(result["decision_correct_count"], 1)
        self.assertEqual(result["issue_exact_set_count"], 1)
        self.assertEqual(result["mapping_correct"], 8)
        self.assertEqual(result["mapping_total"], 8)

    def test_abstention_invention_and_unsafe_acceptance_are_separate(self):
        expected = answer(
            expected_record=record(station_id=None, address=None),
            expected_decision="REJECT",
            expected_issue_codes=["MISSING_STABLE_IDENTITY", "MISSING_REQUIRED_FIELD"],
        )
        actual = prediction(
            record=record(station_id="INVENTED", address=None),
            decision="ACCEPT",
            issue_codes=["MISSING_STABLE_IDENTITY", "EXTRA_WARNING"],
        )
        result = score_case(expected, actual)

        self.assertEqual(result["field_value_correct"], 7)
        self.assertEqual(result["expected_abstention_count"], 2)
        self.assertEqual(result["correct_abstention_count"], 1)
        self.assertEqual(result["unsupported_value_count"], 1)
        self.assertEqual(result["unsafe_acceptance_count"], 1)
        self.assertEqual(result["unsafe_under_routing_count"], 1)
        self.assertEqual(result["issue_true_positive"], 1)
        self.assertEqual(result["issue_false_positive"], 1)
        self.assertEqual(result["issue_false_negative"], 1)

    def test_missing_mapping_object_scores_zero_not_false_null_credit(self):
        expected_mapping = {field: field for field in CANONICAL_FIELDS}
        expected_mapping["port_count"] = None
        result = score_case(
            answer(),
            prediction(source_mappings=None),
            expected_mapping,
        )
        self.assertEqual(result["mapping_correct"], 0)
        self.assertEqual(result["mapping_total"], 8)

    def test_explicit_null_mapping_can_receive_abstention_credit(self):
        expected_mapping = {field: field for field in CANONICAL_FIELDS}
        expected_mapping["port_count"] = None
        predicted_mapping = dict(expected_mapping)
        result = score_case(
            answer(),
            prediction(source_mappings=predicted_mapping),
            expected_mapping,
        )
        self.assertEqual(result["mapping_correct"], 8)

    def test_whitespace_is_harmless_but_case_and_punctuation_are_not(self):
        actual = prediction(record=record(address="  1   Example Ave "))
        self.assertEqual(score_case(answer(), actual)["field_value_correct"], 8)

        changed = prediction(record=record(address="1 Example Avenue"))
        self.assertEqual(score_case(answer(), changed)["field_value_correct"], 7)

    def test_contract_errors_are_reported(self):
        invalid = prediction()
        invalid["record"] = {"station_id": "SITE-1"}
        with self.assertRaisesRegex(ValueError, "canonical fields differ"):
            score_case(answer(), invalid)

        invalid = prediction(input_tokens=-1)
        with self.assertRaisesRegex(ValueError, "nonnegative integer"):
            score_case(answer(), invalid)


class AggregateScoreTests(unittest.TestCase):
    def setUp(self):
        self.answers = [
            answer("EVG-001"),
            answer(
                "EVG-002",
                expected_record=record(station_id=None),
                expected_decision="HUMAN_REVIEW",
                expected_issue_codes=["MISSING_REQUIRED_FIELD"],
            ),
        ]
        self.predictions = [
            prediction("EVG-001", latency_ms=30, input_tokens=10, output_tokens=5, estimated_cost_usd=0.1),
            prediction(
                "EVG-002",
                record=record(station_id="MADE-UP"),
                decision="ACCEPT",
                issue_codes=[],
                source_mappings=None,
                latency_ms=10,
                input_tokens=20,
                output_tokens=7,
                estimated_cost_usd=0.2,
            ),
        ]
        self.cases = [
            {"case_id": "EVG-001", "input_format": "csv", "tags": ["normal"]},
            {"case_id": "EVG-002", "input_format": "text", "tags": ["missing", "hard"]},
        ]
        self.mapping_answers = [
            {
                "case_id": "EVG-001",
                "expected_mappings": {field: field for field in CANONICAL_FIELDS},
            }
        ]

    def test_aggregate_metrics_efficiency_and_slices(self):
        result = aggregate_scores(
            self.answers,
            self.predictions,
            cases=self.cases,
            mapping_answers=self.mapping_answers,
        )
        overall = result["overall"]

        self.assertEqual(overall["case_count"], 2)
        self.assertEqual(overall["field_value_accuracy"], 15 / 16)
        self.assertEqual(overall["correct_abstention_rate"], 0.0)
        self.assertEqual(overall["unsupported_value_rate"], 1 / 16)
        self.assertEqual(overall["decision_accuracy"], 0.5)
        self.assertEqual(overall["unsafe_acceptance_rate"], 1.0)
        self.assertEqual(overall["unsafe_under_routing_rate"], 0.5)
        self.assertEqual(overall["issue_micro_precision"], None)
        self.assertEqual(overall["issue_micro_recall"], 0.0)
        self.assertEqual(overall["issue_micro_f1"], 0.0)
        self.assertEqual(overall["issue_exact_set_rate"], 0.5)
        self.assertEqual(overall["mapping_accuracy"], 1.0)
        self.assertEqual(overall["latency_ms_total"], 40.0)
        self.assertEqual(overall["latency_ms_median"], 20.0)
        self.assertEqual(overall["input_tokens_total"], 30)
        self.assertEqual(overall["output_tokens_total"], 12)
        self.assertAlmostEqual(overall["estimated_cost_usd_total"], 0.3)

        self.assertEqual(result["by_format"]["csv"]["case_count"], 1)
        self.assertEqual(result["by_format"]["text"]["case_count"], 1)
        self.assertEqual(result["by_tag"]["missing"]["unsafe_acceptance_rate"], 1.0)
        self.assertEqual(result["by_tag"]["normal"]["mapping_accuracy"], 1.0)
        self.assertIsNone(result["by_tag"]["hard"]["mapping_accuracy"])

    def test_zero_denominators_are_none_not_misleading_zeroes(self):
        result = aggregate_scores([answer()], [prediction()])["overall"]
        self.assertIsNone(result["correct_abstention_rate"])
        self.assertIsNone(result["unsafe_acceptance_rate"])
        self.assertIsNone(result["issue_micro_precision"])
        self.assertIsNone(result["issue_micro_recall"])
        self.assertIsNone(result["issue_micro_f1"])
        self.assertIsNone(result["mapping_accuracy"])

    def test_unavailable_efficiency_values_remain_explicit(self):
        actual = prediction(
            latency_ms=None,
            input_tokens=None,
            output_tokens=None,
            estimated_cost_usd=None,
        )
        result = aggregate_scores([answer()], [actual])["overall"]

        self.assertIsNone(result["latency_ms_total"])
        self.assertIsNone(result["input_tokens_total"])
        self.assertIsNone(result["output_tokens_total"])
        self.assertIsNone(result["estimated_cost_usd_total"])
        self.assertEqual(result["estimated_cost_observed_count"], 0)

    def test_alignment_duplicate_and_unknown_mapping_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "case_ids differ"):
            aggregate_scores(self.answers, self.predictions[:1])
        with self.assertRaisesRegex(ValueError, "duplicate case_id"):
            aggregate_scores([self.answers[0]], [self.predictions[0], self.predictions[0]])
        with self.assertRaisesRegex(ValueError, "unknown case_ids"):
            aggregate_scores(
                [self.answers[0]],
                [self.predictions[0]],
                mapping_answers=[
                    {
                        "case_id": "EVG-999",
                        "expected_mappings": {field: field for field in CANONICAL_FIELDS},
                    }
                ],
            )


class JsonlLoaderTests(unittest.TestCase):
    def test_load_jsonl_accepts_blank_lines_and_reports_bad_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.jsonl"
            path.write_text(json.dumps({"case_id": "EVG-001"}) + "\n\n", encoding="utf-8")
            self.assertEqual(load_jsonl(path), [{"case_id": "EVG-001"}])

            path.write_text("{}\nnot-json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r":2: invalid JSON"):
                load_jsonl(path)


if __name__ == "__main__":
    unittest.main()
