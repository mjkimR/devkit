---
id: PLAN-incubation-sdd-baseline
spec: SPEC-incubation-sdd-baseline
---

# Technical Plan: Incubation SDD baseline

## 1. Constitution & Invariant Review

`ADR-adopt-sdd-through-an-evidenced-baseline-playbook` authorizes one spec-owned playbook and semantic readiness.
`ARCH-05-2-components` permits bundle content and mirrored package integration tests. No architectural invariant changes.
Governance protects accidental misuse; no machinery is added to prevent a repository owner deliberately bypassing guidance.

## 2. Architecture Overview & Impact

Add `playbooks/sdd-baseline/` to the existing spec bundle and select it in core. The entry orders preparation,
evidence review and activation; a referenced report template captures scope, source and evidence without a workflow binding.
There is no product runtime code or new dependency. Existing brownfield containment remains separate.

## 3. Component & Interface Design

- `SKILL.md`: explicit entry, staged package/assets while incubation, bounded current-document work, readiness,
  exact-effects activation and recovery.
- `references/report-template.md`: ordinary material report with identity, retained-item evidence table, gaps,
  verification outcomes, activation effects and partial-state recovery.
- Manifest and package test: core selection, deployed reference integrity, discovery and policy/evidence boundaries.
- Future Living Spec: the target-docs blueprint selects delivery capability/use case, harness adoption and guides.

The playbook consumes semantic current facts and the prerequisite common policy interface. It does not parse a live
context schema. Exact activation commands are bound to the delivered policy before end-to-end verification.

## 5. Error Handling & Edge Cases

Missing evidence leaves the project in incubation. Changed relevant source invalidates affected observations.
Failed installation/update/sync records actual partial state and next recovery. Preserve unrelated edits and existing
SDD history. A project already using SDD follows ordinary reconciliation or brownfield adoption instead.

## 6. Verification & Test Plan

Mechanical tests load the manifest, sync an isolated consumer and discover/read the deployed playbook/report template.
Guidance assertions guard ordering and prohibited retrospective artifacts; they do not prove semantic adoption.
After prerequisites land, sample-app exercises prove AC-01 through AC-07 for success and gap/source/failure paths,
recording exact commands, source and real versus simulated decisions. Run relevant package lint/types,
`just test-affected` with its full fallback, sync check, code review, Living Spec reconcile review and cumulative governance.
