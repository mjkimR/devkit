---
id: PROP-worker-audit-known-host-advance
title: Keep the worker audit baseline across known Host-owned target advances
summary: "Let worker inspection keep the original source-audit baseline while accounting separately for target advances the Host declared as its own, so independent integrations need not wait for a running worker; unknown or dirty base changes still stop."
status: draft
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: high
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/features/worker/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-worker-audit-known-host-advance] Keep the worker audit baseline across known Host-owned target advances

## 1. Background & Hypothesis

The exact-base observation rule caused unnecessary serialization in the resource-indexer consumer pilot
(`MAT-git-operator-consumer-pilot`): the Host held independent Planning integrations while a Development worker ran,
solely to preserve its recorded base HEAD. The worker reference (`spec-delegate/references/worker.md`) requires the
base checkout's status and HEAD to match the pre-spawn record, and `devkit spec worker inspect` derives
`base_checkout` in `features/worker/usecases/inspect.py`.

Keeping the original source-audit baseline need not mean forbidding all known Host-owned target advances. A bounded
alternative needs explicit design and tests; the pilot announced it but did not exercise it during an active worker.

The hypothesis: inspection can audit the worker's own range against its original baseline and account separately for
target advances the Host declared, without turning them into worker authorship or write permission.

## 2. Technical Spike Questions

- **Q1 Declaration**: How does the Host declare a target advance as its own (an inspection input, a record, or a CLI
  observation), and how does inspection verify it against Git?
- **Q2 Boundary**: Which changes still stop the worker: unknown or dirty base changes, real conflicts, and anything
  else Planning finds?
- **Q3 Interaction with light merging**: If `PROP-integration-merge-moved-target` lands, the integrating command
  merges a moved target itself. This proposal adds no manual base-merge requirement back.

## 3. Proposed Design & Impact

- `spec-delegate/references/worker.md` and `devkit spec worker inspect` separate the worker's audit range from declared
  Host advances.
- `CAP-DLV-delivery-workflows` states the audit-baseline versus known-Host-advance contract.
- Planning effort is high because this relaxes a safety check: an exception that is too broad would let unknown base
  changes or Host commits count as worker-authorized, weakening the write audit that
  `ADR-reusable-lifecycle-resource-manager` keeps with the Host.

Acceptance check (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-08 | An original worker audit baseline A, a known Host-only target advance B and a returned source C | Worker results and integration readiness are inspected | A..C is audited for worker changes and B is accounted for separately. Unknown or dirty target changes or actual conflicts stop; Host changes do not become worker authorship or permission. |

### Non-goals

- **Scope Excluded**: a global repository lock or autonomous scheduler.
- **Scope Excluded**: treating a known Host advance as worker authorship, write permission or a skip of the final
  integration checks.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-worker-audit-known-host-advance`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
