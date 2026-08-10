"""Strict safety boundary for untrusted model-generated candidates.

The model is allowed to propose a canonical record, source-field mappings, and
issue codes. It is never allowed to decide whether a record is accepted. This
module parses the proposal, rejects schema drift, reruns local safety controls,
and computes the final route from deterministic issue severities.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .models import CanonicalRecord, Issue, IssueSeverity, RouteDecision
from .validation import detect_payload_issues, route_for_issues, validate_record


CANONICAL_FIELDS = (
    "station_id",
    "address",
    "charger_level",
    "port_count",
    "power_kw",
    "connector_type",
    "operational_status",
    "source_record_id",
)
MODEL_OUTPUT_FIELDS = ("record", "source_mappings", "issue_codes")

# This taxonomy is the fixed v1 benchmark contract in EVALUATION_SPEC.md.
ALLOWED_ISSUE_CODES = frozenset(
    {
        "MISSING_REQUIRED_FIELD",
        "MISSING_STABLE_IDENTITY",
        "MISSING_SOURCE_LINEAGE",
        "AMBIGUOUS_FIELD_VALUE",
        "LEVEL_POWER_CONFLICT",
        "INVALID_PORT_COUNT",
        "INVALID_POWER_VALUE",
        "PROMPT_INJECTION_DETECTED",
        "UNSUPPORTED_VALUE_INVENTED",
        "OUTPUT_SCHEMA_ERROR",
        "PARSER_FAILURE",
    }
)

_MODEL_ISSUE_SEVERITIES = {
    "MISSING_REQUIRED_FIELD": IssueSeverity.REVIEW,
    "MISSING_STABLE_IDENTITY": IssueSeverity.REJECT,
    "MISSING_SOURCE_LINEAGE": IssueSeverity.REJECT,
    "AMBIGUOUS_FIELD_VALUE": IssueSeverity.REVIEW,
    "LEVEL_POWER_CONFLICT": IssueSeverity.REVIEW,
    "INVALID_PORT_COUNT": IssueSeverity.REJECT,
    "INVALID_POWER_VALUE": IssueSeverity.REJECT,
    "PROMPT_INJECTION_DETECTED": IssueSeverity.REJECT,
    "UNSUPPORTED_VALUE_INVENTED": IssueSeverity.REJECT,
    "OUTPUT_SCHEMA_ERROR": IssueSeverity.REJECT,
    "PARSER_FAILURE": IssueSeverity.REJECT,
}

_CHARGER_LEVELS = {"L1", "L2", "DCFC"}
_CONNECTOR_TYPES = {"J1772", "CCS1", "NACS", "CHADEMO", "OTHER"}
_OPERATIONAL_STATUSES = {
    "operational",
    "temporarily_unavailable",
    "planned",
    "retired",
    "unknown",
}

_FENCED_JSON = re.compile(
    r"\A```(?:json)?[ \t]*\r?\n(?P<body>.*?)\r?\n```\Z",
    flags=re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class ModelCandidate:
    """A model proposal that has passed the complete structural contract."""

    record: CanonicalRecord
    source_mappings: Dict[str, Optional[str]]
    issue_codes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record": self.record.to_dict(),
            "source_mappings": dict(self.source_mappings),
            "issue_codes": list(self.issue_codes),
        }


@dataclass
class ModelPostprocessResult:
    """Safe result returned even when parsing or schema validation fails."""

    candidate: Optional[ModelCandidate]
    decision: RouteDecision
    issues: List[Issue] = field(default_factory=list)

    @property
    def issue_codes(self) -> List[str]:
        """Return unique issue codes in evidence-preserving order."""

        return list(dict.fromkeys(issue.code for issue in self.issues))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate": None if self.candidate is None else self.candidate.to_dict(),
            "decision": self.decision.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "issue_codes": self.issue_codes,
        }


class ModelOutputError(ValueError):
    """Typed internal error converted to a safe, machine-scoreable rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_model_candidate(raw_response: str) -> ModelCandidate:
    """Parse and strictly validate one raw model response.

    A bare JSON object or a single ``json`` Markdown fence is permitted. Prose,
    multiple fences, missing or extra keys, coercible-but-wrong types, and values
    outside the fixed enums are rejected rather than repaired.
    """

    if not isinstance(raw_response, str) or not raw_response.strip():
        raise ModelOutputError("PARSER_FAILURE", "Model response is empty or is not text.")

    json_text = _unwrap_json_fence(raw_response.strip())
    try:
        payload = json.loads(json_text, parse_constant=_reject_non_json_constant)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        detail = exc.msg if isinstance(exc, json.JSONDecodeError) else str(exc)
        raise ModelOutputError("PARSER_FAILURE", f"Model response is not valid JSON: {detail}.") from exc

    if not isinstance(payload, dict):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "Model output must be a JSON object.")
    _require_exact_keys(payload, MODEL_OUTPUT_FIELDS, "model output")

    record_payload = payload["record"]
    mapping_payload = payload["source_mappings"]
    issue_codes = payload["issue_codes"]
    if not isinstance(record_payload, dict):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "record must be an object.")
    if not isinstance(mapping_payload, dict):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "source_mappings must be an object.")
    _require_exact_keys(record_payload, CANONICAL_FIELDS, "record")
    _require_exact_keys(mapping_payload, CANONICAL_FIELDS, "source_mappings")

    record = _parse_record(record_payload)
    source_mappings = _parse_source_mappings(mapping_payload)
    parsed_issue_codes = _parse_issue_codes(issue_codes)
    return ModelCandidate(record, source_mappings, parsed_issue_codes)


