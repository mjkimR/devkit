---
id: FB-handoff-pointer-owner-docstring-mismatch
title: Handoff docstrings say Development rewrites the partial-supersession pointer while post-handoff guidance gives it to the Host
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-handoff-pointer-owner-docstring-mismatch] Handoff docstrings say Development rewrites the partial-supersession pointer while post-handoff guidance gives it to the Host

## 1. Friction / Question (friction, question)

- **Context**: Planning a proposal whose PADR supersedes an accepted ADR in part, and deciding whether the proposal's
  `boundaries` must own that ADR so the "Superseded in part by" line can be clarified after handoff.
- **Expectation**: One owner for clarifying the pointer, stated the same way in the handoff source and the
  post-handoff guidance.
- **Actual**: The handoff module docstring and `_clause` say "Development replaces the summary with the replaced
  clauses", while the `spec-next` post-handoff reference says the Host clarifies the pointer in a commit on
  `dev-<slug>` before a worker starts. The resolved `FB-handoff-pointer-carries-summary-not-clauses` chose the Host
  route, and the docstrings were not updated.
- **Workaround (or Interpretation Chosen)**: Followed the post-handoff reference: the Host clarifies the pointer, and
  the proposal owns the ADR only for a separate reference repair.
- **Suggestion**: Change both docstrings to name the Host's post-handoff clarification, so Planning does not add the
  ADR to Development's boundary for the pointer alone.

## Diagnostic Details

- **Reproduction**: Read `handoff.py` lines 14-17 and the `_clause` docstring, then `post-handoff.md` step 4.
- **Expected / Actual**: Expected one owner; actual Development in source, Host in guidance.
- **Versions**: worktree base `f810077abd5583303b18105c690b95ca4ac73a3b`.
- **Conditions**: proposals with a PADR that supersedes an ADR in part.
- **Workarounds Attempted**: followed the guidance; the proposal text was corrected before commit.
- **Related Assets**: `FB-handoff-pointer-carries-summary-not-clauses`, the `spec-next` post-handoff reference.

## Evidence

```text
handoff.py:17   "Development replaces the summary with the replaced clauses."
handoff.py:749  "Development replaces it with the replaced clauses."
post-handoff.md step 4: "Review each `Superseded in part by` pointer handoff added. If it repeats the new ADR's
summary instead of naming the replaced clauses, clarify it from the new ADR's Decision Outcome"
post-handoff.md: "Commit link fixes and partial-supersession pointer clarifications on `dev-<slug>` as a later Host
commit before a worker starts."
```
