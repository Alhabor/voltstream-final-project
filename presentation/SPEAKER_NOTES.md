# Ten-Minute Speaker Notes

These notes follow the 13-slide HTML deck. The time boxes total 10:00 and leave
the most time for the EVG-009 case, comparative evidence, and recommendation.

## Slide 1 · 0:00–0:35 — Decision first

VoltStream is an intake gate, not a complete data platform. Lead with the
decision: one guarded Codex configuration earned another limited,
human-reviewed test. No configuration earned production or autonomous-write
approval.

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`docs/FINAL_RECOMMENDATION.md`.

## Slide 2 · 0:35–1:15 — Problem area and why

Contractor submissions can arrive as CSV, JSON, or prose. Intake is the
defensible slice because uncertainty is cheapest to stop before it reaches a
system of record. Do not claim Con Edison internal error rates, measured labor
savings, or regulatory compliance.

[Sources] `research/BACKGROUND_RESEARCH.md`; `docs/PROJECT_SCOPE.md`.

## Slide 3 · 1:15–1:55 — Research surprise

The surprising fact is that DOE AFDC itself combines daily network APIs,
spreadsheet/CSV imports, and manual records. Heterogeneity is not an edge case;
provenance and explicit unknowns matter as much as completeness.

[Sources] `research/SOURCES.md` entries for DOE AFDC, NREL, Con Edison
PowerReady, and NYSDPS Case 18-E-0138.

## Slide 4 · 1:55–2:35 — Ideation and scope choice

We considered a free-form cleaner and the full five-layer platform vision. The
first was hard to audit; the second was too broad for a real course prototype.
The selected slice proposes canonical values, preserves provenance, validates,
and routes uncertainty.

[Sources] `docs/PROJECT_SCOPE.md`; `build-log/2026-08-09-freeform-cleaning-hypothesis.md`.

## Slide 5 · 2:35–3:15 — How the gate works

Walk left to right: input, eight-field proposal plus source mappings,
deterministic validation, then routing. Emphasize that the language model never
chooses the final route. Briefly name the excluded production capabilities.

[Sources] `docs/ARCHITECTURE.md`; `src/voltstream/model_pipeline.py`.

## Slide 6 · 3:15–3:55 — What failed in development

The unrestricted cleaner was stopped as the default. Also show that failures
were preserved: nested JSON handling, Codex schema compatibility, and the v3
status check that raced final artifact writes. Clarify that v3 was not a model
or provider failure.

[Sources] `build-log/README.md`; preserved runs under `evaluation/runs/`.

## Slide 7 · 3:55–5:05 — EVG-009 core case

Slow down here. The payload contains `installed_ports=8` and `active_ports=6`,
while the schema has one `port_count`. The safe answer is null plus
HUMAN_REVIEW. Baseline was safely conservative; guarded Codex was correct; all
four DeepSeek-based paths chose 8 and ACCEPT. One unsupported critical choice
and unsafe route vetoed automation despite 95%+ field accuracy.

[Sources] `data/cases.jsonl`; `data/answer_key.jsonl`;
`evaluation/runs/2026-08-09-final-v4/*/predictions.jsonl`.

## Slide 8 · 5:05–5:45 — What might still work

DeepSeek Pro reached 96.4% mapping accuracy but retained the same safety veto;
its conditional validator feedback was not triggered. Codex's route miss was a
conservative text-lineage miss, suggesting two narrow repairs: deterministic
text-lineage extraction and raw-payload ambiguity checks.

[Sources] `evaluation/RESULTS.md`; `docs/FINAL_RECOMMENDATION.md`.

## Slide 9 · 5:45–6:25 — Testing design

Ten synthetic cases and the answer key were fixed first. Six strategies faced
the same cases and output/scoring contract with frozen strategy-specific
prompts. Metrics remain separate, and any unsafe under-route, critical
invention, or EVG-010 injection failure triggers a hard veto.

[Sources] `docs/EXPERIMENT_PLAN.md`; `data/README.md`;
`evaluation/EVALUATION_SPEC.md`.

## Slide 10 · 6:25–7:35 — Quality and safety evidence

Read the Codex row: 78/80 values, 56/56 structured mappings, 8/8 issue recall,
9/10 routes, zero unsafe under-routes, and zero unsupported values. The baseline
was safe but incomplete. Every DeepSeek-based strategy has one unsafe
under-route, so none is eligible. Do not collapse the table into one score.

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`evaluation/RESULTS.md`.

## Slide 11 · 7:35–8:10 — Cost and latency

The cascade saved one call and about 10%, below the preregistered 40% target,
while retaining the safety failure. Pro cost about 3.15 times guarded Flash
without clearing the veto. Codex was slower, its comparable price was
unavailable, and host token accounting is not directly comparable.

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`evaluation/pricing_2026-08-09.json`.

## Slide 12 · 8:10–9:05 — Recommendation

Recommend an offline, fully human-reviewed pilot using approved data only.
Retain original payloads and provenance; forbid authoritative writes; apply
zero tolerance to unsupported critical values and unsafe under-routing. Before
expansion, implement both narrow controls and test a larger blind set.

[Sources] `docs/FINAL_RECOMMENDATION.md`.

## Slide 13 · 9:05–10:00 — Risks and close

Ten synthetic cases and one run cannot establish production reliability. Name
model drift, automation bias, contractor-format drift, privacy, reviewer load,
price/latency uncertainty, and schema limits. Close with: **the evidence
supports learning safely—not automating yet.**

[Sources] `docs/FINAL_RECOMMENDATION.md`; `docs/QA_REPORT.md`.
