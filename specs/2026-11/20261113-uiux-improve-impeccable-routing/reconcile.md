---
reconcile_id: REC-uiux-improve-impeccable-routing
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    resolution: modified
  - file: docs/decisions/2026-11/20261113-impeccable-question-relay.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
    resolution: modified
---

# Reconcile: SPEC-uiux-improve-impeccable-routing

`CAP-DLV-uiux-improvement` rules 10 and 16, use-case extensions 5c/5d/5e and scenarios 15–18 reflect AC-01..AC-08:
native load/continuation, every confirmed answer, read-only questions, source/new-round confirmation, nested-role
fallback, existing permissions and partial-return attribution. The promoted decision has current accepted wording;
the predecessor's exact partial-supersession pointer was written by handoff commit 49326e950da6 and remains intact.
Other run-model, setup, file ownership and acceptance clauses remain authoritative.

The reviewed source entry, orchestration and guide and 11 focused contract tests state the same conditions.
Only one catalog bundle and one capability area change; its Living Spec reflection adds no component. All exact
targets and their changed statements are identified, so the medium self-verification exception applies without an
independent reconcile call. Compare against the branch merge base to include the handoff-written pointer.

No required criterion is deferred. The already-scoped pilot hygiene follow-up remains owned by
`PROP-uiux-improve-bundle-hygiene`. Native Impeccable loading, full relay, nested roles and model obedience remain
unverified best-effort coverage, not omitted required functionality. No runtime, dependency, projection or new
entry doorway is introduced.

Entrypoint derivation proposed the broad bundle source directory and integration test. Both are rejected:
the directory is not the user doorway and the test is verification. Capability and use case retain the existing
`packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md` entrypoint.
