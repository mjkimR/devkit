---
id: PLAN-partial-adr-supersession-statements
spec: SPEC-partial-adr-supersession-statements
---

# Technical Plan: `SPEC-partial-adr-supersession-statements` Structured partial-supersession statements for ADRs

## 1. Constitution & Invariant Review

No invariant changes. `ADR-partial-supersession-statements` fixes the representation of the replaced scope required by `ADR-decision-ledger`. Feature edges stay unchanged. The accepted two migration scope decisions are retained.

## 2. Architecture Overview & Impact
- Target Area: capabilities/documents/
- Target Docs Blueprint: `PROP-partial-adr-supersession-statements-target` (Living Spec targets for this plan and reconcile.md)

## 3. Component & Interface Design

A shared pure models/supersession reader extracts visible statement/pointer starts, then takes source text through the next blank line, item or heading. It preserves inline source and normalizes whitespace only for equality. Governance checks statements for ADRs and PADRs, and deduplicates pointer mismatches per canonical pair with target-sensitive locations. A typed BaseUseCase coordinates the index and text reads for the new CLI command. Handoff plans pointers from promoted text before writes, eliminating summary fallback.

`docs supersession ID` returns id, supersedes, superseded_by and notices; each record carries id/path/status/scope/line/text. ARGUMENT_INVALID rejects another kind; existing lookup errors reject unresolved or duplicate IDs. Whole scope requires reciprocal superseded metadata.

### Failure and migration

Missing handoff statements fail SPEC_PROPOSAL_INVALID before writes. Rule additions are non-fixable errors. Before ADR migration the changed rule measures all current pairs. Migration keeps existing clauses, splits mixed clauses from replacement statements and records every pair in reconcile.md. Open PADRs receive statements only.

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

## 6. Verification & Test Plan

- Reader unit tests: masking, wrapped source, inline code differences and item boundaries (AC-03/04).
- Deployed rule tests: missing/stray/duplicate/empty, alias canonicalization, PADR exemptions and all target selections (AC-02/03/04/06).
- Handoff integration tests: statement copying, no-write failure, reference rewriting, placeholder compatibility (AC-05).
- CLI integration tests: both directions, whole scope, aliases, error codes and JSON (AC-07).
- Guidance assertions and whole repository rules prove AC-01/08/09; pair inventory and wording diff review prove AC-06.
- Run just lint-check docs/spec, just check docs/spec, just test-affected --base 2999c21d4e2bc26e4c6633124afc11c4e50e9144, and whole rules. Host collects fixed-SHA E2E and landed verification.
