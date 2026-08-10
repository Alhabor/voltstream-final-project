"""Auditable rule-based parser used both as baseline and safety layer."""

from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .models import CanonicalRecord, InputEnvelope, InputFormat, Issue, IssueSeverity


# Alias matching is intentionally exact after punctuation/case normalization. The
# baseline must expose unfamiliar fields instead of pretending that it understood.
FIELD_ALIASES: dict[str, set[str]] = {
    "station_id": {"station id", "station no", "site id", "site ref", "site number"},
    "address": {"address", "site address", "site location", "location"},
    "charger_level": {"charger level", "charging level", "level", "evse level"},
    "port_count": {"port count", "ports", "connector qty", "number of connectors"},
    "power_kw": {"power kw", "rated output", "rated power", "max kw", "power"},
    "connector_type": {"connector type", "connector", "plug type", "plug"},
    "operational_status": {"operational status", "station status", "status"},
    "source_record_id": {"source record id", "record id", "vendor record id"},
}

_ALIAS_LOOKUP = {
    alias: canonical for canonical, aliases in FIELD_ALIASES.items() for alias in aliases
}


@dataclass
class BaselineParseResult:
    """Intermediate parse output retained for audit and scoring."""

    record: CanonicalRecord
    issues: list[Issue] = field(default_factory=list)
    unmapped_fields: list[str] = field(default_factory=list)
    source_mappings: dict[str, Optional[str]] = field(default_factory=dict)


