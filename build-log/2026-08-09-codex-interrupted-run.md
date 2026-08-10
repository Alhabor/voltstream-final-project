# Corrected Observation: Late Codex Completion and Resume Gap

## What happened

After the live schema repair, run `2026-08-09-final-v3` completed the baseline
and DeepSeek Flash. An early filesystem check during Codex EVG-010 found only
request metadata and no terminal output. A later evidence review showed that
the process had still been finishing: all ten raw responses, parsed outputs,
the strategy predictions file, and the manifest completion timestamp are
present.

The earlier description of v3 as interrupted is therefore retracted. The
process-status check raced the final artifact writes; this is not a model or
provider failure.

## Engineering correction

The race still exposed a real recovery gap: before the change below, a
genuinely interrupted strategy would write its aggregate predictions only
after all ten cases and refuse its existing directory on restart.

The runner now supports explicit `--resume`. It loads completed per-case
`parsed-output.json` files without rewriting them and runs only incomplete
cases. A resumed incomplete case receives `resume.json` audit metadata. A
regression test proves the completed case file is unchanged.

The provider response schema is also added to the manifest's frozen hashes.
Because those changes occurred after v3 began, v3 is retained under the
historically named `evaluation/failed-runs/2026-08-09-codex-interrupted-run/`
and excluded from the final comparison. Its corrected `failure.json` controls
interpretation of the folder name.

