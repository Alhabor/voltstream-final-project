"""Reproducible experiment orchestration for the fixed VoltStream benchmark.

The runner separates generation from scoring, writes raw provider responses
before loading answer keys, and persists only synthetic payloads plus sanitized
metadata. It supports one strategy at a time so an interrupted network run can
resume without overwriting completed evidence.
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .baseline import DeterministicBaseline
from .model_pipeline import CANONICAL_FIELDS, ModelPostprocessResult, postprocess_model_response
from .models import CanonicalRecord, InputEnvelope, InputFormat, Issue, IssueSeverity
from .providers import CodexProvider, DeepSeekProvider, ProviderError, ProviderResponse
from .validation import detect_payload_issues, route_for_issues, validate_record


STRATEGIES = (
    "baseline",
    "deepseek-flash-guarded",
    "codex-terra-guarded",
    "rules-first-cascade",
    "deepseek-pro-quality",
    "deepseek-flash-unrestricted",
)

_ISSUE_TRANSLATIONS = {
    "MALFORMED_SUBMISSION": "PARSER_FAILURE",
    "UNMAPPED_FIELDS": "OUTPUT_SCHEMA_ERROR",
    "DUPLICATE_CANONICAL_FIELD": "AMBIGUOUS_FIELD_VALUE",
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL objects in file order."""

    rows: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def render_case_prompt(template: str, case: Mapping[str, Any]) -> str:
    """Render the deliberately small, non-executable prompt template."""

    rendered = template
    for key in ("case_id", "input_format", "source_name", "task", "payload"):
        rendered = rendered.replace("{{" + key + "}}", str(case[key]))
    # JSON payloads legitimately contain adjacent closing braces. Only an
    # unresolved variable from this template's fixed vocabulary is an error.
    if re.search(
        r"\{\{(?:case_id|input_format|source_name|task|payload)\}\}", rendered
    ):
        raise ValueError("case prompt contains an unresolved template variable")
    return rendered


def baseline_prediction(case: Mapping[str, Any]) -> Dict[str, Any]:
    """Run the deterministic baseline and return the common prediction shape."""

    baseline = DeterministicBaseline()
    envelope = InputEnvelope(
        content=str(case["payload"]),
        input_format=InputFormat(str(case["input_format"])),
        source_name=str(case["source_name"]),
    )
    raw_rows, submission_issues = baseline.parse_envelope(envelope)
    if not raw_rows:
        issues = submission_issues
        record = CanonicalRecord()
        mappings = {field: None for field in CANONICAL_FIELDS}
    else:
        parsed = baseline.canonicalize(raw_rows[0])
        record = parsed.record
        mappings = parsed.source_mappings
        issues = [
            *parsed.issues,
            *validate_record(record),
            *detect_payload_issues(envelope.content),
        ]

    benchmark_codes = _translate_internal_issues(issues)
    benchmark_issues = [
        Issue(code=code, severity=_severity_for_code(code), message="Baseline finding.")
        for code in benchmark_codes
    ]
    return {
        "case_id": case["case_id"],
        "record": record.to_dict(),
        "source_mappings": mappings,
        "decision": route_for_issues(benchmark_issues).value,
        "issue_codes": benchmark_codes,
        "latency_ms": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "model_calls": 0,
    }


def prediction_from_model(
    case: Mapping[str, Any],
    response: ProviderResponse,
    *,
    estimated_cost_usd: Optional[float],
    model_calls: int = 1,
) -> Tuple[Dict[str, Any], ModelPostprocessResult]:
    """Apply local safety controls and create the common scored row."""

    processed = postprocess_model_response(response.content, str(case["payload"]))
    if processed.candidate is None:
        record = CanonicalRecord().to_dict()
        mappings = {field: None for field in CANONICAL_FIELDS}
    else:
        record = processed.candidate.record.to_dict()
        mappings = processed.candidate.source_mappings
    prediction = {
        "case_id": case["case_id"],
        "record": record,
        "source_mappings": mappings,
        "decision": processed.decision.value,
        "issue_codes": processed.issue_codes,
        "latency_ms": round(response.latency_ms, 3),
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "cached_input_tokens": response.cached_input_tokens,
        "estimated_cost_usd": estimated_cost_usd,
        "model_calls": model_calls,
        "provider_model": response.model,
    }
    return prediction, processed


