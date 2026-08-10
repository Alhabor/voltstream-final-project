# Rejected as default, pending test: unrestricted end-to-end LLM cleaning

- Date: 2026-08-09
- Owner/agent: project team
- Status: PROPOSED
- Related commit(s): to be added by the integrating agent
- Related cases/results: none yet

## Question

Should one language-model prompt be allowed to parse, infer missing values,
resolve conflicts, “clean” the record, and approve it without deterministic
validation or human review?

## Hypothesis written before the test

An unrestricted cleaner may produce fluent and complete-looking records, but
is expected to have a higher unsupported-value or unsafe-acceptance rate on
missing, conflicting, and adversarial cases than a guarded pipeline.

This is a **risk hypothesis**, not an experimental result. The project must not
present it as a demonstrated failure until the planned comparison is run.

## Why it is not the implementation default

- It collapses extraction, transformation, validation, and approval into an
  output that is difficult to audit.
- A complete-looking record can hide whether a value came from the source, a
  deterministic conversion, or model inference.
- Source text may contain instructions that should be treated as data.
- It removes the explicit abstention and human-review boundary required by the
  selected product concept.

These are architectural reasons to quarantine the route, not measured evidence
that it performs worse.

## Current decision

Reject unrestricted cleaning as the prototype's default architecture because
it violates the chosen provenance, abstention, and deterministic-approval
boundaries. Keep it as a quarantined experimental comparator so the final
presentation can distinguish an architectural rejection from a measured
performance failure. Its experimental status remains `PROPOSED`.

## Planned method

After the answer key is frozen, run an unrestricted-cleaner prompt on the same
fixed cases used by the guarded pipeline. At minimum, compare:

- exact field/value accuracy;
- unsupported-field rate;
- unsafe acceptance rate;
- correct abstention rate;
- category-level errors on missing, conflict, and prompt-injection cases; and
- latency/token use when available.

Record the exact prompt/model/version and raw outputs. Do not permit the trial
output to modify source files or an authoritative dataset.

## Stop/continue rule

- Mark `STOPPED` if the route creates unsupported critical values or unsafe
  approvals at a rate that violates the predeclared evaluation threshold.
- Mark `NOT_SUPPORTED` if it does not show a meaningful quality benefit over
  the guarded approach.
- Keep `PROPOSED` or `IN_PROGRESS` until evidence exists.
- If it shows useful extraction behavior, preserve that evidence as a possible
  component while still evaluating whether deterministic validation is needed.

## Evidence

No model run has been completed at the time of this entry. There is currently
no empirical basis for calling the route failed.

## Next action

Freeze cases, answer key, rubric, and thresholds; then conduct the controlled
comparison and update this log without deleting the pre-test hypothesis.
