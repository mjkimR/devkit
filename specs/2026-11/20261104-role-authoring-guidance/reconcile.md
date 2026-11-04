---
reconcile_id: REC-role-authoring-guidance
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-shared-role-authoring.md
    resolution: modified
---

# Reconciliation

`CAP-HARN-agent-guidance` section 4.3 reflects the shared instruction's applicability, placement default,
registration exceptions, bounded role loading and host-setting limitations. `ADR-shared-role-authoring` records
the guidance owner and the decision to keep the playbook scope. No runtime or other bundle behavior changes.
`FB-skill-local-role-authoring` is resolved by the instruction, playbook and independent review with passing
existing distribution tests. Entrypoints remain the existing harness doorway files; authoring files are supporting
guidance rather than replacements for those entrypoints.
