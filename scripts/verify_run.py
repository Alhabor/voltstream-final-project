#!/usr/bin/env python3
"""Verify a completed VoltStream experiment bundle without modifying it.

The verifier checks evidence integrity from the frozen benchmark inputs through
the saved aggregate scores. It deliberately recomputes scores in memory and
never calls ``score_run()``, because that command rewrites result files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from evaluation.scoring import aggregate_scores, load_jsonl  # noqa: E402
from scripts.score_run import assess_strategy  # noqa: E402
from voltstream.experiment_runner import STRATEGIES  # noqa: E402
from voltstream.model_pipeline import CANONICAL_FIELDS  # noqa: E402


class RunVerificationError(RuntimeError):
    """Raised after collecting one or more completed-run integrity failures."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = list(errors)
        super().__init__("Run verification failed:\n- " + "\n- ".join(self.errors))


def verify_run(root: Path, run_id: str) -> Dict[str, Any]:
    """Verify ``run_id`` below ``root`` and return a compact success report.

    The function performs reads only. Every expected artifact is interpreted as
    immutable evidence; JSON values are compared semantically so indentation or
    final-newline differences do not create false alarms.
    """

    root = root.resolve()
    run_dir = root / "evaluation" / "runs" / run_id
    errors: List[str] = []
    manifest = _load_json_object(run_dir / "manifest.json", errors, "manifest")
    if not manifest:
        raise RunVerificationError(errors or ["manifest is empty"])
    if manifest.get("run_id") != run_id:
        errors.append(
            f"manifest run_id mismatch: expected {run_id!r}, got {manifest.get('run_id')!r}"
        )

    _verify_frozen_hashes(root, manifest, errors)

    answers = _load_jsonl_safe(root / "data" / "answer_key.jsonl", errors)
    cases = _load_jsonl_safe(root / "data" / "cases.jsonl", errors)
    mappings = _load_jsonl_safe(root / "data" / "mapping_answer_key.jsonl", errors)
    answer_ids = _unique_case_ids(answers, "answer key", errors)

    completed = _completed_strategies(manifest, errors)
    expected_strategies = set(STRATEGIES)
    if set(completed) != expected_strategies:
        errors.append(
            "manifest completed-strategy set mismatch: "
            f"missing={sorted(expected_strategies - set(completed))}, "
            f"extra={sorted(set(completed) - expected_strategies)}"
        )

    prediction_paths = sorted(run_dir.glob("*/predictions.jsonl"))
    prediction_strategies = {path.parent.name for path in prediction_paths}
    if prediction_strategies != expected_strategies:
        errors.append(
            "prediction strategy set mismatch: "
            f"missing={sorted(expected_strategies - prediction_strategies)}, "
            f"extra={sorted(prediction_strategies - expected_strategies)}"
        )

    saved_all = _load_json_object(run_dir / "scores.json", errors, "aggregate scores")
    if saved_all and saved_all.get("run_id") != run_id:
        errors.append("aggregate scores run_id does not match the requested run")
    saved_strategies = saved_all.get("strategies") if saved_all else None
    if not isinstance(saved_strategies, dict):
        errors.append("aggregate scores must contain a strategies object")
        saved_strategies = {}

    verified_cases = 0
    for strategy in STRATEGIES:
        strategy_dir = run_dir / strategy
        predictions = _load_jsonl_safe(strategy_dir / "predictions.jsonl", errors)
        prediction_ids = _unique_case_ids(predictions, f"{strategy} predictions", errors)
        if prediction_ids != answer_ids:
            errors.append(
                f"{strategy} prediction IDs do not align with answer key: "
                f"missing={sorted(answer_ids - prediction_ids)}, "
                f"extra={sorted(prediction_ids - answer_ids)}"
            )
        prediction_by_id = {
            row.get("case_id"): row
            for row in predictions
            if isinstance(row.get("case_id"), str)
        }
        for case_id in sorted(answer_ids & prediction_ids):
            prediction = prediction_by_id[case_id]
            case_dir = strategy_dir / case_id
            parsed = _load_json_object(
                case_dir / "parsed-output.json",
                errors,
                f"{strategy}/{case_id} parsed output",
            )
            if parsed and parsed != prediction:
                errors.append(f"{strategy}/{case_id} parsed output differs from aggregate prediction")
            _verify_validation(strategy, case_id, case_dir, prediction, errors)
            verified_cases += 1

        # Scoring requires complete aligned inputs. Avoid cascading exceptions
        # when an earlier integrity check has already established incompleteness.
        if prediction_ids != answer_ids or not answers or not cases:
            continue
        try:
            recomputed_scores = aggregate_scores(
                answers,
                predictions,
                cases=cases,
                mapping_answers=mappings,
            )
            recomputed = {
                "scores": recomputed_scores,
                "assessment": assess_strategy(answers, predictions, recomputed_scores),
            }
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{strategy} independent scoring failed: {exc}")
            continue

        saved_strategy = saved_strategies.get(strategy)
        if saved_strategy != recomputed:
            errors.append(f"{strategy} aggregate saved score differs from independent recomputation")
        saved_local = _load_json_object(
            strategy_dir / "scores.json", errors, f"{strategy} saved scores"
        )
        if saved_local and saved_local != recomputed:
            errors.append(f"{strategy} saved scores differ from independent recomputation")

    if set(saved_strategies) != expected_strategies:
        errors.append(
            "aggregate score strategy set mismatch: "
            f"missing={sorted(expected_strategies - set(saved_strategies))}, "
            f"extra={sorted(set(saved_strategies) - expected_strategies)}"
        )

    if errors:
        raise RunVerificationError(errors)
    return {
        "run_id": run_id,
        "strategies_verified": len(STRATEGIES),
        "cases_per_strategy": len(answer_ids),
        "per_case_outputs_verified": verified_cases,
        "frozen_files_verified": len(manifest["frozen_sha256"]),
        "scores_recomputed": len(STRATEGIES),
    }


