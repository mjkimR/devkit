---
id: FB-handoff-rewrite-edits-sibling-draft
title: Handoff reference rewrite edits a sibling draft on the dev branch
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal handoff
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-handoff-rewrite-edits-sibling-draft] Handoff reference rewrite edits a sibling draft on the dev branch

## 1. Friction / Question (friction, question)

- **Context**: `devkit spec proposal accept deep-research-bundle --mode accept_and_handoff` while a sibling proposal
  that cites it, `PROP-rename-incubation-to-adaptive-dev`, was in Planning on its own `plan-` branch.
- **Expectation**: The handoff rewrites references inside the handed-off Unit and its promoted ADRs; a sibling draft
  owned by another Planning branch is left to that branch, or the rewrite is reported for the Host to schedule.
- **Actual**: The rewrite also edited the sibling's `proposal.md` (its base-branch draft version) in the new
  `dev-deep-research-bundle` worktree, uncommitted (`SPEC_PROPOSAL_REFS_REWRITTEN` listed it among its targets). After
  the sibling's Planning merged into `main`, merging `main` into the dev branch conflicted on that file.
- **Workaround (or Interpretation Chosen)**: The Host took the accepted version from `main` and ran `devkit rules fix`
  on the sibling proposal, which rewrote the four citations to `SPEC-deep-research-bundle`.
- **Suggestion**: Leave proposals owned by an active `plan-` branch out of the handoff rewrite and report them as
  pending rewrites, or rewrite them only through `devkit rules fix` once their Planning merges.

## Diagnostic Details

- **Reproduction**: Two related drafts in parallel Planning; accept and hand off the cited one first while the citing
  one is still in Planning; later integrate the citing one and merge `main` into the dev branch.
- **Expected / Actual**: Expected no edit to a Planning-owned sibling; observed a one-line edit and a later conflict.
- **Versions**: devkit workspace at `fb9b549a`..`b2711684`.
- **Conditions**: `local-orchestrated`, `worktree = "required"`, `plan-accept = ask`.
- **Workarounds Attempted**: Accepted version plus `devkit rules fix`; succeeded.
- **Related Assets**: `devkit spec proposal handoff`, `devkit spec proposal accept --mode accept_and_handoff`,
  `SPEC_PROPOSAL_REFS_REWRITTEN`, `CAP-DLV-proposal-incubation`.

## Evidence

```text
[NOTICE] (SPEC_PROPOSAL_REFS_REWRITTEN) 10 ID reference(s) to PROP-deep-research-bundle or its PADRs now name the spec or the ADRs
[TARGET] ..., docs/proposals/PROP-rename-incubation-to-adaptive-dev/proposal.md, ...
CONFLICT (content): Merge conflict in docs/proposals/PROP-rename-incubation-to-adaptive-dev/proposal.md
```