def _normalize_key(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[_\-.]+", " ", value.strip().lower()))


def _clean_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _parse_integer(value: Any) -> Optional[int]:
    cleaned = _clean_string(value)
    if cleaned is None:
        return None
    # Reject decimals rather than silently rounding a physical port count.
    if not re.fullmatch(r"[+-]?\d+", cleaned.replace(",", "")):
        raise ValueError(f"expected an integer, received {cleaned!r}")
    return int(cleaned.replace(",", ""))


def _parse_power_kw(value: Any) -> Optional[float]:
    cleaned = _clean_string(value)
    if cleaned is None:
        return None
    match = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(kw|w)?", cleaned.lower())
    if not match:
        raise ValueError(f"expected numeric power in W or kW, received {cleaned!r}")
    amount = float(match.group(1))
    return amount / 1000 if match.group(2) == "w" else amount


def _normalize_level(value: Any) -> Optional[str]:
    cleaned = _clean_string(value)
    if cleaned is None:
        return None
    key = re.sub(r"[\s_-]+", "", cleaned.lower())
    aliases = {
        "1": "L1",
        "l1": "L1",
        "level1": "L1",
        "2": "L2",
        "l2": "L2",
        "level2": "L2",
        "dcfc": "DCFC",
        "dcfast": "DCFC",
        "dcfastcharging": "DCFC",
        "level3": "DCFC",
        "l3": "DCFC",
    }
    return aliases.get(key, cleaned.upper())


def _normalize_connector(value: Any) -> Optional[str]:
    cleaned = _clean_string(value)
    if cleaned is None:
        return None
    key = re.sub(r"[\s_-]+", "", cleaned.lower())
    aliases = {
        "j1772": "J1772",
        "saej1772": "J1772",
        "ccs": "CCS1",
        "ccs1": "CCS1",
        "combo": "CCS1",
        "chademo": "CHADEMO",
        "nacs": "NACS",
        "tesla": "NACS",
    }
    return aliases.get(key, cleaned)


def _normalize_status(value: Any) -> Optional[str]:
    cleaned = _clean_string(value)
    if cleaned is None:
        return None
    key = re.sub(r"[\s_-]+", "", cleaned.lower())
    aliases = {
        "available": "operational",
        "active": "operational",
        "operational": "operational",
        "inservice": "operational",
        "offline": "temporarily_unavailable",
        "outofservice": "temporarily_unavailable",
        "maintenance": "temporarily_unavailable",
        "temporarilyunavailable": "temporarily_unavailable",
        "planned": "planned",
        "retired": "retired",
        "unknown": "unknown",
    }
    return aliases.get(key, cleaned.lower())


_CONVERTERS = {
    "station_id": _clean_string,
    "address": _clean_string,
    "charger_level": _normalize_level,
    "port_count": _parse_integer,
    "power_kw": _parse_power_kw,
    "connector_type": _normalize_connector,
    "operational_status": _normalize_status,
    "source_record_id": _clean_string,
}


class DeterministicBaseline:
    """Parse known contractor formats without semantic guesses."""

    def parse_envelope(self, envelope: InputEnvelope) -> tuple[list[dict[str, Any]], list[Issue]]:
        try:
            if envelope.input_format is InputFormat.CSV:
                rows = list(csv.DictReader(io.StringIO(envelope.content)))
                if not rows:
                    raise ValueError("CSV contains no data rows")
                return rows, []
            if envelope.input_format is InputFormat.JSON:
                payload = json.loads(envelope.content)
                if isinstance(payload, dict):
                    return [payload], []
                if isinstance(payload, list) and payload and all(isinstance(row, dict) for row in payload):
                    return payload, []
                raise ValueError("JSON must be an object or a non-empty list of objects")
            if envelope.input_format is InputFormat.TEXT:
                row = self._parse_key_value_text(envelope.content)
                if not row:
                    raise ValueError("text must contain one or more 'field: value' lines")
                return [row], []
        except (csv.Error, json.JSONDecodeError, ValueError) as exc:
            return [], [
                Issue(
                    code="MALFORMED_SUBMISSION",
                    severity=IssueSeverity.REJECT,
                    message=str(exc),
                )
            ]
        raise ValueError(f"unsupported input format: {envelope.input_format}")

    @staticmethod
    def _parse_key_value_text(content: str) -> dict[str, str]:
        row: dict[str, str] = {}
        for line_number, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            key, separator, value = line.partition(":")
            if separator and key.strip() and value.strip():
                row[key.strip()] = value.strip()
            else:
                # Preserve rather than discard prose. It becomes an unmapped field
                # downstream and therefore forces HUMAN_REVIEW (or REJECT when key
                # identity data is also absent). This is important for auditability
                # and prevents instruction-like text from bypassing review.
                row[f"unparsed line {line_number}"] = line
        return row

    def canonicalize(self, raw: dict[str, Any]) -> BaselineParseResult:
        values: dict[str, Any] = {}
        source_mappings: dict[str, Optional[str]] = {}
        issues: list[Issue] = []
        unmapped: list[str] = []

        for raw_key, raw_value in raw.items():
            canonical_key = _ALIAS_LOOKUP.get(_normalize_key(str(raw_key)))
            if canonical_key is None:
                unmapped.append(str(raw_key))
                continue
            try:
                converted_value = _CONVERTERS[canonical_key](raw_value)
            except ValueError as exc:
                issues.append(
                    Issue(
                        code="INVALID_FIELD_FORMAT",
                        severity=IssueSeverity.REJECT,
                        field=canonical_key,
                        message=str(exc),
                    )
                )
                continue

            if canonical_key not in values:
                values[canonical_key] = converted_value
                source_mappings[canonical_key] = str(raw_key)
            elif values[canonical_key] is None and converted_value is not None:
                # A populated alias safely fills an earlier blank alias.
                values[canonical_key] = converted_value
                source_mappings[canonical_key] = str(raw_key)
            elif converted_value is not None and converted_value != values[canonical_key]:
                # Preserve the first populated value and surface the disagreement.
                source_mappings[canonical_key] = None
                issues.append(
                    Issue(
                        code="DUPLICATE_CANONICAL_FIELD",
                        severity=IssueSeverity.REVIEW,
                        field=canonical_key,
                        message=f"Conflicting source fields map to {canonical_key!r}.",
                    )
                )

        if unmapped:
            issues.append(
                Issue(
                    code="UNMAPPED_FIELDS",
                    severity=IssueSeverity.REVIEW,
                    message="One or more source fields are not in the audited alias dictionary.",
                )
            )
        complete_mappings = {
            field_name: source_mappings.get(field_name)
            for field_name in CanonicalRecord.__dataclass_fields__
        }
        return BaselineParseResult(
            CanonicalRecord(**values), issues, sorted(unmapped), complete_mappings
        )
