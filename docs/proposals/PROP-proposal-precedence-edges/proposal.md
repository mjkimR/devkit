---
id: PROP-proposal-precedence-edges
title: Enforced ordering between proposals
summary: Makes an ordering claim between proposals visible to the handoff gate or to Planning start, so a draft whose premise depends on other proposals not yet being handed off surfaces when that premise is stale.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: delivery/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    - docs/proposals/PROP-proposal-precedence-edges/
  excludes:
    - packages/devkit-docs/
    - packages/devkit/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-proposal-precedence-edges] Enforced ordering between proposals

## 1. Background & Hypothesis

`FB-draft-precedence-claim-unenforced`: a draft proposal stated in prose that its handoff precedes the handoff of
two accepted proposals, and argued its change was cheap because neither had a spec yet. Both were handed off, and
one spec integrated, before the draft reached Planning. Nothing flagged the stale premise: `depends_on` is declared
only by the dependent, the accepted proposals carried no edge to the draft, and `devkit spec proposal check`
reported `editable=yes` with no notice.

Hypothesis: an ordering claim that lives where a gate reads it, or a status report of the documents a draft names
when Planning starts, makes a stale ordering premise visible before the first Planning decision.

## 2. Technical Spike Questions

- **Q1**: Should a draft declare a prerequisite edge onto accepted proposals (for example a `precedes:` list) that
  `devkit spec proposal handoff` checks for the named proposals, or should the existing `depends_on` on the
  dependents stay the only edge?
- **Q2**: Should Planning start (`status: reviewing`) or `devkit spec proposal check` report the current status of
  every proposal or spec the draft names as following it, as a notice rather than a refusal?

## 3. Proposed Design & Impact

To settle in Planning. Candidate: a notice-level report at Planning start and in `proposal check` listing each
named proposal or spec that was already handed off, plus an optional reverse edge the handoff gate refuses on while
the preceding draft is not handed off. Impact is limited to the proposals feature of `devkit-spec`, its tests and
`CAP-DLV-proposal-lifecycle`.

## 4. Lifecycle & Retirement Criteria

Retired when the accepted design is handed off and `FB-draft-precedence-claim-unenforced` is marked promoted to it.
