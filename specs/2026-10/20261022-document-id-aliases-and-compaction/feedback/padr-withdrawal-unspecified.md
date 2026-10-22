---
id: FB-padr-withdrawal-unspecified
title: Planning gives no procedure for withdrawing an unaccepted PADR
scope: repo
kind: friction
category: spec-ambiguity
target: spec skill references/planning.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-padr-withdrawal-unspecified] Planning gives no procedure for withdrawing an unaccepted PADR

## 1. Friction / Question (friction, question)

- **Context**: A Planning turn folded answers that removed a direction, so a draft PADR recorded in an earlier turn
  had to be withdrawn.
- **Expectation**: The Planning reference says how a PADR is recorded (`devkit spec proposal padr`) and that every
  PADR graduates at handoff, so a withdrawal procedure was expected beside it.
- **Actual**: Neither the planning reference nor the document model names a withdrawn PADR status or a deletion
  rule; handoff would graduate any PADR left in `decisions/`.
- **Workaround (or Interpretation Chosen)**: Deleted the unaccepted PADR file in the fold commit (Git keeps it) and
  named the withdrawal in `proposal.md`.
- **Suggestion**: State in planning.md that a PADR withdrawn before `plan-accept` is deleted in the fold commit and
  named in the proposal's Planning decisions.

## Evidence

- `references/planning.md` step 2 covers recording and summaries only.
- `CAP-DOCS-document-model` lists the `PADR` kind without a status vocabulary for withdrawal.

## Disposition

- **Disposition (resolved)**: `SPEC-feedback-guidance-fixes` states in the `spec` skill's `references/planning.md` step 2 and in
  `CAP-DLV-proposal-incubation` 4.4 that a PADR withdrawn before `plan-accept` is deleted in the fold commit and named
  with its reason in the proposal's Planning decisions; no withdrawn status exists. Verified by the spec's review and
  reconcile self-check.
