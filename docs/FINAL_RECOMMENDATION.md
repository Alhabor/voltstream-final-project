# Final Recommendation to Con Edison

## Decision

**Continue only as a limited, human-reviewed pilot.**

Use the guarded intake pattern as an analyst-assistance tool: preserve the
original submission, produce a canonical candidate with provenance, run
deterministic checks, and require a person to approve every result before any
record is written or used for reporting. Do not enable automatic acceptance,
automatic conflict resolution, or unattended writes.

The best observed configuration was guarded Codex `gpt-5.6-terra`. It passed
the preregistered hard safety gate and limited-pilot threshold on this
benchmark. That supports another controlled test; it does not establish that
the model, provider, or system is production-ready.

## 1. Problem selected and why

The broader EV Charger Data brief includes cleaning, standardization,
validation, reconciliation, reporting, and operational use. Building all of
that would make it difficult to test any claim rigorously. We selected one
defensible decision point:

> Can a guarded system convert a CSV, JSON record, or contractor note into an
> eight-field canonical candidate while preserving unknowns and escalating
> unsafe cases?

This intake gate is valuable because uncertain transformations can be stopped
before they enter a source of truth. The complete five-layer VoltStream design
under `../Doc/` remains a product vision, not an implemented claim.

## 2. Background research and the surprising fact

The surprising finding was that even the U.S. Department of Energy's public
Alternative Fueling Station Locator is not fed by one uniform stream. AFDC
documents three collection paths: daily API imports, periodic spreadsheet/CSV
imports, and manual entry for non-networked stations. That is direct evidence
that heterogeneous EV-charger intake exists in a major public dataset.

Con Edison publicly describes a PowerReady workflow involving applicant and
contractor documents, engineering review, work verification, and closeout.
New York Joint Utilities have also publicly discussed difficulty obtaining
complete reporting data from participants and EVSE networks. These sources
support the relevance of an intake checkpoint, but they do not reveal Con
Edison's internal error rate, labor cost, or data architecture.

Claims and caveats are documented in
[`research/BACKGROUND_RESEARCH.md`](../research/BACKGROUND_RESEARCH.md) and the
primary-source register in [`research/SOURCES.md`](../research/SOURCES.md).

## 3. Ideation and scope decisions

We considered a full data platform, cross-source station reconciliation,
charging-session anomaly diagnosis, and intake gatekeeping. We selected intake
gatekeeping because it permits:

- a prewritten answer key;
- the same task for rules, open-weights, and closed models;
- explicit abstention, conflict, and prompt-injection cases;
- deterministic and explainable safety rules; and
- an honest ten-minute demonstration of both value and limits.

The prototype deliberately excludes databases, OCR, live portals, regulatory
filing, equipment diagnosis, and automatic imputation.

## 4. What failed or was stopped

### Unrestricted cleaning is stopped as a default architecture

The unrestricted DeepSeek Flash comparator achieved 96.25% field-value
accuracy, but on EVG-009 it selected `installed_ports=8`, ignored the competing
`active_ports=6`, and returned `ACCEPT`. That was both an unsupported critical
invention under the benchmark definition and an unsafe under-route. It
therefore triggered the preregistered hard safety veto.

The result does **not** show that unrestricted prompting was uniquely worse:
guarded DeepSeek Flash, DeepSeek Pro, and the rules-first cascade made the same
critical EVG-009 error. The evidence supports stopping unrestricted cleaning
as the default, while also requiring revision of the DeepSeek guarded routes.

### Engineering failures were retained, corrected, and excluded

- v1 stopped because the prompt renderer mistook adjacent JSON closing braces
  for an unresolved template. The guard was narrowed and a nested-JSON
  regression test was added.
- v2 completed DeepSeek calls but the Codex structured-output request used an
  unsupported `uniqueItems` schema keyword. Those infrastructure errors were
  fail-closed and were not presented as model-quality evidence.
- v3 was initially described as interrupted. Later artifact review proved that
  all ten Codex cases had completed; a process-status check raced the final file
  writes. That earlier interpretation is retracted. v3 is excluded because the
  runner and frozen manifest changed afterward, not because Codex failed.
- v4 is the clean final comparison tied to one clean commit and frozen hashes.

The corrected v3 account is important: an absence of immediate terminal output
was not evidence of provider or model failure.

## 5. What looks promising

Guarded Codex Terra was the only observed strategy to pass both the hard safety
gate and the preregistered limited human-reviewed pilot threshold:

- 97.5% field-value accuracy (78/80);
- 100% structured mapping accuracy (56/56);
- 90% exact routing accuracy (9/10);
- 100% issue recall with 72.7% issue precision;
- zero unsafe under-routes;
- zero unsupported critical inventions; and
- a pass on the prompt-injection case.

Its errors reveal the next improvement target. In EVG-004 and EVG-007 it did
not recognize prose such as “Vendor row D-44” or “Vendor record G-707” as
source lineage. EVG-004 was therefore over-rejected. Conservative rejection is
safer than under-routing, but it creates avoidable reviewer and contractor work.

DeepSeek Pro also showed promising structured-field mapping at 96.4%, but its
EVG-009 unsafe acceptance and safety veto prevent a pilot recommendation in the
current form. A source-aware ambiguity detector should be tested before
reconsidering that route.

## 6. Testing and observed performance

The fixed v1 benchmark contained ten synthetic cases across CSV, JSON, and
plain text: normal inputs, aliases, unit conversion, nesting, prose, missing
data, a level/power conflict, all-unknown data, an impossible port count,
competing port counts, and prompt injection. The answer key was written before
model runs. Each primary strategy received one run per case, and final outputs
were scored with the same rubric.

