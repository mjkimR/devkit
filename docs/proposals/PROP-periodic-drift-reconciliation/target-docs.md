---
id: PROP-periodic-drift-reconciliation-target
title: Target Living Spec Structure for PROP-periodic-drift-reconciliation
status: draft
proposal: PROP-periodic-drift-reconciliation
created_at: 2026-10-14
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
  - file: docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md
  - file: docs/stories/governance/US-keep-the-living-spec-consistent.md
---

# [Blueprint] PROP-periodic-drift-reconciliation: Target Living Spec Structure for Spec-code drift reconciliation maintenance playbook

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-periodic-drift-reconciliation is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets. The frontmatter `targets` list is the structured form of the documents named below; paths that do not exist yet are planned documents.

---

## 1. System Capabilities Plan (docs/capabilities/)

- New CAP-DLV-drift-reconciliation (planned path in targets): the manually invocable reconciliation playbook, evidence report, user dispositions, and verification.
- `CAP-DLV-delivery-workflows`: link the periodic sweep to per-feature reconciliation (`spec-sync`).
- `CAP-TRACE-code-entrypoints`: a consumer note if the sweep reads entrypoints; path-only stale-document hints stay
  rejected (proposal section 4).

---

## 2. User Stories Plan (docs/stories/)

- `US-keep-the-living-spec-consistent`: cover manual maintenance review and the update-documentation, fix-code, or defer outcomes.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

`ADR-dual-source-of-truth-and-periodic-reconciliation` stays the parent decision. No detector threshold or scheduling
trigger decision is part of this playbook delivery.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

A maintenance playbook over existing commands and evidence review, with a demonstrated manual run. Catalog bundle
and preset placement remain a Planning question; no dedicated detection command, standalone skill, or scheduler
integration is included.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Drift review | Ad hoc inspection | A scoped playbook combining existing checks and semantic evidence review |
| Cleanup | Ad hoc, after drift piles up | A manually invoked sweep with user dispositions, verified changes, and traceable deferrals |