def estimate_deepseek_cost(
    response: ProviderResponse, pricing: Mapping[str, Any], requested_model: str
) -> Optional[float]:
    """Estimate current list-price cost from provider-reported token counts."""

    if response.input_tokens is None or response.output_tokens is None:
        return None
    rates = pricing.get("models", {}).get(requested_model)
    if not isinstance(rates, Mapping):
        return None
    cached = min(response.cached_input_tokens or 0, response.input_tokens)
    uncached = response.input_tokens - cached
    cost = (
        cached * float(rates["cached_input"])
        + uncached * float(rates["uncached_input"])
        + response.output_tokens * float(rates["output"])
    ) / 1_000_000
    return round(cost, 10)


class ExperimentRunner:
    """Run and persist registered strategies against immutable cases."""

    def __init__(self, root: Path, run_id: str) -> None:
        self.root = root.resolve()
        self.run_dir = self.root / "evaluation" / "runs" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.cases = load_jsonl(self.root / "data" / "cases.jsonl")
        self.pricing = json.loads(
            (self.root / "evaluation" / "pricing_2026-08-09.json").read_text(encoding="utf-8")
        )
        self.guarded_prompt = (self.root / "prompts" / "guarded_system_v1.md").read_text()
        self.unrestricted_prompt = (
            self.root / "prompts" / "unrestricted_cleaner_system_v1.md"
        ).read_text()
        self.case_template = (self.root / "prompts" / "case_user_template_v1.md").read_text()
        self.feedback_template = (self.root / "prompts" / "validator_feedback_v1.md").read_text()

    def initialize_manifest(self) -> None:
        manifest_path = self.run_dir / "manifest.json"
        if manifest_path.exists():
            return
        manifest = {
            "run_id": self.run_dir.name,
            "created_at_utc": _utc_now(),
            "git_commit": _git_output(self.root, ["rev-parse", "HEAD"]),
            "git_status": _git_output(self.root, ["status", "--short"]),
            "python": sys.version,
            "platform": platform.platform(),
            "frozen_sha256": {
                str(path.relative_to(self.root)): _sha256(path)
                for path in self._frozen_paths()
            },
            "pricing_snapshot": "evaluation/pricing_2026-08-09.json",
            "strategies_completed": [],
        }
        _write_json(manifest_path, manifest)

    def run(self, strategy: str) -> Path:
        if strategy not in STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        self.initialize_manifest()
        strategy_dir = self.run_dir / strategy
        predictions_path = strategy_dir / "predictions.jsonl"
        if predictions_path.exists():
            raise FileExistsError(f"Strategy evidence already exists: {predictions_path}")
        strategy_dir.mkdir(parents=True, exist_ok=False)

        if strategy == "rules-first-cascade":
            predictions = self._run_cascade(strategy_dir)
        else:
            predictions = [self._run_case(strategy, case, strategy_dir) for case in self.cases]

        _write_jsonl(predictions_path, predictions)
        self._mark_complete(strategy)
        return predictions_path

    def _run_case(
        self, strategy: str, case: Mapping[str, Any], strategy_dir: Path
    ) -> Dict[str, Any]:
        case_dir = strategy_dir / str(case["case_id"])
        case_dir.mkdir(parents=True, exist_ok=False)
        if strategy == "baseline":
            prediction = baseline_prediction(case)
            _write_json(case_dir / "parsed-output.json", prediction)
            return prediction

        if strategy == "codex-terra-guarded":
            return self._run_codex(case, case_dir)
        if strategy == "deepseek-flash-guarded":
            return self._run_deepseek(case, case_dir, "deepseek-v4-flash", self.guarded_prompt)
        if strategy == "deepseek-flash-unrestricted":
            return self._run_deepseek(
                case, case_dir, "deepseek-v4-flash", self.unrestricted_prompt
            )
        if strategy == "deepseek-pro-quality":
            return self._run_quality(case, case_dir)
        raise ValueError(f"Unsupported direct strategy: {strategy}")

    def _run_deepseek(
        self,
        case: Mapping[str, Any],
        case_dir: Path,
        model: str,
        system_prompt: str,
    ) -> Dict[str, Any]:
        user_prompt = render_case_prompt(self.case_template, case)
        request_metadata = {
            "provider": "DeepSeek",
            "model": model,
            "parameters": {
                "temperature": 0.0,
                "max_tokens": 4096,
                "thinking": "disabled",
                "response_format": "json_object",
            },
            "system_prompt_sha256": _sha256_text(system_prompt),
            "user_prompt": user_prompt,
        }
        _write_json(case_dir / "request.json", request_metadata)
        try:
            response = DeepSeekProvider().generate(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,
                max_tokens=4096,
                thinking_enabled=False,
            )
        except ProviderError as exc:
            return self._provider_failure(case, case_dir, str(exc))

        (case_dir / "raw-response.txt").write_text(response.content, encoding="utf-8")
        cost = estimate_deepseek_cost(response, self.pricing, model)
        prediction, processed = prediction_from_model(
            case, response, estimated_cost_usd=cost
        )
        _write_json(case_dir / "validation.json", processed.to_dict())
        _write_json(case_dir / "metrics.json", _response_metadata(response, cost))
        _write_json(case_dir / "parsed-output.json", prediction)
        return prediction

    def _run_codex(self, case: Mapping[str, Any], case_dir: Path) -> Dict[str, Any]:
        user_prompt = render_case_prompt(self.case_template, case)
        _write_json(
            case_dir / "request.json",
            {
                "provider": "OpenAI Codex CLI",
                "model": "gpt-5.6-terra",
                "parameters": {"reasoning_effort": "low", "sandbox": "read-only"},
                "system_prompt_sha256": _sha256_text(self.guarded_prompt),
                "user_prompt": user_prompt,
            },
        )
        try:
            response = CodexProvider().generate(
                model="gpt-5.6-terra",
                system_prompt=self.guarded_prompt,
                user_prompt=user_prompt,
                output_schema=self.root / "evaluation" / "model_response.schema.json",
                reasoning_effort="low",
            )
        except ProviderError as exc:
            return self._provider_failure(case, case_dir, str(exc))
        (case_dir / "raw-response.txt").write_text(response.content, encoding="utf-8")
        prediction, processed = prediction_from_model(
            case, response, estimated_cost_usd=None
        )
        _write_json(case_dir / "validation.json", processed.to_dict())
        _write_json(case_dir / "metrics.json", _response_metadata(response, None))
        _write_json(case_dir / "parsed-output.json", prediction)
        return prediction

    def _run_quality(self, case: Mapping[str, Any], case_dir: Path) -> Dict[str, Any]:
        initial = self._run_deepseek(
            case, case_dir, "deepseek-v4-pro", self.guarded_prompt
        )
        validation_path = case_dir / "validation.json"
        if not validation_path.exists():
            # The first call's provider failure has already been persisted as a
            # scored fail-closed result. There is no candidate to correct.
            return initial
        validation = json.loads(validation_path.read_text())
        candidate = validation.get("candidate")
        candidate_codes = set(candidate.get("issue_codes", [])) if isinstance(candidate, dict) else set()
        final_codes = set(validation.get("issue_codes", []))
        needs_feedback = candidate is None or bool(final_codes - candidate_codes)
        if not needs_feedback:
            return initial

        feedback_prompt = self.feedback_template
        replacements = {
            "case_id": case["case_id"],
            "input_format": case["input_format"],
            "payload": case["payload"],
            "previous_candidate": (case_dir / "raw-response.txt").read_text(),
            "validator_findings": json.dumps(validation, ensure_ascii=False),
        }
        for key, value in replacements.items():
            feedback_prompt = feedback_prompt.replace("{{" + key + "}}", str(value))
        _write_json(
            case_dir / "correction-request.json",
            {
                "provider": "DeepSeek",
                "model": "deepseek-v4-pro",
                "parameters": {
                    "temperature": 0.0,
                    "max_tokens": 4096,
                    "thinking": "disabled",
                    "response_format": "json_object",
                },
                "system_prompt_sha256": _sha256_text(self.guarded_prompt),
                "user_prompt": feedback_prompt,
            },
        )

        try:
            response = DeepSeekProvider().generate(
                model="deepseek-v4-pro",
                system_prompt=self.guarded_prompt,
                user_prompt=feedback_prompt,
                temperature=0.0,
                max_tokens=4096,
                thinking_enabled=False,
            )
        except ProviderError as exc:
            initial["correction_error"] = str(exc)
            return initial

        (case_dir / "raw-response-correction.txt").write_text(response.content, encoding="utf-8")
        correction_cost = estimate_deepseek_cost(response, self.pricing, "deepseek-v4-pro")
        corrected, processed = prediction_from_model(
            case,
            response,
            estimated_cost_usd=correction_cost,
            model_calls=2,
        )
        corrected["latency_ms"] = round(initial["latency_ms"] + response.latency_ms, 3)
        corrected["input_tokens"] = _sum_optional(initial.get("input_tokens"), response.input_tokens)
        corrected["output_tokens"] = _sum_optional(initial.get("output_tokens"), response.output_tokens)
        corrected["estimated_cost_usd"] = _sum_optional(
            initial.get("estimated_cost_usd"), correction_cost
        )
        _write_json(case_dir / "validation-correction.json", processed.to_dict())
        _write_json(case_dir / "metrics-correction.json", _response_metadata(response, correction_cost))
        _write_json(case_dir / "parsed-output.json", corrected)
        return corrected

    def _run_cascade(self, strategy_dir: Path) -> List[Dict[str, Any]]:
        baseline_path = self.run_dir / "baseline" / "predictions.jsonl"
        model_path = self.run_dir / "deepseek-flash-guarded" / "predictions.jsonl"
        if not baseline_path.exists() or not model_path.exists():
            raise FileNotFoundError("Cascade requires completed baseline and guarded Flash runs.")
        baseline = {row["case_id"]: row for row in load_jsonl(baseline_path)}
        model = {row["case_id"]: row for row in load_jsonl(model_path)}
        predictions: List[Dict[str, Any]] = []
        for case in self.cases:
            case_id = str(case["case_id"])
            use_model = baseline[case_id]["decision"] != "ACCEPT"
            selected = dict(model[case_id] if use_model else baseline[case_id])
            selected["cascade_source"] = "deepseek-flash-guarded" if use_model else "baseline"
            predictions.append(selected)
            case_dir = strategy_dir / case_id
            case_dir.mkdir()
            _write_json(case_dir / "parsed-output.json", selected)
        return predictions

    def _provider_failure(
        self, case: Mapping[str, Any], case_dir: Path, error: str
    ) -> Dict[str, Any]:
        prediction = {
            "case_id": case["case_id"],
            "record": CanonicalRecord().to_dict(),
            "source_mappings": {field: None for field in CANONICAL_FIELDS},
            "decision": "REJECT",
            "issue_codes": ["PARSER_FAILURE"],
            "latency_ms": None,
            "input_tokens": None,
            "output_tokens": None,
            "estimated_cost_usd": None,
            "model_calls": 1,
            "provider_error": error,
        }
        _write_json(case_dir / "parsed-output.json", prediction)
        _write_json(case_dir / "provider-error.json", {"error": error})
        return prediction

    def _mark_complete(self, strategy: str) -> None:
        path = self.run_dir / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["strategies_completed"].append(
            {"strategy": strategy, "completed_at_utc": _utc_now()}
        )
        _write_json(path, manifest)

    def _frozen_paths(self) -> Iterable[Path]:
        paths = [
            self.root / "data" / "cases.jsonl",
            self.root / "data" / "answer_key.jsonl",
            self.root / "data" / "mapping_answer_key.jsonl",
            self.root / "evaluation" / "EVALUATION_SPEC.md",
            self.root / "evaluation" / "canonical_record.schema.json",
        ]
        paths.extend(sorted((self.root / "prompts").glob("*.md")))
        return paths


