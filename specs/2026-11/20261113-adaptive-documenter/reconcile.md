---
reconcile_id: REC-adaptive-documenter
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
---

# Reconciliation: SPEC-adaptive-documenter

CAP-DLV-adaptive-development names the installed documenter overlay, swarm-worker execution, source-bound document assignments, conflict reporting and Host context/integration ownership. The shared-interface exception is retained.

The package README documents invocation inputs. No CLI, architecture dependency, product use-case step or ADR decision changes; existing document timing and role authority apply unchanged.

Entrypoints remain the existing adaptive-dev SKILL.md and swarm-worker contract. Reject role and reference candidates because they are subordinate assets reached from those existing entrypoints; reject README and tests as non-entrypoints.