def postprocess_model_response(raw_response: str, source_payload: str) -> ModelPostprocessResult:
    """Convert a raw model response into a locally routed safe result.

    ``source_payload`` is the original untrusted contractor content, not the
    prompt template. It is checked independently for benchmark injection signals.
    """

    try:
        candidate = parse_model_candidate(raw_response)
    except ModelOutputError as exc:
        issue = Issue(
            code=exc.code,
            severity=IssueSeverity.REJECT,
            message=str(exc),
        )
        return ModelPostprocessResult(
            candidate=None,
            decision=RouteDecision.REJECT,
            issues=[issue],
        )

    # Deterministic findings take precedence and retain field-level explanations.
    local_issues = [
        *validate_record(candidate.record),
        *_validate_provenance(candidate),
        *detect_payload_issues(source_payload),
    ]
    issues = _merge_model_issues(local_issues, candidate.issue_codes)
    return ModelPostprocessResult(
        candidate=candidate,
        decision=route_for_issues(issues),
        issues=issues,
    )


def _unwrap_json_fence(response: str) -> str:
    if not response.startswith("```"):
        return response
    match = _FENCED_JSON.fullmatch(response)
    if match is None:
        raise ModelOutputError(
            "PARSER_FAILURE",
            "Markdown output must contain exactly one JSON code fence and no surrounding prose.",
        )
    return match.group("body").strip()


def _reject_non_json_constant(value: str) -> None:
    """Reject NaN and infinities, which Python accepts but JSON forbids."""

    raise ValueError(f"non-standard numeric constant {value}")


def _require_exact_keys(value: Dict[str, Any], expected: Tuple[str, ...], label: str) -> None:
    actual_keys = set(value)
    expected_keys = set(expected)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        details = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if extra:
            details.append(f"extra keys: {', '.join(extra)}")
        raise ModelOutputError(
            "OUTPUT_SCHEMA_ERROR",
            f"{label} has an invalid key set ({'; '.join(details)}).",
        )


def _parse_record(value: Dict[str, Any]) -> CanonicalRecord:
    string_fields = ("station_id", "address", "source_record_id")
    for field_name in string_fields:
        _require_nullable_nonempty_string(value[field_name], f"record.{field_name}")

    _require_nullable_enum(value["charger_level"], _CHARGER_LEVELS, "record.charger_level")
    _require_nullable_enum(value["connector_type"], _CONNECTOR_TYPES, "record.connector_type")
    _require_nullable_enum(
        value["operational_status"],
        _OPERATIONAL_STATUSES,
        "record.operational_status",
    )

    port_count = value["port_count"]
    if port_count is not None and (isinstance(port_count, bool) or not isinstance(port_count, int)):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "record.port_count must be an integer or null.")

    power_kw = value["power_kw"]
    if power_kw is not None:
        if isinstance(power_kw, bool) or not isinstance(power_kw, (int, float)):
            raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "record.power_kw must be a number or null.")
        if not math.isfinite(power_kw):
            raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "record.power_kw must be finite.")

    return CanonicalRecord(**value)


def _parse_source_mappings(value: Dict[str, Any]) -> Dict[str, Optional[str]]:
    for field_name in CANONICAL_FIELDS:
        _require_nullable_nonempty_string(value[field_name], f"source_mappings.{field_name}")
    # Rebuild in canonical order so persisted results remain stable across runs.
    return {field_name: value[field_name] for field_name in CANONICAL_FIELDS}


def _parse_issue_codes(value: Any) -> List[str]:
    if not isinstance(value, list):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "issue_codes must be an array.")
    if any(not isinstance(code, str) for code in value):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "Every issue code must be a string.")
    if len(value) != len(set(value)):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", "issue_codes must not contain duplicates.")
    unsupported = sorted(set(value) - ALLOWED_ISSUE_CODES)
    if unsupported:
        raise ModelOutputError(
            "OUTPUT_SCHEMA_ERROR",
            f"Unsupported issue codes: {', '.join(unsupported)}.",
        )
    return list(value)


def _require_nullable_nonempty_string(value: Any, label: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", f"{label} must be a non-empty string or null.")


def _require_nullable_enum(value: Any, allowed: set, label: str) -> None:
    if value is not None and (not isinstance(value, str) or value not in allowed):
        choices = ", ".join(sorted(allowed))
        raise ModelOutputError("OUTPUT_SCHEMA_ERROR", f"{label} must be null or one of: {choices}.")


def _merge_model_issues(local_issues: List[Issue], model_codes: List[str]) -> List[Issue]:
    """Merge model claims without replacing more specific local evidence."""

    merged = list(local_issues)
    locally_reported_codes = {issue.code for issue in local_issues}
    for code in model_codes:
        if code in locally_reported_codes:
            continue
        merged.append(
            Issue(
                code=code,
                severity=_MODEL_ISSUE_SEVERITIES[code],
                message="Issue reported by the model candidate and retained for review.",
            )
        )
    return merged


def _validate_provenance(candidate: ModelCandidate) -> List[Issue]:
    """Reject non-null model values that have no claimed source evidence.

    The scorer later checks whether a claimed mapping is correct. This local
    gate handles the more fundamental failure: a model returning a business
    value while explicitly admitting that it has no source mapping.
    """

    issues: List[Issue] = []
    record = candidate.record.to_dict()
    for field_name in CANONICAL_FIELDS:
        if record[field_name] is not None and candidate.source_mappings[field_name] is None:
            issues.append(
                Issue(
                    code="UNSUPPORTED_VALUE_INVENTED",
                    severity=IssueSeverity.REJECT,
                    field=field_name,
                    message="Non-null model value has no source evidence mapping.",
                )
            )
    return issues
