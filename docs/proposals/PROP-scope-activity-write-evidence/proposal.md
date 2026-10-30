---
id: PROP-scope-activity-write-evidence
title: Show current activity writes beside future implementation impact in scope output
summary: "Show each current activity's actual write boundaries in scope inspection separately from declared or candidate future implementation impact, keeping every overlap and coverage gap visible and the output informational."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/collaboration/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/scope/
    - packages/devkit-spec/tests/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - docs/capabilities/collaboration/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-scope-activity-write-evidence] Show current activity writes beside future implementation impact in scope output

## 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), scope observations exposed future
implementation candidates while current Planning writers owned distinct proposal directories. The Host had to explain
that difference before parallel Planning could proceed.

The hypothesis: scope output that shows each current activity's actual write boundaries (a Planning run writes only
its proposal directory) beside declared or candidate future impact lets the Host schedule without re-deriving it.
`CAP-COLL-work-scope-registry` owns this informational evidence.

## 2. Technical Spike Questions

- **Q1 Presentation**: Can scope output show current activity write boundaries beside declared and candidate
  implementation impact without hiding unresolved inputs, suppressing overlaps or becoming write authority?
- **Q2 Provenance**: How do candidate and observed provenance and the partial-coverage signal stay visible?

## 3. Proposed Design & Impact

- `devkit spec scope collect` adds current activity write evidence as a distinct kind.
- `CAP-COLL-work-scope-registry` keeps informational semantics, provenance, partial coverage and every actual overlap.
- The Host keeps the scheduling decision.

Acceptance check (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-04 | Disjoint proposal-only Planning writes and overlapping future implementation candidates | Scope is inspected for scheduling | Both facts and unresolved coverage remain visible; the result grants or refuses no write and the Host retains the decision. |

### Non-goals

- **Scope Excluded**: claiming that informational scope observations authorize writes, or that unresolved coverage
  means no conflict.
- **Scope Excluded**: redefining overlap to hide it.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-scope-activity-write-evidence`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
