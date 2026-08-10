# Failed Run: JSON Mistaken for an Unresolved Template

## What was attempted

After phase 2 passed 54 local tests, run `2026-08-09-final-v1` completed the
deterministic baseline and began the guarded DeepSeek Flash strategy. EVG-001
and EVG-002 returned and were persisted normally. The runner stopped before
sending EVG-003.

## Evidence and root cause

`render_case_prompt` rejected any rendered text containing `}}`. Nested JSON
naturally ends with adjacent closing braces, so EVG-003 triggered the guard even
though all five known template variables had been resolved. The unit test used
a plain-text payload and did not cover nested JSON syntax.

The partial artifacts, manifest, and sanitized failure record are retained in
`evaluation/failed-runs/2026-08-09-runner-template-failure/`. They are excluded
from final scoring.

## Correction and restart rule

The guard now searches only for unresolved names from the fixed template
vocabulary. A nested-JSON regression test was added. Because the code changed
after the original manifest was created, the run is not resumed: all strategies
will restart under a new run ID tied to the corrective commit.

No credential, authorization header, or environment-file content was written
to the preserved evidence.

