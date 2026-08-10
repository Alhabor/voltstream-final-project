# Final Project Requirements

This checklist is distilled from the Capstone assignment page. It should be
treated as the repository's working submission contract.

## Product and scope

- [x] Address Con Edison's EV Charger Data problem area.
- [x] Build a generative-AI agent system that supports one specific,
      defensible part of the business decision or workflow.
- [x] Keep the prototype real, tested, and honest about what it can and cannot
      do; the complete enterprise system is not required.
- [x] Begin with public or synthetic data and respect data/privacy boundaries.

## Evaluation evidence

- [x] Define a fixed set of representative cases and write the answer key
      before running the models.
- [x] Include normal, hard, missing-data, and abstention cases.
- [x] Run a simple baseline on the same cases.
- [x] Run at least one open-weights model and one closed model on the same
      inputs and task.
- [x] Judge all outputs using the same rubric.
- [x] Include one evaluation aimed at reducing cost and one aimed at improving
      quality relative to the baseline.
- [x] Report errors by category, not only as a single aggregate score.
- [x] Report latency and/or cost where useful.
- [x] Use metrics the team can explain clearly during the presentation.

## Process evidence

- [x] Maintain a build log showing what the team tried.
- [x] Document at least one failed or stopped approach: what was attempted,
      what the evidence showed, and why it was stopped.
- [x] Document at least one potentially promising approach and the evidence so
      far.
- [x] Preserve prompts, model/version information, raw outputs, scoring code,
      and reproducible run instructions.
- [ ] Add every team member as a GitHub collaborator.
- [ ] Ensure every team member's agent makes a traceable commit.

## Ten-minute HTML presentation

The presentation must be committed to this repository as an HTML page and
cover, in the following order:

1. Problem area selected and why
2. Background research, including one surprising fact
3. Ideation process
4. What failed
5. What did not work but might indicate a future solution
6. Testing approach and case-by-case evidence
7. Recommendation to Con Edison
8. What could go wrong

## Final repository contents

- [x] Background research and sources
- [x] Product and technical documentation
- [x] Runnable prototype
- [x] Public/synthetic input data and answer key
- [x] Baseline and multi-model raw outputs
- [x] Evaluation code and results
- [x] Build log, including failed and promising approaches
- [x] HTML presentation page
- [x] Reproduction instructions and dependency manifest

## Final recommendation boundary

The recommendation must follow the evidence and explicitly choose one of these
positions:

- continue a limited test;
- revise the system;
- stop the system; or
- leave the decision human-led.

Do not recommend deployment beyond what the evaluation supports.
