---
reconcile_id: REC-high-effort-review-loop
feature: SPEC-high-effort-review-loop
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-bounded-high-effort-review-loop.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: waived
    rationale: "It defines no plan-accept request content: the request and its gap report live in the sdd-proposal body and rule 15 of CAP-DLV-delivery-workflows, where the missing-scout gap was added. Its effort-hint and handoff rules are unchanged."
  - file: docs/decisions/2026-10/20261016-medium-review-delegation.md
    resolution: modified
---

# Reconcile: `SPEC-high-effort-review-loop`

## Reflected

- `CAP-DLV-delivery-workflows`
  - Rule 7 (problem rule): the `high` hand-over joins the stop reasons: a batch not minor at the cap round or a
    recurring P1 is a problem, a P1 still contested after one counter-evidence round is a `worker` question; the
    P1 waiver after a user ruling, the one further round outside the cap, the session path, and that none of it is
    the `exception` stage.
  - Rule 15: the `high` review loop (fresh reviewer per round, whole batch, round inputs, closing record, minor-fix
    exit, mandatory initial calls, `round <N>;` marker, cap of 3 surviving `devkit workflow return`), P1-P3 severity
    on every `review`, `reconcile-check` and `challenger` finding, session reclassification advice, `scout` from
    `devkit spec refs` in `high` Planning and the `plan-accept` gap report for a missing `scout`. The deciding ADR
    reference moves from `ADR-medium-review-delegation` to `ADR-bounded-high-effort-review-loop`; the `medium` and
    `low` sentences are unchanged. Rule 15 also states the out-of-scope and `Decision needed:` exclusions.
  - Section 4.5: the `reconcile-check` row names a `high` minor-fix self-verification and the round marker; the role
    return fields include `severity`.
  - Summary: names the bounded high-effort loop and P1-P3 severity.
- `CAP-DLV-workflow-envelopes`: the example severity is `P2`, and the severity bullet states that the engine validates
  nothing beyond a non-empty string while the `spec` bundle requires and defines the levels. No schema change.
- `ADR-medium-review-delegation`: frontmatter only, set in the integrate stage: `status: superseded` and
  `superseded_by: ADR-bounded-high-effort-review-loop`, so the supersede link runs both ways; the body stays as
  accepted (`reconcile-check-01` finding 1).
- `ADR-bounded-high-effort-review-loop`: promoted by the handoff commit on this branch; its status (`accepted`) and
  consequences match the implementation, so this turn did not edit it.

## Not affected

- `docs/architecture/`: no module, import or package boundary changed (bundle prose and one test file).
- `docs/development/reference/` and package READMEs: none restates the effort procedure (searched for `re-review`,
  `high` with `effort` or `review`).
- `docs/stories/`: no story changes; the user stories in `spec.md` stay inside `US-route-development-intent` and
  `US-incubate-and-hand-off-a-proposal` as they stand.
