---
id: PADR-host-native-worktrees-excluded
title: Host-native worktrees stay excluded
summary: 'Keeps devkit worktree start as the only way an orchestrated activity gets its worktree: Claude Code isolation: worktree and WorktreeCreate hooks, Codex managed worktrees and Antigravity branch workspaces are not adopted or registered.'
proposal: PROP-worktree-host-compatibility
status: draft
created_at: 2026-10-19
---

# [PADR-host-native-worktrees-excluded] Host-native worktrees stay excluded

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q4 and Q7 of `PROP-worktree-host-compatibility`; option O4. Evidence: `MAT-worktree-host-spike-evidence`
  §3, `MAT-host-worktree-flows`, `envelopes/scout-01.yaml`, `envelopes/scout-02.yaml`.

---

## 1. Context & Problem Statement

Every host offers its own worktree flow. A devkit activity is one `plan-<slug>` or `dev-<slug>` branch in one
worktree from `devkit worktree start`, continued across several one-shot worker turns, registered in the scope
registry and integrated by `finish`; `spec-orchestrate` already forbids host-native worktrees. The spike asked whether
a host flow can be adopted and registered instead, chiefly a Claude Code `WorktreeCreate` hook that runs
`devkit worktree start` for `isolation: worktree` subagents.

## 2. Decision Drivers

- The branch name and path stay computable by every session and agent (`CAP-WT-task-worktrees`).
- Several worker turns of one activity land in the same worktree and branch.
- A hook must not change worktree creation for work devkit does not orchestrate.

## 3. Considered Options

- **Claude Code `isolation: worktree` with the default creation.** Cons: a fresh `.claude/worktrees/<name>` on
  `worktree-<name>` per subagent run, from `fresh` (the remote default branch) or `head` only, so a later turn never
  sees the earlier turn's branch. Pros: Claude Code then refuses edits, command directories and Git redirects into the
  main checkout.
- **Claude Code `WorktreeCreate`/`WorktreeRemove` hooks running devkit.** Cons: the hook receives a generated `name`
  and the session fields, never the activity's slug or branch, so it cannot find an existing activity worktree; it
  replaces creation for every `--worktree` session, background session and workflow worktree as well; a projected
  hook would be a host setting devkit does not write (`CAP-DIST-agent-projections`). Pros: hook-created worktrees are
  kept when a subagent ends and are skipped by Claude Code's sweep, so `finish` would stay devkit's.
- **Codex managed worktrees.** Cons: detached HEAD without a branch under `$CODEX_HOME/worktrees`, created by the app
  or `codex exec --worktree`, with no writable grant for the shared git dir.
- **Antigravity `branch` workspace.** Cons: location, base and branch are undocumented, and the worktree is removed
  when the subagent is killed.
- **Keep `devkit worktree start` as the only source (selected).**

## 4. Decision Outcome

- An orchestrated activity MUST get its worktree from `devkit worktree start` (or `start --existing-branch`), as
  `spec-orchestrate` states; no host-native worktree is adopted, registered or created by a devkit hook.
- Worker contracts MUST NOT set `isolation: worktree` in their Claude Code blocks.
- Reopen when a host lets the caller name the worktree path or branch of an isolated subagent (for example a path
  parameter on the spawn, or the spawn's payload in the `WorktreeCreate` input), so an existing devkit worktree can be
  passed and the host's isolation enforcement gained.

## 5. Consequences

- No change to `devkit.worktree`, the scope registry or the projected hooks.
- The isolation enforcement Claude Code applies to isolated subagents is not available to workers; the Host's
  committed-range check stays the guarantee.
