#!/usr/bin/env python3
"""Validate the fixed benchmark without optional third-party dependencies.

The project keeps JSON Schemas for interoperability, while this script enforces
the highest-risk cross-file contracts in a stock Python environment: immutable
IDs, exact canonical keys, answer coverage, field types, enum values, routing
labels, structured mapping coverage, and agreement with the runtime validator.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVALUATION = ROOT / "evaluation"

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
DECISIONS = {"ACCEPT", "HUMAN_REVIEW", "REJECT"}
LEVELS = {"L1", "L2", "DCFC", None}
CONNECTORS = {"J1772", "CCS1", "NACS", "CHADEMO", "OTHER", None}
STATUSES = {
    "operational",
    "temporarily_unavailable",
    "planned",
    "retired",
    "unknown",
    None,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise AssertionError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def index_unique(rows: Iterable[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or case_id in indexed:
            raise AssertionError(f"{label} contains an invalid or duplicate case_id: {case_id!r}")
        indexed[case_id] = row
    return indexed


def validate_answer(case_id: str, answer: dict[str, Any]) -> None:
    record = answer.get("expected_record")
    if not isinstance(record, dict) or tuple(record) != CANONICAL_FIELDS:
        raise AssertionError(f"{case_id}: canonical keys or key order differ from the contract")
    if answer.get("expected_decision") not in DECISIONS:
        raise AssertionError(f"{case_id}: invalid routing decision")
    if record["charger_level"] not in LEVELS:
        raise AssertionError(f"{case_id}: invalid charger_level")
    if record["connector_type"] not in CONNECTORS:
        raise AssertionError(f"{case_id}: invalid connector_type")
    if record["operational_status"] not in STATUSES:
        raise AssertionError(f"{case_id}: invalid operational_status")
    if record["port_count"] is not None and (
        not isinstance(record["port_count"], int) or isinstance(record["port_count"], bool)
    ):
        raise AssertionError(f"{case_id}: port_count must be an integer or null")
    if record["power_kw"] is not None and (
        not isinstance(record["power_kw"], (int, float))
        or isinstance(record["power_kw"], bool)
    ):
        raise AssertionError(f"{case_id}: power_kw must be numeric or null")


def main() -> int:
    cases = index_unique(read_jsonl(DATA / "cases.jsonl"), "cases")
    answers = index_unique(read_jsonl(DATA / "answer_key.jsonl"), "answer key")
    mappings = index_unique(
        read_jsonl(DATA / "mapping_answer_key.jsonl"), "mapping answer key"
    )

    expected_ids = {f"EVG-{number:03d}" for number in range(1, 11)}
    if set(cases) != expected_ids or set(answers) != expected_ids:
        raise AssertionError("cases and answer key must contain exactly EVG-001 through EVG-010")

    structured_ids = {
        case_id
        for case_id, case in cases.items()
        if case.get("input_format") in {"csv", "json"}
    }
    if set(mappings) != structured_ids:
        raise AssertionError("mapping answers must cover every and only structured case")

    for case_id, case in cases.items():
        if not str(case.get("source_name", "")).startswith("synthetic_"):
            raise AssertionError(f"{case_id}: source must be explicitly synthetic")
        payload = case.get("payload")
        if not isinstance(payload, str) or not payload:
            raise AssertionError(f"{case_id}: payload must be non-empty text")
        if case["input_format"] == "csv":
            parsed = list(csv.DictReader(io.StringIO(payload)))
            if len(parsed) != 1:
                raise AssertionError(f"{case_id}: CSV benchmark case must contain one row")
        elif case["input_format"] == "json":
            if not isinstance(json.loads(payload), dict):
                raise AssertionError(f"{case_id}: JSON benchmark case must be one object")

        validate_answer(case_id, answers[case_id])
        if case_id in mappings and tuple(mappings[case_id]["expected_mappings"]) != CANONICAL_FIELDS:
            raise AssertionError(f"{case_id}: mapping keys differ from canonical contract")

    schema = json.loads((EVALUATION / "canonical_record.schema.json").read_text())
    if tuple(schema["required"]) != CANONICAL_FIELDS:
        raise AssertionError("canonical JSON Schema required fields differ from fixtures")

    # Import after local fixture checks so a packaging error has a clear origin.
    sys.path.insert(0, str(ROOT / "src"))
    from voltstream.validation import (  # pylint: disable=import-outside-toplevel
        ALLOWED_CONNECTORS,
        ALLOWED_LEVELS,
        ALLOWED_STATUSES,
    )

    if ALLOWED_LEVELS != LEVELS - {None}:
        raise AssertionError("runtime charger levels differ from evaluation schema")
    if ALLOWED_CONNECTORS != CONNECTORS - {None}:
        raise AssertionError("runtime connector types differ from evaluation schema")
    if ALLOWED_STATUSES != STATUSES - {None}:
        raise AssertionError("runtime statuses differ from evaluation schema")

    print(
        "Fixture validation passed: "
        f"{len(cases)} cases, {len(answers)} answers, {len(mappings)} mapping keys."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

