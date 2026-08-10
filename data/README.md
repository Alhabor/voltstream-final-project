# Synthetic Evaluation Data

This directory contains the fixed evaluation set for the VoltStream Intake
Gatekeeper. Every record is synthetic and was written specifically for this
course project. It does not contain Con Edison, contractor, customer, or other
private operational data.

## Files

- `cases.jsonl`: ten immutable model inputs with task instructions and tags.
- `answer_key.jsonl`: expected canonical records, routing decisions, and issue
  codes written before model evaluation.
- `mapping_answer_key.jsonl`: expected source-to-canonical field mappings for
  the seven structured CSV/JSON cases, kept separate so mapping quality can be
  scored independently from value extraction.

Each line is an independent JSON object. Join the files by `case_id`. Keeping
inputs and expected answers separate reduces accidental answer leakage when a
model runner loads the cases. `mapping_answer_key.jsonl` uses JSONPath-like
source paths for JSON and exact header text for CSV.

## Coverage

The set intentionally includes CSV, JSON, and plain-text submissions as well
as normal, alias-heavy, missing-data, contradictory, ambiguous, invalid-value,
abstention, and prompt-injection cases. It is a small fixed benchmark for
comparing a deterministic baseline, an open-weights model, and a closed model;
it is not representative of production prevalence.

Do not edit an answer after seeing model results. If a genuine labeling error
is found, document the correction and rerun every system on the new benchmark
version.
