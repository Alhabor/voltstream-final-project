# Ten-Minute Speaker Notes

## 0:00–0:45 — Decision first

VoltStream is an intake gate, not a complete data platform. Lead with the
recommendation: one guarded Codex configuration earned another limited,
human-reviewed test; no system earned production or autonomous-write approval.

## 0:45–1:35 — Problem selected

Explain why intake is the defensible slice. Contractor data can arrive in CSV,
JSON, or prose, and uncertainty is cheapest to stop before it reaches a system
of record. Do not claim Con Edison internal error rates or labor savings.

## 1:35–2:15 — Research surprise

DOE AFDC itself combines daily network APIs, periodic spreadsheet/CSV imports,
and manual records. Heterogeneity is not an edge case; provenance and explicit
unknowns therefore matter as much as completeness.

## 2:15–3:10 — Prototype and ideation

Walk through: input → eight-field candidate → source mappings → deterministic
validation → ACCEPT/HUMAN_REVIEW/REJECT. The model proposes; ordinary code
routes. Mention the alternatives deliberately excluded: OCR, live portals,
master-data reconciliation, anomaly diagnosis, production writes.

## 3:10–4:45 — What failed

Use EVG-009. The payload has `installed_ports=8` and `active_ports=6`, while the
canonical schema has only `port_count`. The safe answer is null plus review.
All four DeepSeek-based paths chose 8 and ACCEPTed, so one rare case vetoed
automation despite 95%+ overall field accuracy. Also briefly mention the two
retained runner failures and the corrected v3 status race as evidence of an
honest build process.

## 4:45–5:35 — Future signal

DeepSeek Pro reached 96.4% mapping accuracy but did not solve safety. Codex's
miss was conservative text-lineage extraction, a narrower and testable repair.
That is why Codex is promising and Pro is only a future signal.

## 5:35–7:35 — Testing and results

Ten fixed synthetic cases, answer key written first, same contract and rubric.
Keep metrics separate. Codex: 78/80 values, 56/56 structured mappings, 8/8
issue recall, 9/10 routes, zero unsafe under-routes, zero unsupported values.
The baseline was safe but incomplete. The cascade saved only one call and kept
the safety failure; Pro cost about 3.15× Flash without passing the gate.

## 7:35–8:50 — Recommendation

Continue an offline, fully human-reviewed pilot: approved data only, original
payload and provenance retained, no authoritative writes, zero tolerance for
unsupported critical values or unsafe under-routing. Add raw-payload ambiguity
rules and text-lineage extraction before expanding the benchmark.

## 8:50–10:00 — Risks and close

Ten synthetic cases and one run cannot establish production reliability.
Mention model drift, automation bias, privacy, false rejection, price/latency
uncertainty, and schema limits. Close with: evidence supports learning safely,
not automating yet.
