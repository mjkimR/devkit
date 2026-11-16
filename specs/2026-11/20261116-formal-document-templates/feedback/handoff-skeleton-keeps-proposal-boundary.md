---
id: FB-handoff-skeleton-keeps-proposal-boundary
title: "Handoff skeleton keeps the removed proposal directory as a planned and task boundary"
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/proposals/usecases/specs.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-handoff-skeleton-keeps-proposal-boundary] Handoff skeleton keeps the removed proposal directory as a planned and task boundary

## 1. Friction / Question (friction, question)

- **Context**: A Development worker rewrote the handoff skeletons of a spec handed off from a proposal.
- **Expectation**: The skeleton `plan.md` Planned Boundaries and the `tasks.md` `_Boundary:` list only paths the
  Development turn can write.
- **Actual**: Both listed `docs/proposals/PROP-<slug>/`, which handoff had already removed; the Host's write scope
  correctly left it out, so the skeleton and the payload disagreed.
- **Workaround (or Interpretation Chosen)**: Dropped the path while rewriting `plan.md` and `tasks.md` and recorded it
  as an assumption in `spec.md`.
- **Suggestion**: Exclude the handed-off proposal directory when the handoff builds the boundary lists.

## Diagnostic Details

- **Reproduction**: Hand off a proposal whose Planned Boundaries include its own proposal directory; read the new
  spec bundle's `plan.md` and `tasks.md`.
- **Expected / Actual**: Expected no `docs/proposals/PROP-<slug>/` entry; actual entry present in both files.
- **Versions**: devkit worktree at the handoff commit of `SPEC-formal-document-templates`.
- **Conditions**: `sdd-proposal` handoff to `sdd-spec-feature`.
- **Workarounds Attempted**: Manual removal during `specify`; succeeded.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/specs.py` (Planned Boundaries
  and task boundary rendering).

## Evidence

```text
plan.md (handoff skeleton) Planned Boundaries: ... - `docs/proposals/PROP-formal-document-templates/`
tasks.md (handoff skeleton) Task 1.1 _Boundary: ..., docs/proposals/PROP-formal-document-templates/, ...
ls docs/proposals/ | rg formal  -> no entry
```
