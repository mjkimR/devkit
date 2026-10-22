---
reconcile_id: REC-hygiene-reliability
status: resolved
targets:
  - file: docs/capabilities/gate/CAP-GATE-commit-gates.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/development/reference/rules-library.md
    resolution: modified
---

# Reconciliation: Hygiene reliability

`CAP-GATE-commit-gates` defines automatic per-stage fallback preservation, validation and repair for active entries,
while explicit installs replace their fallbacks. `CAP-DLV-workflow-envelopes` defines optional descriptive severity,
Git CLI revision resolution, invalid-revision errors and portable composition/loading outside that boundary.

The rules command reference links the extracted library reference, and `CAP-GOV-rule-authoring` points its library
and test links at the moved sections. The executable example test reads the new reference. The source spec envelope
reference and synchronized installation receipt mirror the revised metadata and scope behavior.

No architecture, advisory API or user-story contract changes are needed: the work stays within existing gate and
workflow responsibilities. The three selected feedback items are promoted to `SPEC-hygiene-reliability`; other
backlog items remain outside its scope. Tests use dedicated files to avoid extending unrelated test collections.

Entrypoint derivation was reviewed per document: gate declares its two hook modules, envelopes declares its CLI and
composition/model modules. Cross-module pairs, tests and the rule-authoring link-only target were excluded.
