"""Deterministic scoring for the VoltStream fixed evaluation benchmark.

The scorer intentionally uses only the Python standard library so evaluation
does not depend on the model runtime.  It reports separate quality, safety,
routing, mapping, and efficiency metrics; it never creates a composite score.

Public entry points:

``score_case``
    Score one answer-key row against one prediction row.

``aggregate_scores``
    Score aligned JSON-like rows and optionally create input-format and tag
    slices from the case metadata.

``load_jsonl``
    Read machine-produced JSONL while giving useful line-numbered errors.
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


CANONICAL_FIELDS: tuple[str, ...] = (
    "station_id",
    "address",
    "charger_level",
    "port_count",
    "power_kw",
    "connector_type",
    "operational_status",
    "source_record_id",
)

DECISION_SEVERITY = {"ACCEPT": 0, "HUMAN_REVIEW": 1, "REJECT": 2}
_MISSING = object()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load nonblank JSONL rows and report malformed rows with line numbers."""

    rows: list[dict[str, Any]] = []
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{source}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{source}:{line_number}: each JSONL row must be an object")
            rows.append(row)
    return rows


def score_case(
    answer: Mapping[str, Any],
    prediction: Mapping[str, Any],
    expected_mappings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Score one prediction and return additive counts plus case metadata.

    ``expected_mappings`` is optional because text cases have no structured
    mapping answer.  When a mapping answer exists but the prediction provides
    ``source_mappings=null`` (or omits individual mapping keys), all omitted
    mappings are counted as incorrect.  An explicitly predicted ``null`` can
    receive credit when the expected mapping is deliberately ``null``.
    """

    answer_id = _required_string(answer, "case_id", "answer")
    prediction_id = _required_string(prediction, "case_id", "prediction")
    if answer_id != prediction_id:
        raise ValueError(f"case_id mismatch: answer={answer_id!r}, prediction={prediction_id!r}")

    expected_record = _required_record(answer, "expected_record", "answer")
    predicted_record = _required_record(prediction, "record", "prediction")

    field_correct = 0
    expected_null = 0
    correct_abstentions = 0
    predicted_non_null = 0
    unsupported_values = 0
    for field in CANONICAL_FIELDS:
        expected = expected_record[field]
        predicted = predicted_record[field]
        if _values_equal(expected, predicted):
            field_correct += 1
        if expected is None:
            expected_null += 1
            if predicted is None:
                correct_abstentions += 1
            elif predicted is not None:
                # With this benchmark's closed answer key, a non-null value
                # where gold requires abstention is unsupported by definition.
                unsupported_values += 1
        if predicted is not None:
            predicted_non_null += 1

    expected_decision = answer.get("expected_decision")
    predicted_decision = prediction.get("decision")
    if expected_decision not in DECISION_SEVERITY:
        raise ValueError(f"answer {answer_id}: invalid expected_decision {expected_decision!r}")
    decision_correct = int(predicted_decision == expected_decision)
    expected_non_accept = int(expected_decision != "ACCEPT")
    unsafe_acceptance = int(expected_non_accept == 1 and predicted_decision == "ACCEPT")
    # Unknown decisions are treated as severity -1: failing to produce a safe
    # route is under-routing, rather than an exception that hides the failure.
    predicted_severity = DECISION_SEVERITY.get(predicted_decision, -1)
    unsafe_under_routing = int(predicted_severity < DECISION_SEVERITY[expected_decision])

    expected_issues = _as_string_set(answer.get("expected_issue_codes"), "expected_issue_codes")
    predicted_issues = _as_string_set(prediction.get("issue_codes"), "issue_codes")
    issue_tp = len(expected_issues & predicted_issues)
    issue_fp = len(predicted_issues - expected_issues)
    issue_fn = len(expected_issues - predicted_issues)

    mapping_correct = 0
    mapping_total = 0
    if expected_mappings is not None:
        _require_exact_fields(expected_mappings, "expected_mappings", answer_id)
        mapping_total = len(CANONICAL_FIELDS)
        predicted_mappings = prediction.get("source_mappings")
        if not isinstance(predicted_mappings, Mapping):
            predicted_mappings = {}
        for field in CANONICAL_FIELDS:
            predicted_source = predicted_mappings.get(field, _MISSING)
            if predicted_source is not _MISSING and _values_equal(
                expected_mappings[field], predicted_source
            ):
                mapping_correct += 1

    # Providers do not expose every efficiency metric. Missing values remain
    # explicit ``None`` rather than being guessed or silently converted to 0.
    latency_ms = _optional_nonnegative_number(prediction, "latency_ms")
    input_tokens = _optional_nonnegative_integer(prediction, "input_tokens")
    output_tokens = _optional_nonnegative_integer(prediction, "output_tokens")
    estimated_cost_usd = _optional_nonnegative_number(
        prediction, "estimated_cost_usd"
    )

    return {
        "case_id": answer_id,
        "field_value_correct": field_correct,
        "field_value_total": len(CANONICAL_FIELDS),
        "expected_abstention_count": expected_null,
        "correct_abstention_count": correct_abstentions,
        "predicted_non_null_count": predicted_non_null,
        "unsupported_value_count": unsupported_values,
        "decision_correct_count": decision_correct,
        "decision_total": 1,
        "expected_non_accept_count": expected_non_accept,
        "unsafe_acceptance_count": unsafe_acceptance,
        "unsafe_under_routing_count": unsafe_under_routing,
        "issue_true_positive": issue_tp,
        "issue_false_positive": issue_fp,
        "issue_false_negative": issue_fn,
        "issue_exact_set_count": int(expected_issues == predicted_issues),
        "issue_case_total": 1,
        "mapping_correct": mapping_correct,
        "mapping_total": mapping_total,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost_usd,
    }


def aggregate_scores(
    answers: Sequence[Mapping[str, Any]],
    predictions: Sequence[Mapping[str, Any]],
    *,
    cases: Sequence[Mapping[str, Any]] | None = None,
    mapping_answers: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Score a complete run and optionally aggregate by format and case tag.

    Answer and prediction IDs must form the same unique set. This fail-closed
    alignment prevents a missing model output from disappearing from reported
    denominators. ``mapping_answers`` may cover only structured cases.
    """

    answer_by_id = _index_unique(answers, "answers")
    prediction_by_id = _index_unique(predictions, "predictions")
    _require_same_ids(answer_by_id, prediction_by_id, "predictions")

    mapping_by_id: dict[str, Mapping[str, Any]] = {}
    if mapping_answers is not None:
        raw_mapping_by_id = _index_unique(mapping_answers, "mapping_answers")
        unknown = sorted(set(raw_mapping_by_id) - set(answer_by_id))
        if unknown:
            raise ValueError(f"mapping_answers contain unknown case_ids: {unknown}")
        for case_id, row in raw_mapping_by_id.items():
            value = row.get("expected_mappings")
            if not isinstance(value, Mapping):
                raise ValueError(f"mapping answer {case_id}: expected_mappings must be an object")
            mapping_by_id[case_id] = value

    per_case = [
        score_case(
            answer_by_id[case_id],
            prediction_by_id[case_id],
            mapping_by_id.get(case_id),
        )
        for case_id in answer_by_id
    ]
    result: dict[str, Any] = {
        "overall": _summarize(per_case),
        "by_format": {},
        "by_tag": {},
        "cases": per_case,
    }

    if cases is not None:
        case_by_id = _index_unique(cases, "cases")
        _require_same_ids(answer_by_id, case_by_id, "cases")
        scores_by_id = {row["case_id"]: row for row in per_case}

        formats = sorted({_required_string(row, "input_format", "case") for row in cases})
        for input_format in formats:
            selected = [
                scores_by_id[case_id]
                for case_id, row in case_by_id.items()
                if row["input_format"] == input_format
            ]
            result["by_format"][input_format] = _summarize(selected)

        tags = sorted({tag for row in cases for tag in _case_tags(row)})
        for tag in tags:
            selected = [
                scores_by_id[case_id]
                for case_id, row in case_by_id.items()
                if tag in _case_tags(row)
            ]
            result["by_tag"][tag] = _summarize(selected)

    return result


def _summarize(case_scores: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate additive case counts and derive independent metrics."""

    def total(key: str) -> int | float:
        return sum(row[key] for row in case_scores)

    field_correct = int(total("field_value_correct"))
    field_total = int(total("field_value_total"))
    expected_abstentions = int(total("expected_abstention_count"))
    correct_abstentions = int(total("correct_abstention_count"))
    predicted_non_null = int(total("predicted_non_null_count"))
    unsupported_values = int(total("unsupported_value_count"))
    decision_correct = int(total("decision_correct_count"))
    decision_total = int(total("decision_total"))
    expected_non_accept = int(total("expected_non_accept_count"))
    unsafe_acceptances = int(total("unsafe_acceptance_count"))
    unsafe_under_routing = int(total("unsafe_under_routing_count"))
    issue_tp = int(total("issue_true_positive"))
    issue_fp = int(total("issue_false_positive"))
    issue_fn = int(total("issue_false_negative"))
    issue_exact = int(total("issue_exact_set_count"))
    issue_case_total = int(total("issue_case_total"))
    mapping_correct = int(total("mapping_correct"))
    mapping_total = int(total("mapping_total"))

    issue_precision = _safe_divide(issue_tp, issue_tp + issue_fp)
    issue_recall = _safe_divide(issue_tp, issue_tp + issue_fn)
    # The count form remains defined as 0.0 when gold issues exist but the
    # system predicts none; it is only not-applicable when neither side has an
    # issue anywhere in the selected slice.
    issue_f1 = _safe_divide(2 * issue_tp, 2 * issue_tp + issue_fp + issue_fn)
    latencies = [
        float(row["latency_ms"])
        for row in case_scores
        if row["latency_ms"] is not None
    ]
    input_tokens = [
        int(row["input_tokens"])
        for row in case_scores
        if row["input_tokens"] is not None
    ]
    output_tokens = [
        int(row["output_tokens"])
        for row in case_scores
        if row["output_tokens"] is not None
    ]
    costs = [
        float(row["estimated_cost_usd"])
        for row in case_scores
        if row["estimated_cost_usd"] is not None
    ]

    return {
        "case_count": len(case_scores),
        "field_value_correct": field_correct,
        "field_value_total": field_total,
        "field_value_accuracy": _safe_divide(field_correct, field_total),
        "correct_abstention_count": correct_abstentions,
        "expected_abstention_count": expected_abstentions,
        "correct_abstention_rate": _safe_divide(correct_abstentions, expected_abstentions),
        "unsupported_value_count": unsupported_values,
        "predicted_non_null_count": predicted_non_null,
        "unsupported_value_rate": _safe_divide(unsupported_values, predicted_non_null),
        "decision_correct_count": decision_correct,
        "decision_total": decision_total,
        "decision_accuracy": _safe_divide(decision_correct, decision_total),
        "unsafe_acceptance_count": unsafe_acceptances,
        "expected_non_accept_count": expected_non_accept,
        "unsafe_acceptance_rate": _safe_divide(unsafe_acceptances, expected_non_accept),
        "unsafe_under_routing_count": unsafe_under_routing,
        "unsafe_under_routing_rate": _safe_divide(unsafe_under_routing, decision_total),
        "issue_true_positive": issue_tp,
        "issue_false_positive": issue_fp,
        "issue_false_negative": issue_fn,
        "issue_micro_precision": issue_precision,
        "issue_micro_recall": issue_recall,
        "issue_micro_f1": issue_f1,
        "issue_exact_set_count": issue_exact,
        "issue_exact_set_rate": _safe_divide(issue_exact, issue_case_total),
        "mapping_correct": mapping_correct,
        "mapping_total": mapping_total,
        "mapping_accuracy": _safe_divide(mapping_correct, mapping_total),
        "latency_observed_count": len(latencies),
        "latency_ms_total": sum(latencies) if latencies else None,
        "latency_ms_median": statistics.median(latencies) if latencies else None,
        "input_tokens_observed_count": len(input_tokens),
        "input_tokens_total": sum(input_tokens) if input_tokens else None,
        "output_tokens_observed_count": len(output_tokens),
        "output_tokens_total": sum(output_tokens) if output_tokens else None,
        "estimated_cost_observed_count": len(costs),
        "estimated_cost_usd_total": sum(costs) if costs else None,
    }


def _values_equal(expected: Any, predicted: Any) -> bool:
    """Compare canonical values with only harmless whitespace normalization."""

    if isinstance(expected, str) and isinstance(predicted, str):
        normalize = lambda value: re.sub(r"\s+", " ", value).strip()
        return normalize(expected) == normalize(predicted)
    # bool is a subclass of int but should never equal a numeric field value.
    if isinstance(expected, bool) or isinstance(predicted, bool):
        return expected is predicted
    if isinstance(expected, (int, float)) and isinstance(predicted, (int, float)):
        return math.isfinite(float(expected)) and math.isfinite(float(predicted)) and expected == predicted
    return expected == predicted


def _safe_divide(numerator: int | float, denominator: int | float) -> float | None:
    """Return ``None`` when a metric has no eligible denominator."""

    return numerator / denominator if denominator else None


def _required_string(row: Mapping[str, Any], key: str, owner: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{owner}: {key} must be a non-empty string")
    return value


def _required_record(row: Mapping[str, Any], key: str, owner: str) -> Mapping[str, Any]:
    value = row.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{owner}: {key} must be an object")
    _require_exact_fields(value, key, _required_string(row, "case_id", owner))
    return value


def _require_exact_fields(record: Mapping[str, Any], owner: str, case_id: str) -> None:
    actual = set(record)
    expected = set(CANONICAL_FIELDS)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{case_id} {owner}: canonical fields differ; missing={missing}, extra={extra}")


def _as_string_set(value: Any, owner: str) -> set[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{owner} must be a list of strings")
    return set(value)


def _optional_nonnegative_number(row: Mapping[str, Any], key: str) -> float | None:
    value = row.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"prediction {row.get('case_id')}: {key} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise ValueError(f"prediction {row.get('case_id')}: {key} must be finite and nonnegative")
    return numeric


def _optional_nonnegative_integer(row: Mapping[str, Any], key: str) -> int | None:
    value = row.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"prediction {row.get('case_id')}: {key} must be a nonnegative integer")
    return value


def _index_unique(rows: Iterable[Mapping[str, Any]], owner: str) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        case_id = _required_string(row, "case_id", owner)
        if case_id in indexed:
            raise ValueError(f"{owner} contain duplicate case_id {case_id!r}")
        indexed[case_id] = row
    if not indexed:
        raise ValueError(f"{owner} must not be empty")
    return indexed


def _require_same_ids(
    expected: Mapping[str, Any], actual: Mapping[str, Any], owner: str
) -> None:
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing or extra:
        raise ValueError(f"{owner} case_ids differ; missing={missing}, extra={extra}")


def _case_tags(case: Mapping[str, Any]) -> set[str]:
    tags = case.get("tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ValueError(f"case {case.get('case_id')}: tags must be a list of strings")
    return set(tags)
