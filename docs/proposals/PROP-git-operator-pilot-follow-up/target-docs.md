---
id: PROP-git-operator-pilot-follow-up-target
title: Git-operator pilot follow-up targets
summary: "Map candidate lifecycle, readiness and activity-scope improvements to owning contracts while preserving Host authority and explicit evidence limits."
status: draft
proposal: PROP-git-operator-pilot-follow-up
created_at: 2026-10-30
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
---

# [PROP-git-operator-pilot-follow-up-target] Git-operator pilot follow-up targets

PROP-git-operator-pilot-follow-up is an umbrella Backlog draft. These targets are candidates for its eventual
children, not declarations of delivered behavior.

## 1. Owning contracts

- CAP-DLV-delivery-workflows: exact Planning acceptance execution, effect/readiness reporting, valid Planning
  return-stage guidance and bounded per-item batch outcomes. Retain Host decisions and the three role statuses.
- CAP-COLL-work-scope-registry: distinguish current activity write evidence from future implementation candidates
  while preserving informational semantics, provenance, partial coverage and all actual overlap reports.
- CAP-WT-task-worktrees: document generated handoff state and setup evidence only if the selected design changes
  that interface; the current successful uncommitted transaction is not reclassified as a failed CLI operation.

## 2. Source and verification boundaries

Changes belong in source bundle role/dispatch/operating guidance and the owning devkit-spec features, with focused
contract, CLI and partial-recovery tests. Managed files and projections change through ordinary sync after source
changes; they are not edited directly. No implementation or sync is part of this Backlog intake.

GOP-01–07 are proposed acceptance checks. Decomposition assigns only the relevant checks to each selected child.
An independently selected behavior or lasting authority decision receives its own PADR/ADR when required by the
existing lifecycle; this draft does not revise accepted decisions. Existing engine and host checks remain in force.

## 3. Evidence retention

MAT-git-operator-consumer-pilot holds the bounded resource-indexer observations and untested rows.
MAT-git-operator-development-evidence remains the separate development/projection/fixture baseline.
Keep CLI exit/effects, role status, actual Git observations, host emulation and remaining work distinct.
Do not replace unknown timing, tokens, pricing or cross-host behavior with estimates or inferred guarantees.
