---
id: FB-padr-withdrawal-unspecified
title: Planning gives no procedure for withdrawing an unaccepted PADR
scope: repo
kind: friction
category: spec-ambiguity
target: spec skill references/planning.md
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
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
