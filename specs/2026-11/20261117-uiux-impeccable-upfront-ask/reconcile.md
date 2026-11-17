---
reconcile_id: REC-uiux-impeccable-upfront-ask
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    resolution: modified
  - file: docs/decisions/2026-11/20261117-impeccable-upfront-ask.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
    resolution: modified
formal_docs:
  design: "none: instruction text of one opt-in catalog bundle; no mechanism, persisted format or component changes"
  domain: "none: no domain term or object introduced or renamed"
  operations: "none: no runtime, installation or operational procedure changes"
---

# Reconcile: SPEC-uiux-impeccable-upfront-ask

`CAP-DLV-uiux-improvement` rule 15 now requires the first-round Impeccable question (with installation state), the
skip when the request or an exact prior instruction decides, and non-selection on silence (AC-01..AC-03). Rule 10
keeps the unavailable path that AC-04 reuses. `UC-improve-an-interface-and-user-flow` step 1 recovers or asks the
Impeccable choice and extension 3c accepts the step 1 answer as selection. `ADR-impeccable-upfront-ask` records the
decision and supersedes in part `ADR-impeccable-session-authority`, whose exact pointer was added (AC-05).

The bundle skill, orchestration reference and README state the same contract; the focused test asserts it, and the
bundle cites no authoring-repository document ID. At low effort the Developer verified the reconcile; one bundle and
one capability area change and every changed statement is identified.

No required criterion is deferred and no source feedback is addressed. Live obedience to the question remains review
only, as `ADR-impeccable-upfront-ask` Confirmation states.

Entrypoint derivation proposed the bundle source directory and the integration test for both documents. Both are
rejected: the directory is not the user doorway and the test is verification. The existing `SKILL.md` entrypoint
stays.
