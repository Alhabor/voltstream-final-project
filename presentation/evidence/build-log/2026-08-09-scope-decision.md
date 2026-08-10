# Scope decision: intake gatekeeping only

- Date: 2026-08-09
- Owner/agent: project team
- Status: SUPPORTED
- Related commit(s): to be added by the integrating agent
- Related cases/results: evaluation cases not yet created

## Question

What portion of the five-layer VoltStream product vision can be implemented,
tested, and explained honestly for the capstone?

## Alternatives considered

1. Build the full five-layer data platform.
2. Build station reconciliation across multiple master-data sources.
3. Build charging-session anomaly diagnosis.
4. Build one intake gatekeeper for CSV, JSON, and plain-text submissions.

## Evidence and constraints

- The capstone explicitly favors one specific, defensible slice over a complete
  system.
- Intake extraction and routing permit a fixed answer key, simple baseline,
  multi-model comparison, category-level scoring, abstention cases, and a live
  demonstration within one coherent task.
- The broader alternatives add databases, entity-resolution truth sets, sensor
  behavior, or production integrations that are unnecessary to answer the
  selected research question.
- Public DOE/AFDC evidence confirms that EV charging data can enter a major
  station directory through APIs, spreadsheets, and manual workflows.

## Decision

Implement and evaluate only **VoltStream Intake Gatekeeper**:

> supported input -> canonical candidate -> deterministic validation ->
> `ACCEPT`, `HUMAN_REVIEW`, or `REJECT`

The complete five-layer materials in `../Doc/` remain product vision and
supporting ideation. They are not implementation claims and are outside the Git
repository.

## Guardrails

- No silent imputation or overwrite.
- Public/synthetic data only.
- CSV, JSON, and plain text only.
- No production deployment or regulatory-compliance claim.
- Evaluation evidence must precede the recommendation.

## Next action

Freeze the canonical contract, cases, and answer key before running models.

