---
id: PLAN-partial-adr-supersession-statements
spec: SPEC-partial-adr-supersession-statements
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-partial-adr-supersession-statements` Structured partial-supersession statements for ADRs

## 1. Architecture Overview & Impact
- Target Area: capabilities/documents/
- Target Docs Blueprint: `PROP-partial-adr-supersession-statements-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/`
- `packages/devkit-docs/src/devkit_docs/features/governance/usecases/decision_supersession.py`
- `packages/devkit-docs/src/devkit_docs/features/documents/`
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md`
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md`
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/decisions/README.md`
- `packages/devkit-docs/tests/`
- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`
- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/post-handoff.md`
- `packages/devkit-spec/tests/`
- `.devkit/architecture.toml`
- `docs/capabilities/documents/CAP-DOCS-document-model.md`
- `docs/capabilities/documents/CAP-DOCS-document-lookup.md`
- `docs/capabilities/governance/CAP-GOV-spec-rules.md`
- `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`
- `docs/usecases/documents/UC-find-the-right-documents.md`
- `docs/architecture/ARCH-05-2-components.md`
- `docs/decisions/`
- `docs/proposals/`

### Excluded Boundaries:
- `packages/devkit/src/devkit_agt/features/rules/`
- `packages/devkit-viewer/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
