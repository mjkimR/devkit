---
id: FB-draft-precedence-claim-unenforced
title: A draft's claim to precede other proposals' handoff is not enforced or rechecked
scope: repo
kind: friction
category: missing-capability
target: devkit spec proposal handoff
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-draft-precedence-claim-unenforced] A draft's claim to precede other proposals' handoff is not enforced or rechecked

## 1. Friction / Question (friction, question)

- **Context**: Starting Planning of a draft proposal whose retirement section said its handoff precedes the handoff of
  two accepted proposals, and whose background argued the change was cheap because neither had a spec yet.
- **Expectation**: An ordering claim between proposals is either encoded where the handoff gate reads it, or a stale
  premise surfaces when Planning starts.
- **Actual**: Both other proposals were handed off before this draft reached Planning; one spec had completed and
  integrated on the grammar the draft changes. Nothing flagged the draft: the precedence lived only in its prose,
  and the other proposals carried no `depends_on` edge to it. The cost argument in the draft was already false.
- **Workaround (or Interpretation Chosen)**: The Host compared the draft's claims with the handoff commits, spec
  statuses and worktrees by hand, rewrote the premise, widened the write scope to migrate the landed consumers and
  asked the user how to sequence the remaining parallel proposal.
- **Suggestion**: Either let a draft declare a prerequisite edge onto accepted proposals that `proposal handoff`
  checks, or have Planning start (`status: reviewing`) report the current status of every proposal or spec the draft
  names as a dependent, so a stale ordering premise is visible before the first decision.

## Diagnostic Details

- **Reproduction**: Draft names two accepted proposals as following it; hand both off; start the draft's Planning.
- **Expected / Actual**: A notice about the violated ordering / no notice.
- **Versions**: devkit main after the formal document lifecycle integration.
- **Conditions**: Draft in Backlog, dependents accepted with `depends_on` naming only an earlier spec.
- **Workarounds Attempted**: Manual comparison of handoff commits and spec statuses; succeeded.
- **Related Assets**: `devkit spec proposal handoff`, `devkit spec proposal check`, `SPEC-design-bundle-layout`,
  `SPEC-design-document-lifecycle`, `PROP-design-document-viewer`.

## Evidence

```text
draft retirement section: "handoff precedes the handoff of PROP-design-document-lifecycle and PROP-design-document-viewer"
git log: "spec: hand off design-document-lifecycle to Development", "spec: hand off design-document-viewer to Development"
SPEC-design-document-lifecycle status: completed (integrated into main)
devkit spec proposal check design-bundle-layout -> editable=yes, no notice
```
