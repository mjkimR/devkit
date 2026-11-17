---
id: OPS-assignment-attention-routing
title: "Adaptive assignment attention routing"
status: active
summary: "Routes each attention value of devkit adaptive assignment list to the evidence that separates it and to the existing owner; the choice of action stays with the adaptive-dev resume guidance."
related_capabilities: [CAP-DLV-adaptive-assignments, CAP-WT-task-worktrees]
---

# [OPS-assignment-attention-routing] Adaptive assignment attention routing

On resume, a `devkit adaptive assignment list` row can carry `attention` values such as `head-moved` or
`no-changes`. A value names an observed repository fact, not its cause: `list` makes no agent liveness claim and
exits `0` whatever it lists (`CAP-DLV-adaptive-assignments` §3 rule 10, §4 `list`).

## Routing

| Symptom or state | Discriminating evidence | Next useful owner |
| --- | --- | --- |
| `attention=worktree-missing` | `worktree_state=missing` with `head`, `commits` and `dirty` null (`-` in text). `git worktree list --porcelain` does not list the recorded path, or lists it with `prunable`, or the directory is absent; `devkit worktree status` shows `prunable=yes` for a deleted directory. `show <id>` gives the recorded `worktree` path and whether a return with a `final` commit exists. | `CAP-DLV-adaptive-assignments` §4 `list` defines the observation, and §4 Codes names `ADAPTIVE_WORKTREE_UNAVAILABLE` for commands that need the worktree. `CAP-WT-task-worktrees` §4 owns worktree status lines and their removal authority. |
| `attention=worktree-unreadable` | `worktree_state=present` with `head`, `commits` and `dirty` null: Git cannot read the worktree HEAD (an unborn branch) or reach the recorded `base` from it. `show <id>` gives the `base` to compare. | `CAP-DLV-adaptive-assignments` §4 `list` defines the case. |
| `attention=base-not-ancestor` | The worktree HEAD does not descend from the recorded `base`; `commits` counts `<base>..HEAD` only. `list` compares the base with the current HEAD, while `verify`'s `base` check compares it with the return's `final` commit (`ADAPTIVE_BASE_NOT_ANCESTOR`, `checks.base` in JSON), so the two can differ when the HEAD moved after a return. | `CAP-DLV-adaptive-assignments` §4 Verification, `base` row. `ADR-adaptive-assignment-commands` §4 leaves acceptance of a result whose verification failed to the Host. |
| `attention=head-moved` | A return exists and the worktree HEAD differs from its `final` commit: compare the `list` `head` with the return's `final` in `show <id>`. `verify` reports the same fact as its `head` check (`ADAPTIVE_HEAD_MOVED`, `checks.head` with `head` and `final`). The value can occur beside `base-not-ancestor`. | `CAP-DLV-adaptive-assignments` §4 `return` and Verification, `head` row. |
| `attention=no-changes` | Status `open`, HEAD equal to the `base`, and `dirty=0`; `show <id>` lists only the `assigned` event. The observation excludes ignored files, writes outside the worktree and paths in `dirty_at_assign`, so work there leaves this value unchanged. | `CAP-DLV-adaptive-assignments` §4 `list` and Verification stated limits. `ADR-adaptive-assignment-commands` §4 leaves whether an open assignment's agent still runs to the Host. |

For every row, the choice among recording a return from retained state, dispatching again or closing as abandoned
stays with the adaptive-dev resume guidance,
[current-context.md](../../packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/current-context.md).
A failing `verify` code carries its own advisory, which owns its FIX. For a value or combination that matches no
row, read `show <id>` and the capability's `list` contract, and take the case to the Host under the adaptive-dev
resume guidance.

## Normal-state observation

An assignment that is not `closed` needs no attention when its `list` row reads `attention=-` in text, or
`"attention": []` under `observed` in JSON (`CAP-DLV-adaptive-assignments` §4 `list`). A closed assignment also
reads `attention=-` in text, with `"observed": null` in JSON, so read the `status` field with it. After a return,
`[VERIFICATION: <id> result=pass ...]` from `verify` is the separate normal-state observation for the returned work
(`CAP-DLV-adaptive-assignments` §4 Verification).

## Authority boundary

An attention value cannot establish whether an assignee is still running, why a worktree moved, or whether a result
meets its goal; `ADR-adaptive-assignment-commands` §4 leaves the last to the Host.

## Update triggers

- `observe` in
  [verification.py](../../packages/devkit-adaptive/src/devkit_adaptive/features/assignment/services/verification.py)
  adds, removes or renames an attention value or changes its condition.
- `CAP-DLV-adaptive-assignments` §4 changes the `list` contract.
