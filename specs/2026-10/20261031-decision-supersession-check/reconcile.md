---
reconcile_id: REC-decision-supersession-check
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
---

# Reconciliation: `SPEC-decision-supersession-check`

`CAP-DOCS-document-model` replaces review-only metadata enforcement with the named rule, preserving the index's
graph boundary and semantic review. `CAP-GOV-spec-rules` records the catalog, deployment, severity, alias handling,
material and PADR exemptions, historical pointers, malformed metadata and no-fix boundary. Rule inventory counts
are updated. Existing use cases already invoke the rule engine and need no step change. No architectural invariant,
term or decision changes; the checker enforces the existing decision-writing contract.

## Source feedback

`FB-decision-supersession-consistency-unchecked` is resolved by the delivered rule and verification: 21 deployed
rule tests, 2132 affected tests, lint/type checks, independent review and implementer regression re-verification.
The requested consistency checks are implemented. Metadata autofix was excluded by the agreed intent and is not
deferred required work. No remaining authorized scope is deferred.

## Measurement

At fefc351f, bundle registration contained no decision-supersession checker. The head's seeded inconsistent ADR
pair produces non-fixable relationship findings; valid whole/partial alias pairs produce none. This is a functional
coverage comparison, with no performance claim. Before/after evidence is the baseline manifest and rule fixtures.

## Entrypoint selection

Added the dedicated rule implementation as the document-model doorway. The governance capability already names
its owning governance directory. Rejected receipt, rule-test, bundle-wrapper directory and distribution-test
candidates because they are deployment evidence or tests rather than reading entrypoints.
