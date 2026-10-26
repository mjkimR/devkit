---
id: FB-worktree-sandbox-location
title: Document sandbox-safe worktree locations
scope: repo
kind: friction
category: instruction-conflict
target: .agents/skills/spec/references/worktree.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-24
---

# [FB-worktree-sandbox-location] Document sandbox-safe worktree locations

## 1. Friction / Question

- **Context**: Starting the required development worktree and writing files in it.
- **Expectation**: The documented `devkit worktree start` procedure creates a usable worktree for the current agent session.
- **Actual**: The default sibling worktree path was outside the session's writable roots, so file changes required an escalated command.
- **Workaround (or Interpretation Chosen)**: Use the command's `--workspace-root` option to place future task worktrees under an already-writable workspace root.
- **Suggestion**: Document how to choose a workspace root inside the writable checkout when the default sibling path is outside the agent's writable roots.

## Evidence

```text
Observed: devkit worktree start created the required worktree beside the checkout; shell writes to that path were denied by the workspace-write sandbox and succeeded only after escalation. The command supports --workspace-root.
```

## Diagnostic Details

- **Reproduction**: Start a required worktree using the documented default command in a workspace-write session, then write a new file under the returned sibling path.
- **Expected / Actual**: The new worktree should be writable for the task; writes were denied because the path was outside configured writable roots.
- **Versions**: unknown
- **Conditions**: Workspace-write sandbox; linked worktree created outside the writable checkout.
- **Workarounds Attempted**: Escalated write succeeded; setting `--workspace-root` inside the checkout was identified as a future alternative but not tested in this run.
- **Related Assets**: `devkit worktree start --workspace-root`; `.agents/skills/spec/references/worktree.md`.

## Disposition

Resolved by `SPEC-delegation-sandbox-guidance`, with a correction: `--workspace-root` does not place a worktree. It
only names a directory inside the checkout; the task worktree is always `<parent of base>/<base name>-wt-<branch>`
(`CAP-WT-task-worktrees`). The `spec` skill's `references/worktree.md` now states this under "Sandboxed sessions"
and names the permitted route when the path is outside the writable roots: the host's per-operation approval, or
writable roots the user grants; never moving or re-creating the worktree or changing a host setting. Verified by
`packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`.
