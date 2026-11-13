---
reconcile_id: REC-adaptive-orchestration
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md
    resolution: modified
  - file: docs/usecases/delivery/UC-advance-an-idea.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/development/reference/adaptive.md
    resolution: modified
  - file: docs/decisions/2026-11/20261113-coordinator-led-adaptive-delegation.md
    resolution: modified
  - file: docs/decisions/2026-11/20261106-skill-local-swarm-roles.md
    resolution: modified
---

# Living Spec reflection

- `CAP-DLV-adaptive-development` rules 12/13 and assignment payloads describe active coordinator-led delegation,
  narrowed child authority and the retained result checks. Bundle entry, constitution, references and swarm roles
  contain no fixed child-depth or child-budget requirements.
- `CAP-DLV-adaptive-assignments` rules 4/5, refusal list and write-scope contract match the ancestor exemption and
  immediate-parent authority checks. Deeper chains retain recursive bottom-up closure, tested alongside scope/commit
  widening and sibling/unrelated overlap refusals. Record schema, flags and verification checks are unchanged.
- `UC-advance-an-idea` includes useful delegation in the main flow, retains role-lead authority and aggregate checks,
  and removes the obsolete capacity fallback. `CAP-HARN-agent-guidance` describes the same coordinator responsibility.
- The adaptive command reference no longer advertises a depth refusal. Its legacy error class remains importable,
  without an emitted refusal.
- `ADR-coordinator-led-adaptive-delegation` partially supersedes only the fixed depth/child-budget clauses of
  `ADR-skill-local-swarm-roles`; the reciprocal pointer retains the historical decision.

No architecture or glossary change is needed: existing packages, terms, source ownership and feature edges remain.
Existing capability/use case entrypoints already identify the changed bundle, CLI and orchestration reference.
No required work is deferred. Downstream installation, release and publication are outside this Unit's scope.
