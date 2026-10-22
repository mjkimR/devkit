---
id: FB-split-feedback-disposition-outside-scope
title: A Planning split leaves promoted source feedback pointing at the narrowed proposal
scope: repo
kind: friction
category: missing-capability
target: planning-worker write boundaries; feedback disposition on a Planning split
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-19
---

# [FB-split-feedback-disposition-outside-scope] A Planning split leaves promoted source feedback pointing at the narrowed proposal

## 1. Friction / Question (friction, question)

- **Context**: Planning of PROP-integration-follow-ups split three of its four extensions out: two into new drafts,
  one (auto dispatch) back to the open feedback it came from, as the user decided.
- **Expectation**: After the split, each source feedback's status and disposition name where its work now lives,
  and the feedback that is no longer planned anywhere is open again.
- **Actual**: `FB-auto-integration-dispatch`, `FB-pr-remote-and-squash-integration` and
  `FB-multi-host-integration-ergonomics` live in a completed spec's `feedback/` with `status: promoted` and the
  disposition `SPEC-integration-follow-ups`. The planning worker may write only inside its proposal directory and new
  drafts, so it cannot set auto dispatch back to `open` or point the other two at their drafts; the handoff routes
  only this proposal's own feedback.
- **Workaround (or Interpretation Chosen)**: Left the three files unchanged, recorded the needed edits as open
  findings in the worker envelope for the Host.
- **Suggestion**: Name who updates source feedback on a Planning split (the Host after the plan branch merges, or the
  handoff from a list in the proposal), and say so in the planning-worker contract and backlog.md.

## Evidence

```text
specs/2026-10/20261017-hook-driven-integration-cleanup/feedback/{auto-integration-dispatch,pr-remote-and-squash-integration,multi-host-integration-ergonomics}.md:
  status: promoted; Disposition: `PROP-integration-follow-ups`: drafted in Backlog together with the other ...
planning-worker write boundaries: "Allowed: the proposal directory ... and a new draft proposal for a follow-up"
answer-01.yaml q1-split: auto dispatch (Q2) stays as open feedback; Q3 and Q4 become child drafts
```

## Disposition

Dismissed under `ADR-feedback-lifecycle`: promotion closes the originating feedback. Subsequent splitting
or completion is tracked in the receiving work, without reopening the source or requiring a new source disposition.
No additional Planning-worker permission to maintain terminal feedback is needed. The original observation is
retained as history.
