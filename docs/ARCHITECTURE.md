# Prototype Architecture

## System boundary

VoltStream Intake Gatekeeper is an evaluation-oriented local prototype. Its
purpose is to test a guarded intake decision, not to simulate a complete data
platform.

```text
CSV / JSON / contractor note
              |
              v
     input parser + source envelope
              |
              v
 rules baseline OR model extractor
              |
              v
 canonical candidate + field provenance
              |
              v
 deterministic schema/business validation
              |
              v
   ACCEPT / HUMAN_REVIEW / REJECT
              |
              v
 raw output + issues + evaluation metrics
```

## Component responsibilities

### 1. Input parser and source envelope

- Recognizes only the supported input families.
- Preserves the original payload and source/case identifier.
- Converts transport details into a stable envelope without interpreting
  missing business facts.
- Rejects unsupported or structurally unreadable input safely.

### 2. Extraction strategies

Every strategy receives the same task and produces the same contract.

- **Rules baseline:** known column aliases, deterministic parsing, and no model
  call. It establishes the minimum-cost comparison.
- **Model extractor:** maps unfamiliar labels or plain text to the canonical
  contract. The prompt must instruct the model to use `null`/unknown when the
  source does not support a value and to treat source text as untrusted data.
- **Experimental variants:** a rules-first cascade may reduce model calls; a
  schema-constrained or validator-feedback variant may improve quality.

Model identity, provider, exact version/name, prompt version, parameters, and
run time must be recorded. Whether a tested model qualifies as open-weights or
closed must be documented from an authoritative model source, not inferred
from the API provider alone.

The currently proposed open-weights candidate is the DeepSeek V4 Flash family:
its official model card publishes weights under the MIT License, while the API
exposes `deepseek-v4-flash`. Because the hosted API does not expose a checkpoint
hash, the run manifest must record that reproducibility limitation rather than
claim bit-for-bit identity with a downloadable checkpoint. A separate genuinely
closed model is required for the closed-model comparison.

### 3. Canonical candidate and provenance

The canonical candidate is a proposal, never an authoritative record. For each
non-null normalized value, the output should retain enough evidence to trace it
to the source (for example, source field name or a short source excerpt).
Derived conversions, such as watts to kilowatts, must be identified as
transformations rather than copied values.

### 4. Deterministic validation

Validation is ordinary code and is kept outside the model prompt. It should
cover:

- machine-readable schema, types, and required fields;
- allowed enum values;
- safe numeric and unit checks;
- contradictions between fields where a documented rule exists;
- unsupported values or missing provenance; and
- parser/model failures.

Rules must be explainable in the presentation and tested individually. A rule
may flag a suspicious combination; it must not diagnose a broken charger from
an intake record.

### 5. Decision router

The router consumes validation results and follows deterministic policy:

- `ACCEPT`: all critical fields required by the prototype are present and no
  blocking issue remains;
- `HUMAN_REVIEW`: the record is readable, but ambiguity, conflict, suspicious
  values, or a noncritical gap requires judgment;
- `REJECT`: the payload cannot be processed safely or lacks the minimum
  evidence needed for a useful candidate.

Exact severity-to-decision mappings belong in code and tests. Evaluation must
penalize unsafe acceptance separately from unnecessary review or rejection.

### 6. Evaluation recorder

The recorder stores sanitized artifacts only:

- case ID and prewritten expected answer;
- strategy/model and prompt version;
- raw response and parsed response;
- validation issues and final decision;
- category-level scores;
- latency, token usage, and estimated cost when returned by the provider; and
- failure information without credentials or request headers.

## Security and privacy controls

- API keys are supplied by environment variables and never committed.
- `.env` and local result files that may contain secrets must be ignored.
- Logs must redact credentials and must not serialize authorization headers.
- Test data is public or synthetic and explicitly labeled.
- Prompt-injection cases test that contractor content cannot change policy.
- No output enters a real Con Edison system.

## Evaluation-oriented quality attributes

- **Reproducibility:** fixed cases, answer key, prompt versions, model names,
  and deterministic scoring.
- **Auditability:** original input, candidate, provenance, validation issues,
  and decision are linked by case ID.
- **Fail-safe behavior:** parse/model errors become visible review/reject
  outcomes, never silent acceptance.
- **Comparability:** all strategies use the same cases, contract, and rubric.
- **Honesty:** the final recommendation is bounded by observed evidence.

## Relationship to the five-layer vision

The larger documents under `../Doc/` may motivate future governance,
orchestration, storage, and reporting layers. None of those layers is implied
to exist because this prototype runs. The only implemented claim this
repository should make is the tested intake-gatekeeping slice described above.