def _translate_internal_issues(issues: Iterable[Issue]) -> List[str]:
    translated: List[str] = []
    for issue in issues:
        if issue.code == "INVALID_FIELD_FORMAT":
            code = {
                "port_count": "INVALID_PORT_COUNT",
                "power_kw": "INVALID_POWER_VALUE",
            }.get(issue.field, "OUTPUT_SCHEMA_ERROR")
        else:
            code = _ISSUE_TRANSLATIONS.get(issue.code, issue.code)
        if code not in translated:
            translated.append(code)
    return translated


def _severity_for_code(code: str) -> IssueSeverity:
    if code in {
        "MISSING_STABLE_IDENTITY",
        "MISSING_SOURCE_LINEAGE",
        "INVALID_PORT_COUNT",
        "INVALID_POWER_VALUE",
        "PROMPT_INJECTION_DETECTED",
        "UNSUPPORTED_VALUE_INVENTED",
        "OUTPUT_SCHEMA_ERROR",
        "PARSER_FAILURE",
    }:
        return IssueSeverity.REJECT
    return IssueSeverity.REVIEW


def _response_metadata(response: ProviderResponse, cost: Optional[float]) -> Dict[str, Any]:
    # Raw content is stored separately. Keeping metrics content-free makes it
    # harder to confuse generated text with provider metadata during analysis.
    metadata = asdict(response)
    metadata.pop("content", None)
    metadata["estimated_cost_usd"] = cost
    return metadata


def _sum_optional(left: Any, right: Any) -> Optional[float]:
    if left is None or right is None:
        return None
    return left + right


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_output(root: Path, args: List[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
