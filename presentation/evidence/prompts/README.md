# Versioned Experiment Prompts

- `guarded_system_v1.md`: evidence-first extraction used by guarded model
  strategies.
- `unrestricted_cleaner_system_v1.md`: deliberately permissive comparator for
  the preregistered failure hypothesis; synthetic evaluation only.
- `case_user_template_v1.md`: identical case envelope supplied to each model.
- `validator_feedback_v1.md`: one allowed correction turn for the quality
  strategy; it must contain validator findings, never answer-key content.

Prompt files are experimental inputs. Record their SHA-256 hashes in every run
manifest and do not edit a version after observing model results. Create a new
version instead. Never include an API key in a prompt or saved request.

