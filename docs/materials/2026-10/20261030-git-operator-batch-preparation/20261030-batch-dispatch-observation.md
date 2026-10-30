---
id: MAT-git-operator-batch-dispatch-observation
title: Six-item git-operator preparation dispatch in devkit
summary: "Record one Host-reported dispatch of six prepare-worktree jobs to one git-operator in devkit, its serial per-item results and the prepare-worktree outcome classes a batch must keep apart, without claiming a cost or latency benefit."
created_at: 2026-10-30
---

# [MAT-git-operator-batch-dispatch-observation] Six-item git-operator preparation dispatch in devkit

## Evidence boundary

Repository: devkit, base `main` at `fdba6646` (the six `MS-git-operator-lifecycle-refinement` children after their
plan-intent records). The Host reported this observation to the Planning worker of
`SPEC-git-operator-batch-preparation`. The worker did not see the operator's transcript; it checked the resulting
worktree it runs in (`plan-git-operator-batch-preparation`, created from `fdba6646`, with its environment and managed
files present).

## Observed dispatch

| Observation | Actual result | Limit or interpretation |
| --- | --- | --- |
| Dispatch shape | One Host message to one `git-operator` listed six `prepare-worktree` jobs, each with the role contract's full job fields. | The role contract still says "one exact lifecycle job"; the list was an ad hoc composition, as in `MAT-git-operator-consumer-pilot`. |
| Execution order | The operator ran the six jobs one after another and returned one reply holding a result per job. | No concurrent `devkit worktree start` ran; serial execution avoided shared `.git/config` marker writes at the same moment. |
| Outcomes | All six completed: `devkit worktree start <branch>` plus the configured `[worktree] setup` (`just init`) and locked sync, in about 50 seconds in total. | No denied, refused or partial item occurred, so partial-batch behavior remains unexercised here too. |
| Earlier baseline | Earlier lifecycle jobs in this repository used one job per dispatch through operator continuation. | No matched token, cost or latency comparison was taken between the two forms. |

## Prepare-worktree outcome classes

From `CAP-WT-task-worktrees` §2 and `devkit_agt.features.worktree.usecases.lifecycle`, one `devkit worktree start`
item can end in five classes a batch result must keep apart:

| Class | Example codes | CLI exit | Resource left | Remainder |
| --- | --- | --- | --- | --- |
| Refused before creation | `WORKTREE_BRANCH_EXISTS`, `WORKTREE_CONFLICT`, `WORKTREE_NESTED` | non-zero | none | Host decision (for example continue with `--existing-branch`); nothing to retry blindly. |
| Creation failed and rolled back | `WORKTREE_ADD_FAILED` | non-zero | none, or the listed `left:` details | Inspect `left:`; a rerun starts afresh. |
| Created, then failed before setup | `WORKTREE_LOCAL_CONFIG_COPY_FAILED` (an error) | non-zero | the worktree, without setup or sync | A deliberate manual copy, then setup; Host decision. |
| Created with a setup warning | `WORKTREE_SETUP_FAILED`, `WORKTREE_SYNC_FAILED` | `0` (warning) | the worktree | The warning's `[FIX]`; a plain rerun of `start` is `WORKTREE_BRANCH_EXISTS`, and `--existing-branch` reuse runs neither setup nor sync. |
| Not dispatched | host approval denied or unavailable | null | none | Host decision; never rerouted. |

The setup-warning class is the zero-exit partial item: the CLI succeeded, but worker input is not ready.
Other zero-exit notices (`WORKTREE_REMOTE_UNCHECKED` after a 30-second unreachable remote, registration advisories)
leave the worktree in place; whether the item is ready depends on its readiness fields, not on the exit code.
One CLI code covers both item-specific and repository-wide causes (a failing `post-checkout` hook is
`WORKTREE_ADD_FAILED`; a broken setup command is `WORKTREE_SETUP_FAILED` for every item), so the code alone does not
show whether later items would fail too.

## Not measured

Net token, cost, latency and conversation-availability effects of the list form remain unmeasured. This material
grants no authority for a later job.
