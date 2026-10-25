---
reconcile_id: REC-five-subagent-levels
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/decisions/2026-10/20261025-five-subagent-levels.md
    resolution: modified
  - file: docs/decisions/2026-10/20261025-subagent-level-projection.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconcile: `SPEC-five-subagent-levels`

## Delivered behavior

The distribution contracts define five exact presets, inherited default behavior, strict obsolete-name rejection,
field omission and existing project override/reset semantics. Antigravity compact selects Flash; the other four
built-in presets inherit both settings without warning or Pro substitution. Explicit config validation stays strict.
The delivery contract and source-role tests pin compact only on scout. The accepted successor ADR preserves
existing distribution boundaries while replacing the cardinality, effort pairs and scout default. The previous
ADR retains its historical body and is marked superseded with the reciprocal replacement link.

No transport or use-case flow is added. Existing capability entrypoints remain the resolver and inventory doorways.
No required scope is deferred; no open source feedback is fixed by this unit. Native execution/account access
remain unverified. Entrypoint derivation produced broad distribution/bundle directories and test paths; those candidates were
rejected because the existing resolver/inventory doorway files remain accurate. No entrypoints changed.
Host owns sync of generated projections and tracked deployment artifacts before integration.
