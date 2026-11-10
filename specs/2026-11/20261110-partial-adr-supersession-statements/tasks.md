---
id: TASKS-partial-adr-supersession-statements
spec: SPEC-partial-adr-supersession-statements
plan: PLAN-partial-adr-supersession-statements
---

# Task Breakdown: `SPEC-partial-adr-supersession-statements` Structured partial-supersession statements for ADRs

## Phase 1: Implementation
- [x] **Task 1.1**: Shared statement reader, rule, handoff, lookup, guidance and ledger migration with focused tests
  - **_Boundary**: .devkit/installation.json (sync output), packages/devkit-docs/src/devkit_docs/cli.py, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/, packages/devkit-docs/src/devkit_docs/features/governance/usecases/decision_supersession.py, packages/devkit-docs/src/devkit_docs/features/documents/, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/decisions/README.md, packages/devkit-docs/tests/, packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py, packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/post-handoff.md, packages/devkit-spec/tests/, .devkit/architecture.toml, docs/capabilities/documents/CAP-DOCS-document-model.md, docs/capabilities/documents/CAP-DOCS-document-lookup.md, docs/capabilities/governance/CAP-GOV-spec-rules.md, docs/capabilities/delivery/CAP-DLV-proposal-planning.md, docs/usecases/documents/UC-find-the-right-documents.md, docs/architecture/ARCH-05-2-components.md, docs/decisions/, docs/proposals/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09_
  - **Verification**: `just test-affected --base 2999c21d4e2bc26e4c6633124afc11c4e50e9144`, `just rules-check`, lint and types
