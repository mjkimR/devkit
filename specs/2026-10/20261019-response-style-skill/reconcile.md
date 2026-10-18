---
reconcile_id: REC-response-style-skill
feature: SPEC-response-style-skill
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/architecture/ARCH-05-4-distribution-components.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconciliation

The manifest contract admits exactly one plain or templated skill entry, renders skill Markdown before validation,
and retains native invocation ownership. Projections expose rendered filenames; synchronization keeps raw override
sources and rendered consumer paths. The quick reference and bundled consumption/resource guides mirror these
contracts. Response-style is a consumer of the same distribution behavior, with unchanged communication policy.

The distribution component description also includes skill rendering, and workspace ownership names raw template
entry paths in override receipts. No architecture-layer change, new story, or deferred implementation remains. Continue in the existing checkout as
a session-to-spec depth increase. Code review and reconciliation inspect uncommitted working-tree changes; no commit
or integration is included in this request. Entrypoint candidates are reviewed for capability ownership before use.
