import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from voltstream.experiment_runner import (
    baseline_prediction,
    estimate_deepseek_cost,
    ExperimentRunner,
    render_case_prompt,
)
from voltstream.providers import ProviderResponse


class ExperimentRunnerTests(unittest.TestCase):
    def test_baseline_accepts_a_complete_known_record(self):
        case = {
            "case_id": "EVG-T01",
            "input_format": "csv",
            "source_name": "synthetic_test",
            "payload": (
                "station_id,address,charger_level,port_count,power_kw,source_record_id\n"
                "A-1,1 Test Way,L2,2,7.2,ROW-1"
            ),
        }
        result = baseline_prediction(case)
        self.assertEqual(result["decision"], "ACCEPT")
        self.assertEqual(result["source_mappings"]["station_id"], "station_id")
        self.assertEqual(result["model_calls"], 0)

    def test_case_prompt_requires_every_placeholder(self):
        template = "{{case_id}} {{input_format}} {{source_name}} {{task}} {{payload}}"
        case = {
            "case_id": "A",
            "input_format": "text",
            "source_name": "synthetic",
            "task": "extract",
            "payload": "payload",
        }
        self.assertEqual(render_case_prompt(template, case), "A text synthetic extract payload")

    def test_case_prompt_allows_nested_json_closing_braces(self):
        case = {
            "case_id": "A",
            "input_format": "json",
            "source_name": "synthetic",
            "task": "extract",
            "payload": '{"outer":{"inner":1}}',
        }
        rendered = render_case_prompt("{{case_id}}\n{{payload}}", case)
        self.assertEqual(rendered, 'A\n{"outer":{"inner":1}}')

    def test_deepseek_cost_separates_cached_and_uncached_tokens(self):
        response = ProviderResponse(
            content="{}",
            model="deepseek-v4-flash",
            latency_ms=1,
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            cached_input_tokens=500_000,
        )
        pricing = {
            "models": {
                "deepseek-v4-flash": {
                    "cached_input": 1.0,
                    "uncached_input": 2.0,
                    "output": 3.0,
                }
            }
        }
        self.assertEqual(
            estimate_deepseek_cost(response, pricing, "deepseek-v4-flash"), 4.5
        )

    def test_quality_strategy_preserves_initial_provider_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory)
            runner = object.__new__(ExperimentRunner)
            runner.guarded_prompt = "guarded"
            runner.feedback_template = "unused"
            failure = {
                "case_id": "EVG-T01",
                "record": {},
                "decision": "REJECT",
                "issue_codes": ["PARSER_FAILURE"],
            }
            with patch.object(runner, "_run_deepseek", return_value=failure):
                result = runner._run_quality(
                    {"case_id": "EVG-T01", "input_format": "text", "payload": "x"},
                    case_dir,
                )
            self.assertIs(result, failure)

    def test_resume_reuses_completed_case_without_overwriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            strategy_dir = root / "evaluation" / "runs" / "run" / "baseline"
            completed_dir = strategy_dir / "EVG-001"
            completed_dir.mkdir(parents=True)
            completed = {"case_id": "EVG-001", "decision": "ACCEPT"}
            completed_path = completed_dir / "parsed-output.json"
            completed_path.write_text(json.dumps(completed), encoding="utf-8")

            runner = object.__new__(ExperimentRunner)
            runner.root = root
            runner.run_dir = root / "evaluation" / "runs" / "run"
            runner.cases = [
                {"case_id": "EVG-001"},
                {"case_id": "EVG-002"},
            ]
            generated = {"case_id": "EVG-002", "decision": "REJECT"}
            with patch.object(runner, "initialize_manifest"), patch.object(
                runner, "_run_case", return_value=generated
            ) as run_case, patch.object(runner, "_mark_complete"):
                output_path = runner.run("baseline", resume=True)

            self.assertEqual(completed_path.read_text(), json.dumps(completed))
            self.assertEqual(run_case.call_count, 1)
            self.assertEqual(run_case.call_args.args[1]["case_id"], "EVG-002")
            rows = [json.loads(line) for line in output_path.read_text().splitlines()]
            self.assertEqual(rows, [completed, generated])


if __name__ == "__main__":
    unittest.main()
