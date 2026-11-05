---
id: PROP-ux-design-exploration-target
title: Target Living Spec Structure for PROP-ux-design-exploration
summary: "Planned UI/UX improvement capability, use case, bundle layout and installation guidance for the explicitly invoked uiux-improve skill."
status: draft
proposal: SPEC-ux-design-exploration
created_at: 2026-11-05
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md
  - file: packages/devkit-catalog/README.md
  - file: guides/install/bundle-recommendations.md
---

# UI/UX improvement target documents

This blueprint declares prospective paths. New document IDs below are plain text until Development creates them.
If the handoff date changes the promoted ADR path, update this target before reconciliation.

## 1. Capability

Create CAP-DLV-uiux-improvement to own explicit invocation, proportionate inspection and optional independent
roles, implementation through the consumer workflow, actual usage checks and qualified completion. State local
role guidance as behavioral constraints; no filesystem isolation, team superiority or aesthetic-quality guarantee
is claimed. Cross-link the capability with the use case through frontmatter.

## 2. Use case

Create UC-improve-an-interface-and-user-flow for a user seeking interface or flow improvement. Cover target
recovery, inspection, optional perspectives, coherent design, implementation under existing authority and
verification/reporting. Extensions cover review-only requests, missing artifacts, blocked workflow approvals,
unavailable interaction tools and skipped delegation. No mandatory document, alternative count or validation
program is part of the main path. This delivery authors no product screen or UX object register.

## 3. Structure and decision

Update `ARCH-05-2-components` §1.1 to place the opt-in content-only bundle at
`devkit_catalog/uiux_improve/bundle/` with its entry and local roles. Preserve the existing runtime dependency
graph and other bundle ownership.

Promote `ADR-uiux-improvement-workflow-boundary` at handoff. The capability will restate its explicit invocation,
local-role and existing-workflow clauses. The planned ADR path assumes handoff on 2026-11-05; use the actual
promoted path if it differs.

## 4. Consumer and package guidance

Update `packages/devkit-catalog/README.md` with the `uiux-improve:core` row, selection command, overall improvement
goal, optional roles, existing-workflow boundary and invocation requirement. Keep installation possible with
existing dist/catalog distribution; no spec or docs dependency is required by the skill itself.

Add a row to `guides/install/bundle-recommendations.md` for users requesting an explicitly invoked UI/UX improvement
entry. Selection deploys assets and never starts product work or changes development approach. No always-loaded
pointer, source bundle dependency, schema change or generated document is planned.
