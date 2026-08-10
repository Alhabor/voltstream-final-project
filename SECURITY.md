# Security and Data Boundary

## Secrets

- API keys must be supplied through environment variables.
- `.env` and `.env.*` are ignored; `.env.example` contains placeholders only.
- Never place credentials in source code, prompts committed to the repository,
  fixtures, screenshots, model outputs, build logs, or GitHub Actions settings.
- Run `python3 scripts/scan_secrets.py --staged` before every commit.
- If a credential is printed, committed, or shared outside the intended local
  environment, revoke and replace it.

## Data

The prototype uses public-source metadata and explicitly labeled synthetic
contractor submissions. It must not ingest or imply access to Con Edison
internal data, customer data, or production infrastructure.

## Model boundary

The model receives one synthetic evaluation case at a time. It may extract
values and recommend a routing decision, but it cannot write to a production
database, contact a contractor, approve a regulatory submission, or silently
replace the original input.

