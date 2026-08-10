"""Deterministic safety checks and explainable routing policy."""

from __future__ import annotations

import re

from .models import CanonicalRecord, Issue, IssueSeverity, RouteDecision


ALLOWED_LEVELS = {"L1", "L2", "DCFC"}
ALLOWED_CONNECTORS = {"J1772", "CCS1", "CHADEMO", "NACS", "OTHER"}
ALLOWED_STATUSES = {
    "operational",
    "temporarily_unavailable",
    "planned",
    "retired",
    "unknown",
}

# This intentionally narrow detector catches explicit imperative attacks while
# keeping ordinary contractor prose out of the security path. It is an
# auditable benchmark control, not a claim of general prompt-injection defense.
_INJECTION_PATTERN = re.compile(
    r"(?is)\b(?:ignore|bypass|override)\b.{0,80}\b"
    r"(?:instruction|rule|validation|system|approve|accept)\b"
)


def detect_payload_issues(content: str) -> list[Issue]:
    """Detect an explicit attempt by payload text to control system behavior."""

    if _INJECTION_PATTERN.search(content):
        return [
            Issue(
                code="PROMPT_INJECTION_DETECTED",
                severity=IssueSeverity.REJECT,
                message="Payload contains an instruction to override system behavior.",
            )
        ]
    return []


def validate_record(record: CanonicalRecord) -> list[Issue]:
    """Return all known problems without mutating the candidate record."""

    issues: list[Issue] = []
    if record.station_id is None:
        issues.append(
            _issue(
                "MISSING_STABLE_IDENTITY",
                IssueSeverity.REJECT,
                "station_id",
                "Station ID is required and must not be synthesized.",
            )
        )
    if record.source_record_id is None:
        issues.append(
            _issue(
                "MISSING_SOURCE_LINEAGE",
                IssueSeverity.REJECT,
                "source_record_id",
                "Source record ID is required for lineage and must not be synthesized.",
            )
        )

    # Missing operational attributes do not justify discarding the original row,
    # but they prevent automatic acceptance into a source of truth.
    for field_name, label in (
        ("address", "site address"),
        ("charger_level", "charger level"),
        ("port_count", "port count"),
        ("power_kw", "rated power"),
    ):
        if getattr(record, field_name) is None:
            issues.append(
                _issue(
                    "MISSING_REQUIRED_FIELD",
                    IssueSeverity.REVIEW,
                    field_name,
                    f"{label.capitalize()} is missing and requires review.",
                )
            )

    if record.port_count is not None and record.port_count <= 0:
        issues.append(_issue("INVALID_PORT_COUNT", IssueSeverity.REJECT, "port_count", "Port count must be greater than zero."))
    if record.power_kw is not None and record.power_kw <= 0:
        issues.append(_issue("INVALID_POWER_VALUE", IssueSeverity.REJECT, "power_kw", "Rated power must be greater than zero."))
    if record.charger_level is not None and record.charger_level not in ALLOWED_LEVELS:
        issues.append(_issue("UNKNOWN_CHARGER_LEVEL", IssueSeverity.REVIEW, "charger_level", "Charger level is outside the supported vocabulary."))
    if record.connector_type is not None and record.connector_type not in ALLOWED_CONNECTORS:
        issues.append(_issue("UNKNOWN_CONNECTOR", IssueSeverity.REVIEW, "connector_type", "Connector type is outside the supported vocabulary."))
    if record.operational_status is not None and record.operational_status not in ALLOWED_STATUSES:
        issues.append(_issue("UNKNOWN_STATUS", IssueSeverity.REVIEW, "operational_status", "Operational status is outside the supported vocabulary."))

    # These wide bands flag only obvious contradictions. Borderline engineering
    # classifications remain human decisions rather than being over-automated.
    if record.power_kw is not None:
        contradictory = (
            (record.charger_level == "L1" and record.power_kw > 3.0)
            or (record.charger_level == "L2" and not 2.0 <= record.power_kw <= 80.0)
            or (record.charger_level == "DCFC" and record.power_kw < 20.0)
        )
        if contradictory:
            issues.append(
                _issue(
                    "LEVEL_POWER_CONFLICT",
                    IssueSeverity.REVIEW,
                    "power_kw",
                    "Rated power is inconsistent with the reported charger level.",
                )
            )
    return issues


def route_for_issues(issues: list[Issue]) -> RouteDecision:
    """Apply the conservative precedence REJECT > HUMAN_REVIEW > ACCEPT."""

    severities = {issue.severity for issue in issues}
    if IssueSeverity.REJECT in severities:
        return RouteDecision.REJECT
    if IssueSeverity.REVIEW in severities:
        return RouteDecision.HUMAN_REVIEW
    return RouteDecision.ACCEPT


def _issue(code: str, severity: IssueSeverity, field: str, message: str) -> Issue:
    return Issue(code=code, severity=severity, field=field, message=message)
