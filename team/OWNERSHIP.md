# Team Ownership — Who Did What

VoltStream — Team 4 response to Con Edison's **EV Charger Data** use case,
SHBI-GB 7151 Applied Generative AI in Business.

This record answers the review question "who did what" with attributable
evidence. Every claim below points to a commit or a file in this repository.
Nothing here is fabricated; contributions that are not visible in the
repository are explicitly marked as not present.

Last updated: 2026-08-21 (post-grading review response).

## Team roster

| Team member | GitHub | Role |
|---|---|---|
| Haoyu Zheng (郑皓与) | `Alhabor` | Prototype & evaluation author; trial owner; repository owner |
| Heyang Li (李赫阳) | `Williamli1234` | Team member; independent project review |
| Ray Han | `RayHan0722` | Team member; independent project review |
| Zhuowen Cui (崔卓文) | `Stephcui30` | Team member; independent project review |

**Not on the repository:** Yoon Lee was part of the presenting team but has no
GitHub identity, commits, or review record in this repository; the team does
not claim otherwise.

## Attributable contributions

### Haoyu Zheng (`Alhabor`) — substantive author

All prototype code, tests, experiment harness, evaluation data and scoring,
documentation, presentation, and repository administration were authored and
committed by Haoyu Zheng. Representative evidence:

| Area | Evidence |
|---|---|
| Prototype implementation | `src/voltstream/` (e.g., `gatekeeper.py`, parsers, validators) |
| Software tests | `tests/` (unit, fixture, tamper-oriented tests) |
| Experiment harness | `scripts/run_experiments.py`, `scripts/score_run.py`, `scripts/verify_run.py`, `scripts/validate_fixtures.py` |
| Frozen benchmark & results | `data/`, `evaluation/` (prewritten cases, answer key, runs `2026-08-09-final-v4`) |
| Design & recommendation docs | `docs/PROJECT_SCOPE.md`, `docs/EXPERIMENT_PLAN.md`, `docs/ARCHITECTURE.md`, `docs/FINAL_RECOMMENDATION.md`, `docs/QA_REPORT.md` |
| Solution design document | `../Doc/EV-Charger-Data-Solution-Design_EN.md` and `_CN.md` (outside the code repo, mirrored in submission) |
| Presentation | `presentation/` (slides JSON, evidence renderer, self-contained deck) |
| Research | `research/BACKGROUND_RESEARCH.md`, `research/SOURCES.md` |
| Repo administration | Owner; added all collaborators; merged team PRs (`d02a205`, `d2036c8`, `e225766`, `6b66c45`) |

### Independent project reviews (one attributable commit each)

Each teammate independently reviewed the final recommendation against the
frozen evidence and committed a dated review record. These are genuine,
attributable contributions of independent QA, not fabricated authorship.

| Member | Commit | Review record |
|---|---|---|
| Williamli1234 (李赫阳) | `b58b964` (merged 2026-08-10) | `team/contributions/Williamli1234.md` — ran `make check` (81 tests), `git diff --check`, secret scan on `origin/main`; independently concluded the evidence supports only a limited human-reviewed pilot |
| RayHan0722 (Ray Han) | `a7da807` (merged 2026-08-10) | `team/contributions/rayhan0722.md` — ran `make check` under Python 3.9.5 (pass) and 3.13.3 (documented float ULP variance); verified scores, fixtures, freeze, and secret scan |
| Stephcui30 (崔卓文) | `f06efa4` (merged 2026-08-11) | `team/contributions/Stephcui30.md` — ran `make check` on Python 3.13.0 (fail, documented) and 3.9.6 (pass, 83 tests); verified run integrity and secret scan |

## Trial ownership and go/no-go gate

Per the post-grading review response (professor feedback), the pilot now has a
named owner and a preregistered gate:

- **Trial owner: Haoyu Zheng** — accountable for running the pilot, publishing
  results, convening the gate review, and maintaining the gate record.
- **Decision authority:** Con Edison PowerReady intake program manager
  (hypothetical reviewer in this course).
- **Gate criteria:** `docs/FINAL_RECOMMENDATION.md` §7.1–7.2 and
  `../Doc/EV-Charger-Data-Solution-Design_EN.md` §15.3 (GO / GO WITH
  CONDITIONS / NO-GO; hard safety veto unchanged).

## AI-use disclosure

AI-assisted coding and document drafting agents were used for prototype code,
experiments, documentation, and translation; the LLM APIs evaluated in the
benchmark (Codex `gpt-5.6-terra`, DeepSeek Flash/Pro) are disclosed as
evaluated subjects. Full disclosure, including instances where the team
overrode AI output, is in the solution design document Appendix D and
`docs/QA_REPORT.md`.
