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

The directory is initialized as a local Git repository. A GitHub remote,
collaborators, model credentials, and team-member contribution assignments have
not yet been configured.

## Local validation

The deterministic prototype uses Python 3.9+ and has no runtime dependencies.

```bash
make check
```

This runs unit tests, benchmark-contract validation, bytecode compilation, and
the repository secret scan. API keys are read from local environment variables
only; see `SECURITY.md` and `.env.example`.
