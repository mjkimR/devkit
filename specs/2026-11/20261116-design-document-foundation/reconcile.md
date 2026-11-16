---
reconcile_id: REC-design-document-foundation
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    resolution: modified
  - file: docs/architecture/README.md
    resolution: modified
  - file: docs/decisions/2026-11/20261116-documentation-ownership-and-linked-design-entries.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/designs/distribution-transactions.md
    resolution: modified
  - file: docs/designs/distribution-transactions/file-directory-replacement.md
    resolution: modified
  - file: docs/materials/2026-11/20261116-design-document-foundation/development-evidence.md
    resolution: modified
---

# Foundation reconciliation

## Contract and implementation agreement

- `CAP-DOCS-documentation-ownership` is the unique common authority: §3.1 routes all twelve responsibility cases,
  §3.2 distinguishes system ARCH responsibility from local mechanism, §3.3 selects useful linked ID-free entries.
  Generic living-spec/architecture instructions implement these clauses in consumers; they introduce no competing
  matrix or repository IDs. The optional template uses the existing templates asset and is delivered byte-exactly.
- Architecture overview clarifies retained system interactions, deployment, constraints, quality/risk and boundaries
  with meaning, guarantees, goals, rationale and recovery composition. No architectural runtime promise is changed.
- Accepted `ADR-documentation-ownership-and-linked-design-entries` retains its decision and now cites actual
  restatement sections and strength rather than planned IDs. Its required global/package trials are executed.
- `CAP-DIST-sync-and-transactions` gains only the question-specific ordinary route. All eligibility, safety,
  recovery/advisory and readiness authority stays there. No journal absence implies readiness, no recovery executed.
- The two maintained design files adapt historical pilot mechanism into current explanation, with independently
  useful overview/detail and inspected transaction source. Pilot/domain/operations materials are byte-unchanged.
- Development evidence records actual F1–F6 trials, Planning before/Development after qualitative comparison,
  fixture setup failure followed by isolated-root success, corrected exact-template test mismatch, passing final
  checks, emulated isolation and limits. No required failure is waived or deferred.

No user goal/scenario or UX interaction changed; no use case/UX reflection is needed. No new named domain concept
was introduced, so glossary remains unchanged. Runtime, index, Kind, namespace grammar and feature dependencies
remain unchanged. The authorized existing distribution test mirror adds the optional template expectation and
consumer-byte/ID-free checks, preserving all prior assertions. Receipt is the sole tracked generated sync output.

## Deferred work destinations

Existing `PROP-domain-model-documents` retains domain homes and unsupplied discovery; ~~`PROP-operations-documents`~~ (source Git `534ad541e9d1e87beffa6bbc4f1afa95c71f6106`)
retains operations homes and unsupplied discovery; `PROP-design-document-lifecycle` retains lifecycle integration;
`PROP-design-document-viewer` retains viewer verification. All four remain existing draft destinations, confirmed
by proposal list; their scopes and restart criteria remain unchanged. This implementation fulfills F1–F6 rather
than exporting required work there. `FB-runtime-journal-ordering` retains the unrelated journal-ordering ambiguity.

## Entrypoints and verification

No runtime command/API changed. Entry-point derivation is reviewed separately; generic instructions/templates and
an integration test are not runtime doorway code, while the transaction capability's existing entrypoints remain.
Independent Code Reviewer passed actual db9d230..386c6b0 scope with no findings, global route/source/link audit,
source-asset byte/generic checks, sync and whitespace verification. It audited committed package/consumer evidence
without rerunning those readers. Review provenance distinguishes executed checks from caller-supplied native tests.
Separate Reconcile Reviewer passed this complete reflection and all seven targets without findings.
Entrypoint derivation returned eight candidates (both instructions, template and integration test for both CAPs);
all were rejected as non-runtime doorways. No entrypoint was written.
