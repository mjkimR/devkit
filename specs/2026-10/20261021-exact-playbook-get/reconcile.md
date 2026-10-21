---
reconcile_id: REC-exact-playbook-get
feature: SPEC-exact-playbook-get
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/architecture/ARCH-05-4-distribution-components.md
    resolution: modified
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/architecture/ARCH-08-cross-cutting.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/decisions/2026-10/20261021-external-playbook-execution.md
    resolution: waived
    rationale: The accepted ADR was already promoted and committed by proposal handoff; this Development implements its decision without changing the accepted record.
  - file: guides/install/new-repository.md
    resolution: waived
    rationale: The installation guide describes generated skill deployment and projection ignore paths, not invocation conditions; its existing statements remain accurate.
---

# Reconciliation: `SPEC-exact-playbook-get`

`CAP-DIST-context-and-playbooks` now owns the full exact-selector, JSON result, source identity,
context, error-order, snapshot and external-execution contracts. The manifest kind description
and synchronization reader list include exact retrieval. Architecture names the service and
explicit exact invocation; the quick reference lists the command. Shipped consumption and
resource-kind instructions and generated playbook skill source mirror those boundaries.
`ADR-external-playbook-execution` already records the policy decision.

The final implementation preserves runtime receipt validation but normalizes the stale-render
exception instance to exit 2 for exact retrieval, as the feature contract requires. The shared
error code and advisory remain intact. CLI selector validation precedes workspace resolution.

No new domain term, story, dependency, scheduler or execution state was introduced. Existing
search contracts, content-package deployment and installation guidance remain valid. The
constitution's search-only rule still applies to discovery and does not exclude exact retrieval.
No explicitly linked open direct-fix feedback source requires disposition. No required scope
or concrete follow-up from this feature was deferred; scheduling remains the existing milestone's
external-system responsibility, not new retained implementation work.

Entrypoint review keeps the concrete installation/playbook_get.py service for the changed
context/playbook capability, alongside its existing reading/status entries. Broad distribution
and test-directory candidates are not selected: the task boundaries include more than this
capability owns. Manifest and synchronization documents receive wording-only reflection, so
no new code entrypoints are added to those documents.
