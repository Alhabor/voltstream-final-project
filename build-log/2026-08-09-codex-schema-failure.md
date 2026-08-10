# Failed Run: Unsupported Codex Response-Schema Keyword

## What was observed

Run `2026-08-09-final-v2` completed the baseline and all DeepSeek strategies,
but every `codex-terra-guarded` case exited before a model response. The runner
correctly converted each infrastructure error into a fail-closed `REJECT`, so
scoring completed, but those rows cannot represent closed-model capability.

## Diagnosis

A direct, synthetic CLI diagnostic exposed the provider error: structured
output does not permit JSON Schema's `uniqueItems` keyword on `issue_codes`.
The repository's independent `parse_model_candidate` already verifies that
issue codes are unique, so the provider-side keyword was redundant.

## Decision

The unsupported keyword is removed from the response-shaping schema; the local
safety check remains unchanged and tested. The complete v2 artifacts are
preserved under `evaluation/failed-runs/2026-08-09-codex-schema-failure/`, but
are excluded from the final comparison. A live structured-output smoke test is
required before a new all-strategy run.

No model-quality conclusion is drawn from the ten Codex infrastructure errors.

