---
id: PROP-design-document-pilot-target
title: Pilot deliverables and Living Spec impact
summary: "Bounds retained pilot drafts and evidence while preserving current documentation owners and deferring representation implementation."
status: draft
---

# [PROP-design-document-pilot-target] Pilot deliverables and Living Spec impact

## Current and proposed content

This pilot retains evaluation drafts and evidence under `docs/materials/` after proposal handoff. During Planning,
working evidence stays in this proposal's `materials/`. Development names the dated pilot directory inside the
existing `docs/materials/` parent when it writes its spec. The final three documentation homes are not built here.

| Deliverable | Before | Pilot outcome |
| --- | --- | --- |
| Domain entry | Relationships assembled from distribution capability owners and glossary | Composed relationship explanation citing those unchanged owners |
| Design entry and one detail | Component/runtime overview, capability guarantees and implementation source | Navigable explanation of file/directory replacement with source-symbol links |
| Operations entry | Error codes and recovery instructions in existing contracts/reference | Symptom classification and correct recovery-owner selection without copied instructions |
| Evidence report and statement ledger | No pilot-specific trial evidence | Before/after ownership comparison, reader paths, hypothetical maintenance impact and separate representation recommendations |

## Retained owners and deferred work

`CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership`, `CAP-DIST-manifest-spec`,
`CAP-DIST-content-packages` and `CAP-DIST-agent-projections` retain their contracts. `ARCH-06-runtime-view` and
`ARCH-05-4-distribution-components` retain architecture; the glossary retains terminology. The distribution
reference retains library/CLI details and advisory instructions. No existing normative statement is moved.

`CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`, `CAP-DOCS-document-search` and `CAP-DOCS-namespaces`
remain the discovery baseline. No schema, ID kind, relation, namespace, UI or artifact handler change is selected.
`PROP-design-document-foundation` consumes the pilot recommendations. The milestone's later runtime/viewer work
owns global/package and viewer verification after representation choices; the pilot makes no such completion claim.

No capability, use case, UX, architecture, ADR, guide or executable asset edit is required by this bounded pilot.
If a trial exposes a contract defect, record its owner and impact as a finding for the Host rather than modifying
that contract or creating an unauthorized follow-up proposal. There are no drafted product screens.
