# Build Log

This directory records decisions and evidence throughout development. A failed
or stopped route is graded as process evidence, so logs must preserve what was
tried rather than rewrite history after the result is known.

## Status vocabulary

- `PROPOSED` — planned, no execution evidence yet.
- `IN_PROGRESS` — implementation or evaluation has begun.
- `SUPPORTED` — current evidence supports the stated conclusion.
- `NOT_SUPPORTED` — current evidence does not support the stated conclusion.
- `STOPPED` — work ended for a documented evidence-based reason.
- `BLOCKED` — an external dependency prevents the next test.

Do not label an approach `STOPPED` merely because it sounds unsafe. Record a
test, evidence, and decision whenever feasible.

## File naming

Use `YYYY-MM-DD-short-topic.md`. Add a new entry for each material scope,
architecture, experiment, or stop/continue decision.

## Entry template

```markdown
# <Decision or experiment title>

- Date:
- Owner/agent:
- Status: PROPOSED | IN_PROGRESS | SUPPORTED | NOT_SUPPORTED | STOPPED | BLOCKED
- Related commit(s):
- Related cases/results:

## Question

What uncertainty are we resolving?

## Hypothesis written before the test

What do we expect, and why?

## Method

Inputs, answer key version, strategy/model and exact version, prompt version,
parameters, repetitions, metrics, and commands.

## Evidence

Link raw outputs, scored results, tests, or screenshots. Separate observations
from interpretation. Never include API keys or authorization headers.

## Decision

Continue, revise, stop, or remain undecided. State the threshold or evidence
that drove the decision.

## Limitations and next action

What remains unknown, and what is the smallest next test?
```

## Minimum log evidence for the final presentation

- Initial scope and why the five-layer vision was narrowed.
- One approach that failed or was stopped, with observed evidence.
- One potentially promising approach, with evidence so far.
- Cost-oriented and quality-oriented experiment decisions.
- Final recommendation and the evidence boundary.

