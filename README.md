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

The exact slice and evaluation design must be confirmed by the team before
implementation.

## Repository map

- `../Doc/` — supporting English and Chinese solution-design documents kept
  outside this code repository
- `data/` — public-source and synthetic evaluation inputs
- `src/` — prototype implementation
- `tests/` — automated software tests
- `evaluation/` — answer key, model outputs, scoring, and result tables
- `build-log/` — successful and failed approaches with dated evidence
- `presentation/` — final ten-minute HTML presentation

See [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) for the submission
contract distilled from the assignment page.

## Repository status

The directory is initialized as a local Git repository. A GitHub remote,
collaborators, model credentials, and team-member contribution assignments have
not yet been configured.
