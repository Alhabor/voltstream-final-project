# VoltStream Final Project

VoltStream is Team 4's response to Con Edison's **EV Charger Data** use case for
SHBI-GB 7151 Applied Generative AI in Business.

The repository will contain the research, documentation, tested prototype,
evaluation data and results, build log, and HTML presentation required for the
final project.

## Current prototype boundary

The full five-layer governance pipeline in `../Doc/` is the product vision. The
course prototype should implement and evaluate one defensible slice of that
vision. The current recommended slice is:

> Convert heterogeneous EV-charger submissions into a canonical schema,
> validate every proposed transformation, and escalate uncertainty instead of
> silently inventing data.

This slice is now frozen in `docs/PROJECT_SCOPE.md`. Ten synthetic cases and
their prewritten answer key are versioned before any model evaluation.

## Repository map

- `../Doc/` — supporting English and Chinese solution-design documents kept
  outside this code repository
- `data/` — public-source and synthetic evaluation inputs
- `src/` — prototype implementation
- `tests/` — automated software tests
- `evaluation/` — answer key, model outputs, scoring, and result tables
- `build-log/` — successful and failed approaches with dated evidence
- `presentation/` — final ten-minute HTML presentation
- `research/` — authoritative background sources and evidence boundaries
- `docs/` — prototype scope and architecture
- `scripts/` — reproducible validation, evaluation, and security commands

See [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) for the submission
contract distilled from the assignment page.

## Repository status

The private GitHub remote is configured at
`Alhabor/voltstream-final-project`, and the complete v4 experiment plus final
HTML presentation are versioned on `main`. GitHub collaborator membership and
one attributable commit per human team member must still be verified by the
team before submission; the repository does not fabricate that evidence.

## Local validation

The deterministic prototype uses Python 3.9+ and has no runtime dependencies.

```bash
make check
```

This runs unit tests, benchmark-contract validation, a read-only end-to-end
integrity audit of the final experiment bundle, bytecode compilation, and the
repository secret scan. API keys are read from local environment variables
only; see `SECURITY.md` and `.env.example`.

## Reproduce the evidence

Run the deterministic baseline or a registered model strategy:

```bash
PYTHONPATH=src python3 scripts/run_experiments.py \
  --run-id <new-run-id> --strategy baseline

# Model strategies require their normal local provider authentication.
PYTHONPATH=src python3 scripts/run_experiments.py \
  --run-id <new-run-id> --strategy codex-terra-guarded
```

Score a completed run without sending data to a provider:

```bash
python3 scripts/score_run.py --run-id <run-id>
```

Verify the frozen files, per-case evidence, aggregate predictions, and saved
scores of a completed run without rewriting it:

```bash
PYTHONPATH=src python3 scripts/verify_run.py --run-id <run-id>
```

The audited final evidence is in `evaluation/runs/2026-08-09-final-v4/`.
Open `presentation/index.html` directly; it is self-contained, includes
English/Chinese and dark/light switching, and requires no server, network
request, or sibling data file.
