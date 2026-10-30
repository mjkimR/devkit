---
id: FB-received-feedback-status-during-planning
title: Status of feedback a proposal fixes directly is ambiguous
scope: repo
kind: question
category: instruction-conflict
target: .devkit/managed/spec/skills/spec/references/source-feedback.md
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-10-30
---

# [FB-received-feedback-status-during-planning] Status of feedback a proposal fixes directly is ambiguous

## 1. Friction / Question (friction, question)

- **Context**: A Planning answer settled how the proposal addresses a feedback item it holds in its own `feedback/`
  directory; the fix is guidance in the same proposal's Development.
- **Expectation**: One reference names the status a proposal sets when it receives feedback it will fix itself.
- **Actual**: The proposal template's `Source feedback` comment says promotion closes feedback handed to follow-up
  work, and the `feedback-hygiene` playbook defines `promoted` as follow-up work receiving the item.
  `source-feedback.md` keeps a direct-fix source `open` until completion verifies it, and says Planning alone does not
  verify a fix.
- **Workaround (or Interpretation Chosen)**: The worker set `status: promoted` with a disposition naming
  `SPEC-git-operator-result-readiness`, reading the proposal as the follow-up work that received the item.
- **Suggestion**: State in `source-feedback.md` whether a proposal that receives feedback promotes it at Planning or
  keeps it `open` for resolution at completion.

## Evidence

```text
templates/proposal.md: "Promotion closes the feedback by handing it to follow-up work; ... Resolution closes a
verified direct fix without promotion."
source-feedback.md: "Handoff, planning, document checks or integration alone do not verify a fix."
```

## Disposition

Dismissed by the user: `source-feedback.md` already answers it. A direct-fix source stays `open` through Planning and
handoff, because they do not verify a fix, and completion sets it to `resolved`. This item's own source was handled that way.
