---
id: PROP-post-merge-verification-target
title: Post-merge verification Living Spec targets
summary: "Move final content verification to the landed runtime and simplify integration inputs while retaining Git authority and recovery."
status: draft
proposal: SPEC-post-merge-verification
created_at: 2026-11-04
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
  - file: docs/decisions/2026-10/20261022-proposal-acceptance.md
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
  - file: docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/architecture/ARCH-06-runtime-view.md
  - file: docs/decisions/2026-11/20261102-local-and-pull-request-integration.md
  - file: docs/decisions/2026-11/20261102-delivery-approval-and-lifecycle-authority.md
  - file: docs/decisions/2026-11/20261102-test-selection-and-ci.md
---

# Post-merge verification Living Spec targets

## 1. Capabilities

- `CAP-INT-mcp-services`: reduced prepare/integrate interface, Git-only checks, pending verification output,
  preserved scoped cleanup, provider decoupling, and local/PR partial recovery.
- `CAP-DLV-delivery-workflows`: branch verification and mandatory Host-led final verification, in-scope target
  repair, proposal acceptance isolation, source workflow holds and delivery-completion reporting.
- `CAP-DLV-proposal-planning`: composed acceptance yields before handoff, retaining authorized intent and effort;
  the Host verifies the landed runtime before invoking handoff in a fresh process.
- `CAP-DLV-project-policy`: remove mandatory integration provider selection and document legacy config migration;
  retain base authority and route policy.
- `CAP-DLV-cli-and-output`: mirror affected integration/result references without adding a new workflow schema.
- `CAP-GOV-evaluation-lifecycle`: snapshots still use their invoking runtime; integration no longer uses the target
  runtime as a source-content judge. Standalone rules retain their normal validation.
- `CAP-WT-task-worktrees`: retain cleanup safety and explain that Git completion precedes final project verification.
- `CAP-HARN-agent-guidance`: final checks for direct work and batches; a failed batch needs repair and recheck.

## 2. Use cases

`UC-drive-development-to-integration` adds runtime synchronization, final checks and target repair after Git effects.
`UC-plan-and-hand-off-a-proposal` keeps acceptance eligibility while adapting the composed merge and final checks.
`UC-handle-delivery-problems-and-exceptions` distinguishes a failed merge, failed final check and failed cleanup.
No composed product UI changes.

## 3. Architecture and decisions

`ARCH-05-2-components` updates the integration/provider ownership description; no dependency edge is added.
`ARCH-06-runtime-view` reflects the Host-led post-land sequence and fresh runtime invocation.
Promote `ADR-post-merge-verification` on handoff. Add partial-supersession pointers to its four named ADRs without
retiring their surviving authority, Git and CI clauses.

## 4. Guidance and quick references

Update spec-integrate, completion/worktree references, git-operator, orchestration, Development and Planning worker
contracts and affected workflows in the spec bundle. Inspect adaptive-dev guidance and update affected callers
within its owning bundle if present; any such source requires its context and an explicit task boundary.
Update docs/development/ci-cd.md, docs/development/workflow.md, relevant reference pages, consumer guides and AGENTS.md.
Regenerate projections/receipt through devkit sync; never edit projected assets by hand.

## 5. Before and after

Before: branch checks -> old-runtime content readiness -> merge/cleanup -> optional later integrated tests.
After: branch checks -> approved Git merge/cleanup -> synchronize landed runtime -> final checks -> delivery complete.
A failure after landing leads to target repair and recheck, with landed Git effects preserved.
