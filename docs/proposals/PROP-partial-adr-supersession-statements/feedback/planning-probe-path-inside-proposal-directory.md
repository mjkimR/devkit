---
id: FB-planning-probe-path-inside-proposal-directory
title: The Planning payload rule asks for an ignored probe path inside the proposal directory, where none can exist
scope: repo
kind: friction
category: instruction-conflict
target: the spec-delegate skill's references/payload.md (Workers, Planning)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-planning-probe-path-inside-proposal-directory] The Planning payload rule asks for an ignored probe path inside the proposal directory, where none can exist

## 1. Friction / Question (friction, question)

- **Context**: A Planning turn that ran two read-only inventory scripts over `docs/decisions/`.
- **Expectation**: The payload rule for a `planning-worker` reads "Name an ignored probe path inside the proposal
  directory, preparing one if none exists."
- **Actual**: A proposal directory is tracked and `.gitignore` ignores no path below `docs/proposals/`, so the Host
  cannot prepare an ignored path there without editing `.gitignore`. The payload named `tmp/planning-probes/` at the
  worktree root instead, which the `planning-worker` contract allows ("only the ignored path the payload names").
- **Workaround (or Interpretation Chosen)**: Used the root path the payload named and kept the evidence in
  `materials/`.
- **Suggestion**: Let the payload rule name an ignored path inside the worktree, as the `code-reviewer` row does
  ("an ignored probe path inside the worktree"), instead of one inside the proposal directory.

## Diagnostic Details

- **Reproduction**: Build a `planning-worker` payload by `references/payload.md` for a proposal whose Planning needs a
  probe script.
- **Expected / Actual**: expected a preparable ignored path at the named place; `git check-ignore` matches only
  `/tmp/` at the root.
- **Versions**: the repository at `b3e4753d`.
- **Conditions**: every Planning turn that needs a throwaway script.
- **Workarounds Attempted**: the root `tmp/planning-probes/` path; succeeded.
- **Related Assets**: the `planning-worker` contract (Write boundaries, Temporary probes).

## Evidence

```text
payload.md, Workers: "Planning: ... Name an ignored probe path inside the proposal directory, preparing one if none exists."
planning-worker.md: "Temporary probes: only the ignored path the payload names."
.gitignore: "/tmp/" is the only rule that covers a probe path; no rule matches docs/proposals/**.
payload of this turn: probes at <worktree>/tmp/planning-probes/ ("no ignored path exists inside the proposal directory").
```
