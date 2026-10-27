# Design options (Planning round 1)

Inputs: `pass-evidence.md`, the `review-refactor` playbook on this branch, the review-refactor lessons change on its
unmerged development branch (read with `git show`, not cited by ID), `CAP-DIST-context-and-playbooks` §4 (exact
retrieval resolves body resources against the parent of `source.path`) and the `skill-authoring` playbook. Settled by
`user` and not compared here: a separate playbook, the router structure, the `maintenance` bundle, reuse of
`review-refactor`'s application and differential evidence by reference.

## O1. Entry modes (spike Q1)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Three modes: `survey` (measure and attribute, stop at the decision round), `targeted` (named operations through application), `regression` (one operation slower between two revisions) (chosen) | The pass was `targeted`; a survey is the same procedure stopped early; a regression needs two revisions and bisection, which the other modes lack | Mode table in `SKILL.md`; one extra subsection in `measurement.md` | A survey grows into application without a decision; the round is the only way in |
| B. One mode, always targeted | Simplest | None | A user who wants only a ranked list must name targets first; a regression has no comparison step |
| C. Regression as a bugfix route, not a playbook mode | A regression against a stated budget is a defect | Moves bisection to the feature workflow | Most repositories state no budget, so most regressions would have no route |

## O2. Reuse mechanism for `review-refactor` (spike Q5)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Resolve `devkit playbook get maintenance/review-refactor`, read `references/applying.md` and `references/criteria.md` relative to its `source.path`, cite sections by heading; every preset that deploys `performance-pass` deploys `review-refactor`; a bundle test pins the cited headings (chosen) | Exact retrieval returns the effective entrypoint, overrides included (`CAP-DIST-context-and-playbooks` §4) | One preset constraint, one test | A heading rename in `review-refactor` fails the test, which is the intended signal |
| B. Relative link `../review-refactor/references/applying.md` | Managed layout puts both under `playbooks/` | None | Bypasses a user override of `review-refactor`; breaks silently when it is not deployed |
| C. Copy the shared steps | Self-contained like `review-refactor` | About 4 KB duplicated | Two copies drift; contradicts the settled reuse by reference |

## O3. Report placement

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Report fields in `SKILL.md` (chosen) | Every mode ends with a report; `skill-authoring` keeps every-run instructions in `SKILL.md`; `review-refactor` does the same | About 1.5 KB in `SKILL.md` | None within budget |
| B. `references/report.md` | The draft named it | One more file | A reference every run must read is an every-run instruction outside `SKILL.md` |

## O4. Timing helper script (user question)

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. A standard-library `scripts/compare_runs.py` that runs variants as argument lists, interleaved, with warm-up, checks each run's exit code and output digest and prints median, minimum and range as JSON (recommended) | `skill-authoring` script support: repetitive, deterministic steps become a script; the zsh and interleaving traps are mechanical (`pass-evidence.md` §3); `hyperfine` is not installed on this machine | One script, its tests, a check that directory playbooks deploy it executable | First script in any bundle source; a broken script misleads until fixed |
| B. Procedure only, naming an installed benchmark tool as an example and a hand loop otherwise | No bundle ships a script yet | None | Each run re-creates the loop and can repeat the traps |

## O5. Presets

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. Implicit `all` plus a new preset `performance` with `performance-pass` and `review-refactor`; `upkeep` unchanged (chosen) | O2 A requires co-deployment; `refactoring` is the precedent of a single-purpose preset; `upkeep` holds recurring upkeep, while a pass targets operations the user names | Bundle test, README and recommendation guide | A `performance` user also receives `review-refactor`, which runs only on invocation |
| B. Also add `performance-pass` to `upkeep` | Both are maintenance | Same | Existing `upkeep` projects receive a new playbook on their next sync without asking for it |

## O6. Router size

Budget per file: 12288 bytes (`RULE-skill-document-size`), aim about 9.5 KB (75-80 %). Estimated from the content in
`proposal.md` §3: `SKILL.md` about 8 KB; `measurement.md` about 7 KB; `profiling.md` about 5 KB; `candidates.md` about
7 KB; `applying.md` about 5 KB. `profiling.md` is small but read only by some runs (a survey of a single command whose
measurement already names the cost skips it), so it stays separate instead of joining `measurement.md`.
