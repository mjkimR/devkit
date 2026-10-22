---
reconcile_id: REC-feedback-review-auto-proposal
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation

The delivery workflow contract mirrors the source review-loop criterion: the same failure condition remains or
returns, including incomplete fixes. A distinct introduced failure is new; location, topic or causality alone does
not establish recurrence. Existing scope exclusions, severity, self-verification and escalation conditions remain.

`FB-recurs-marker-on-fix-introduced-findings` is directly resolved: independent code review checked all acceptance
scenarios without findings, and spec lint/types plus 1,111 affected tests passed. This is a definition clarification,
not a new marker or a policy exception; the existing bounded-review ADR remains unchanged.

The separately requested automatic-integration work is tracked by `PROP-policy-authorized-integration`, a draft.
Its source `FB-auto-integration-dispatch` is promoted, not resolved; no runtime integration policy changed.
Entrypoint candidates are reviewed against the existing capability ownership; no unrelated entrypoints are added.
