---
reconcile_id: REC-retire-legacy-integration-provider-key
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md
    resolution: modified
  - file: docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: packages/devkit/README.md
    resolution: modified
---

# Reconciliation: `SPEC-retire-legacy-integration-provider-key`

`CAP-INT-mcp-services` §5 now states that `[integration]` MAY be absent or an empty table and accepts no keys: the
retired readiness-provider key `provider` raises `INTEGRATION_CONFIG_INVALID` with a fix to delete it, and any other
key or a non-table value raises the same code with a fix to remove it (AC-01, AC-02, AC-03). `CAP-DLV-project-policy`,
`CAP-DLV-sdd-baseline-adoption` and `UC-adopt-sdd-from-adaptive-development` drop the "legacy provider is ignored"
statements; the use case keeps its adoption steps, which need no provider selection. The integration quick reference
and the devkit-agt README match: the README integration row lists no readiness providers (AC-04). The AC-04 `rg`
prints nothing.

No ADR changes: `ADR-post-merge-verification` already retired the readiness provider, and this unit removes only the
leftover reader. devkit-dist `RESERVED_TABLES` and `docs/development/reference/distribution.md` are unchanged by
Non-Goal 2. No glossary term was introduced or renamed. No work was deferred and no source feedback was assigned.

The devkit-spec delivery fixture, the SDD baseline scenarios and the smoke integration fixture stopped writing the
retired key under the Host-authorized scope extension of Task 1.1; they are tests, not Living Spec.

Entrypoints are unchanged: the documents changed only in wording about the retired key, and their existing doorways
(the integration service and CLI) still hold, so no derived pair was applied.