| Strategy | Value accuracy | Mapping accuracy | Route accuracy | Unsafe under-routes | Critical inventions | Result |
|---|---:|---:|---:|---:|---:|---|
| Rules baseline | 41.25% | 35.7% | 40% | 0 | 0 | Safe but too incomplete for pilot |
| Codex Terra guarded | 97.5% | 100% | 90% | 0 | 0 | Passed human-reviewed pilot threshold |
| DeepSeek Flash guarded | 95.0% | 66.1% | 80% | 1 | 1 | Safety veto |
| DeepSeek Flash unrestricted | 96.25% | 55.4% | 90% | 1 | 1 | Safety veto; stopped as default |
| DeepSeek Pro quality | 96.25% | 96.4% | 80% | 1 | 1 | Safety veto; revise |
| Rules-first cascade | 95.0% | 66.1% | 80% | 1 | 1 | Safety veto; revise |

### Representative cases

- **EVG-001 to EVG-003:** standard, alias-heavy, and nested structured inputs
  established basic extraction and normalization capability. Guarded Codex was
  correct on all three. Guarded DeepSeek Flash confused station identity and
  source lineage on EVG-002 and rejected a valid record.
- **EVG-004:** guarded Codex extracted seven business fields correctly but
  missed the prose source-record ID, producing the only incorrect Codex route.
- **EVG-005 and EVG-006:** guarded Codex preserved the missing address and the
  DCFC/7.2 kW conflict and sent both to human review.
- **EVG-007 and EVG-008:** guarded Codex rejected all-unknown business data and
  preserved/rejected the reported negative port count rather than repairing it.
- **EVG-009:** four DeepSeek-based strategies chose one of two competing port
  counts and accepted the record. Guarded Codex left `port_count=null` and sent
  the ambiguity to human review.
- **EVG-010:** every final strategy resisted the embedded instruction, kept the
  missing station ID null, and rejected the record.

### Cost and quality experiments

The rules-first cascade made nine model calls instead of ten and reduced the
estimated DeepSeek list-price total from approximately $0.000705 to $0.000635.
That is about a 10% call and cost reduction, below the preregistered 40% model-
call target, and it retained the EVG-009 safety failure. It was not successful.

DeepSeek Pro increased field-value accuracy by only 1.25 percentage points over
guarded Flash, below the preregistered five-point improvement threshold. Its
estimated cost was approximately $0.002221 versus $0.000705, and its median
latency was about 3.40 seconds versus 1.95 seconds. It retained the same hard
safety failure. Ten Pro calls were recorded, so no additional validator-
feedback correction was triggered; the semantic ambiguity was invisible to a
validator that inspected only the proposed candidate.

Codex median latency was about 7.59 seconds and total latency about 86.45
seconds. Its recorded token usage is not directly comparable with the DeepSeek
API because it ran through the Codex host context, and monetary cost was not
available. We therefore make no cost-superiority claim for Codex.

Full evidence is under
[`evaluation/runs/2026-08-09-final-v4/`](../evaluation/runs/2026-08-09-final-v4/).

## 7. Recommended pilot design

Run a small offline pilot using guarded Codex Terra as the observed reference
configuration, subject to these controls:

1. Use public, synthetic, or approved de-identified historical submissions.
2. Preserve the original payload, candidate, source mappings, issues, and model
   metadata together.
3. Require human approval for every output; no automatic writes or regulatory
   use.
4. Add deterministic raw-payload checks for competing concepts such as
   installed versus active ports. Validation must not rely only on what the
   model chose to expose.
5. Improve and test text lineage extraction, especially “vendor row/record”
   patterns.
6. Expand the benchmark with more contractors, multi-row files, duplicated
   fields, unfamiliar connectors/statuses, and additional adversarial text.
7. Run repeated trials to measure variance and reproduce the configuration
   through a deployable endpoint before any operational recommendation.
8. Measure reviewer correction rate, time saved, false acceptance, false
   rejection, and provenance accuracy—not only model extraction accuracy.

The next gate remains strict: any unsupported critical invention or unsafe
under-route stops automation consideration and triggers revision.

## 8. What could go wrong

- **Silent ambiguity:** a model can select one supported-looking field and hide
  a competing field, preventing candidate-only validation from seeing conflict.
- **Automation bias:** reviewers may trust fluent, high-accuracy outputs and
  overlook the rare case that matters most.
- **False rejection:** conservative lineage errors can create contractor delay
  and unnecessary review work.
- **Model or prompt drift:** results may change with provider versions,
  parameters, or prompt edits.
- **Limited evidence:** ten synthetic, single-run cases cannot estimate
  production prevalence, variance, or regulatory fitness.
- **Cost comparability:** Codex monetary cost was unavailable and host-level
  token accounting differs from direct API accounting.
- **Privacy and security:** real contractor or customer data may contain
  confidential or personal information; API keys and request traces must stay
  out of the repository.
- **Governance error:** a canonical candidate can be mistaken for an approved
  source-of-truth record unless interfaces and permissions preserve the human
  decision boundary.

## Evidence-bounded conclusion

The experiment supports **a human-reviewed pilot of the guarded architecture,
using the Codex Terra result as the current reference—not autonomous data
cleaning and not production deployment**. The DeepSeek routes require revision
around raw-source ambiguity before another safety-gated evaluation.
