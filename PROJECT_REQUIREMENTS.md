# Final Project Requirements

This checklist is distilled from the Capstone assignment page. It should be
treated as the repository's working submission contract.

## Product and scope

- [ ] Address Con Edison's EV Charger Data problem area.
- [ ] Build a generative-AI agent system that supports one specific,
      defensible part of the business decision or workflow.
- [ ] Keep the prototype real, tested, and honest about what it can and cannot
      do; the complete enterprise system is not required.
- [ ] Begin with public or synthetic data and respect data/privacy boundaries.

## Evaluation evidence

- [ ] Define a fixed set of representative cases and write the answer key
      before running the models.
- [ ] Include normal, hard, missing-data, and abstention cases.
- [ ] Run a simple baseline on the same cases.
- [ ] Run at least one open-weights model and one closed model on the same
      inputs and task.
- [ ] Judge all outputs using the same rubric.
- [ ] Include one evaluation aimed at reducing cost and one aimed at improving
      quality relative to the baseline.
- [ ] Report errors by category, not only as a single aggregate score.
- [ ] Report latency and/or cost where useful.
- [ ] Use metrics the team can explain clearly during the presentation.

## Process evidence

- [ ] Maintain a build log showing what the team tried.
- [ ] Document at least one failed or stopped approach: what was attempted,
      what the evidence showed, and why it was stopped.
- [ ] Document at least one potentially promising approach and the evidence so
      far.
- [ ] Preserve prompts, model/version information, raw outputs, scoring code,
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

- [ ] Background research and sources
- [ ] Product and technical documentation
- [ ] Runnable prototype
- [ ] Public/synthetic input data and answer key
- [ ] Baseline and multi-model raw outputs
- [ ] Evaluation code and results
- [ ] Build log, including failed and promising approaches
- [ ] HTML presentation page
- [ ] Reproduction instructions and dependency manifest

## Final recommendation boundary

The recommendation must follow the evidence and explicitly choose one of these
positions:

- continue a limited test;
- revise the system;
- stop the system; or
- leave the decision human-led.

Do not recommend deployment beyond what the evaluation supports.