def _verify_frozen_hashes(
    root: Path, manifest: Mapping[str, Any], errors: List[str]
) -> None:
    frozen = manifest.get("frozen_sha256")
    if not isinstance(frozen, dict) or not frozen:
        errors.append("manifest frozen_sha256 must be a non-empty object")
        return
    for relative, expected in sorted(frozen.items()):
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append("manifest frozen_sha256 entries must map paths to strings")
            continue
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"frozen path escapes repository root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"frozen file is missing: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"frozen hash mismatch: {relative}")


def _completed_strategies(manifest: Mapping[str, Any], errors: List[str]) -> List[str]:
    raw = manifest.get("strategies_completed")
    if not isinstance(raw, list):
        errors.append("manifest strategies_completed must be an array")
        return []
    names: List[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict) or not isinstance(item.get("strategy"), str):
            errors.append(f"manifest strategies_completed[{index}] is invalid")
            continue
        names.append(item["strategy"])
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        errors.append(f"manifest contains duplicate completed strategies: {duplicates}")
    return names


def _unique_case_ids(
    rows: Sequence[Mapping[str, Any]], label: str, errors: List[str]
) -> set:
    ids: List[str] = []
    for index, row in enumerate(rows):
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{label} row {index + 1} has an invalid case_id")
        else:
            ids.append(case_id)
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    if duplicates:
        errors.append(f"{label} contains duplicate case IDs: {duplicates}")
    return set(ids)


def _verify_validation(
    strategy: str,
    case_id: str,
    case_dir: Path,
    prediction: Mapping[str, Any],
    errors: List[str],
) -> None:
    # Baseline and cascade are deterministic selections and intentionally do
    # not have model validation artifacts in the existing bundle layout.
    if strategy in {"baseline", "rules-first-cascade"}:
        return

    final_validation = (
        case_dir / "validation-correction.json"
        if (case_dir / "validation-correction.json").exists()
        else case_dir / "validation.json"
    )
    if not final_validation.exists():
        # A sanitized provider failure has no model candidate to validate. It is
        # valid only when both failure evidence and a fail-closed prediction exist.
        if (case_dir / "provider-error.json").is_file() and _is_fail_closed(prediction):
            return
        errors.append(f"{strategy}/{case_id} is missing final validation evidence")
        return

    validation = _load_json_object(
        final_validation, errors, f"{strategy}/{case_id} validation"
    )
    if not validation:
        return
    if validation.get("decision") != prediction.get("decision"):
        errors.append(f"{strategy}/{case_id} validation decision differs from prediction")
    if validation.get("issue_codes") != prediction.get("issue_codes"):
        errors.append(f"{strategy}/{case_id} validation issues differ from prediction")
    candidate = validation.get("candidate")
    if candidate is None:
        if not _record_and_mappings_are_null(prediction):
            errors.append(f"{strategy}/{case_id} parser failure prediction is not null-safe")
        return
    if not isinstance(candidate, dict):
        errors.append(f"{strategy}/{case_id} validation candidate must be an object or null")
        return
    if candidate.get("record") != prediction.get("record"):
        errors.append(f"{strategy}/{case_id} validation record differs from prediction")
    if candidate.get("source_mappings") != prediction.get("source_mappings"):
        errors.append(f"{strategy}/{case_id} validation mappings differ from prediction")


def _record_and_mappings_are_null(prediction: Mapping[str, Any]) -> bool:
    return all(
        isinstance(prediction.get(key), dict)
        and set(prediction[key]) == set(CANONICAL_FIELDS)
        and all(prediction[key][field] is None for field in CANONICAL_FIELDS)
        for key in ("record", "source_mappings")
    )


def _is_fail_closed(prediction: Mapping[str, Any]) -> bool:
    return (
        prediction.get("decision") == "REJECT"
        and "PARSER_FAILURE" in (prediction.get("issue_codes") or [])
        and _record_and_mappings_are_null(prediction)
    )


def _load_jsonl_safe(path: Path, errors: List[str]) -> List[Dict[str, Any]]:
    try:
        return load_jsonl(path)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        errors.append(f"cannot load {path}: {exc}")
        return []


def _load_json_object(
    path: Path, errors: List[str], label: str
) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"cannot load {label} at {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} at {path} must be a JSON object")
        return {}
    return value


def main(argv: Sequence[str] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    try:
        report = verify_run(ROOT, args.run_id)
    except RunVerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
