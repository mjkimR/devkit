---
id: FB-supersession-rewording-outside-payload-scope
title: A handoff ADR announces a body rewording of the superseded ADR that the Development payload does not admit
scope: repo
kind: friction
category: other
target: the spec-orchestrate skill (Development payload write scope for partial supersession)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-11
---

# [FB-supersession-rewording-outside-payload-scope] A handoff ADR announces a body rewording of the superseded ADR that the Development payload does not admit

Nature: a mismatch between a handed-off decision and the Development write scope the Host derives from it.

## 1. Friction / Question (friction, question)

- **Context**: Development of a spec whose promoted ADR supersedes an earlier ADR in part. The new ADR's outcome and
  the superseded ADR's pointer line both state that the earlier ADR's `query`/history wording "is reworded" to the
  remaining read surfaces; `target-docs.md` plans that body rewording.
- **Expectation**: the Development payload admits the files the plan says Development changes.
- **Actual**: the payload admitted only the superseded ADR's "Superseded in part" line. `RULE-decision-supersession`
  requires that line to repeat the superseder's statement verbatim, so it cannot absorb the rewording either; the
  announced body rewording stayed undone and was waived in `reconcile.md` for the Host.
- **Workaround (or Interpretation Chosen)**: left the ADR unchanged, recorded spec assumption A1 and a waived reconcile
  target, and reported the item to the Host.
- **Suggestion**: when a handoff ADR's supersession statement announces a body rewording of the earlier ADR, the
  Development payload derived for it should admit that ADR's body (rewording only), or the statement should not
  promise one.
