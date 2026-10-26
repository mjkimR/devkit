---
id: PLAN-table-driven-document-kinds
spec: SPEC-table-driven-document-kinds
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-table-driven-document-kinds` Table-driven document kind definitions

## 1. Architecture Overview & Impact
- Target Area: documents/
- Target Docs Blueprint: `PROP-table-driven-document-kinds-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/features/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/`
- `packages/devkit-spec/tests/`
- `docs/capabilities/documents/`
- `docs/capabilities/governance/`
- `docs/architecture/`
- `.devkit/managed/spec/`
- `.devkit/installation.json`

### Excluded Boundaries:
- `New document kinds`
- `A plug-in or configuration extension point for document kinds`
- `Changes to document IDs, paths, rule codes or messages`
- `The viewer (link-prefix drift is FB-viewer-link-prefixes-drift; UX viewer support is PROP-ux-documentation)`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
