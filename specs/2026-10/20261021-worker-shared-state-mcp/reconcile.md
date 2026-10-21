---
reconcile_id: REC-worker-shared-state-mcp
feature: SPEC-worker-shared-state-mcp
status: pending
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-shared-artifacts.md
    resolution: modified
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/development/reference/shared.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconciliation

The shared-artifact capability owns immutable generation identity, local discovery/exclusion, expiry, configuration,
public adapters and transport behavior. MCP runtime defines the fixed bounded_write classification and owning
configuration binding for reads as well as writes. Architecture and package references identify devkit.shared as
a dist area depending only on core/advisory. The glossary registers shared artifact with scope/authority exclusions;
the Host authorized this exact additional file boundary. No scope-registry production behavior changed.

The explicit deferred destination `FB-remote-shared-adapter-follow-up` exists in this unit and remains open for
production remote backend selection and real integration evidence. It is deferred scope, not a direct-fix source.
`PROP-cloud-agent-rendering` retains cloud rendering work. No linked open direct-fix source needs resolution.

The two source guidance assets now require connected project tools before local-orchestrated shared operations.
The Host owns deployment sync because generated projections and .devkit/ writes are outside worker boundaries.

Distribution configuration accepts and templates the shared table. This required a Host-authorized narrow
expansion to distribution/installation/config.py; its existing schema and checkout-local capability sections
are updated in place. Entrypoint derivation was reviewed: broad package/test/guidance candidates are rejected
because they do not belong to each capability. The shared domain directory and existing MCP/core/config
entrypoints identify the actual owners; no broad cross-component declaration was applied.
