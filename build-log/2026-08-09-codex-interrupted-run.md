# Interrupted Run: Missing Case-Level Resume

## What happened

After the live schema repair, run `2026-08-09-final-v3` completed the baseline,
DeepSeek Flash, and nine valid Codex Terra responses. The outer experiment
process ended during EVG-010 without a Python traceback. EVG-010 contains only
request metadata; no model response or parsed prediction was recorded.

The exact external termination cause is unavailable, so it is not attributed
to the model. The actionable engineering failure is clear: the runner wrote
the strategy-level predictions file only after all ten cases and refused an
existing strategy directory, despite its documentation claiming recovery.

## Correction

The runner now supports explicit `--resume`. It loads completed per-case
`parsed-output.json` files without rewriting them and runs only incomplete
cases. A resumed incomplete case receives `resume.json` audit metadata. A
regression test proves the completed case file is unchanged.

The provider response schema is also added to the manifest's frozen hashes.
Because this changes the runner after v3 began, v3 is retained under
`evaluation/failed-runs/2026-08-09-codex-interrupted-run/` and is not used in
the final comparison.

