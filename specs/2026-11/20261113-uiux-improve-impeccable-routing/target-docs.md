---
id: PROP-uiux-improve-impeccable-routing-target
title: Target Living Spec for capability-gated Impeccable question relay
summary: "Maps prospective capability, use-case and partial-ADR updates to the existing bundle guidance and integration test, preserving explicit user answers and host-capability fallback."
status: draft
proposal: SPEC-uiux-improve-impeccable-routing
created_at: 2026-11-13
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
---

# [PROP-uiux-improve-impeccable-routing-target] Target Living Spec for capability-gated Impeccable question relay

These prospective changes restate `ADR-impeccable-question-relay` after implementation. Current contracts remain
in force during Planning. This mapping extracts the decisions and cases in `SPEC-uiux-improve-impeccable-routing`;
it adds no scope or decision. Native Impeccable live checks remain unverified and best-effort under the user's
explicit personal-project direction.

## 1. Capability: CAP-DLV-uiux-improvement

- Rule 16: admit the proposal's two-phase relay only after native loading and same-child continuation are observed
  for the actual host/project. Phase 1 is read-only; every answer including each source-cited pre-fill receives
  explicit user confirmation before the same child writes. Additional questions or relevant source changes stop
  dependent writes and return to confirmation.
- Rule 16: `shape`/`critique` also need the nested-role capabilities their loaded command requires. Unavailable or
  unverified capabilities, lost continuation or unavailable native loading route to the user-operated session.
- Rule 10: load-failure reports state observed current-project enablement/native skill availability and the concrete
  blocker. Cache-file reads are not a sanctioned loading route.
- Rules 15, 17, 18 and 19: preserve user-selected invocation, recorded-base acceptance, context-file ownership,
  explicit `PRODUCT.md`/`DESIGN.md` direction, setup authority and qualified reporting. Preserve `live` exclusion.
- Rule 3 and workflow preconditions: use the preceding run-model's landed result; this proposal changes no delivery
  authority. Keep independent installation and add no runtime dependency or new record kind.

## 2. Use case: UC-improve-an-interface-and-user-flow

Extend delegated-session extension 3c and its examples with the complete question packet and confirmation before
same-child continuation. Add negative examples for omitted pre-fills/additional questions, native-load failure,
lost continuation or changed relevant source facts, unavailable nested roles, context-file permission and partial
writes. Existing return acceptance, stale-document reporting and user-requested setup/cleanup remain.

## 3. Decision: partial supersession

Promote `ADR-impeccable-question-relay` to ADR-impeccable-question-relay under the existing `docs/decisions/`
parent; use the handoff-returned path rather than inventing a dated filename. Add only this exact pointer to
`ADR-impeccable-session-authority`, which stays accepted:

> Superseded in part by ADR-impeccable-question-relay: Decision Outcome clause restricting fresh children to answer-free refinement and routing every interactive command to a user-operated session.

The new ADR's supersession statement repeats the clause text. Native skill loading, permissions and all other
in-force clauses remain. Follow the preceding run-model's landed changes without overwriting them.

## 4. Source and verification mapping

| Existing path | Prospective edit |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md` | Entry routes selected Impeccable work through capability-gated relay or user-session fallback |
| `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/references/orchestration.md` | Native-load checks, read-only question packet, every-answer confirmation, same-child continuation, nested-role and state-change fallbacks, qualified return |
| `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md` | User-facing route and project-enablement troubleshooting; no cache workaround as a supported path |
| `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py` | Contract assertions for the relay and fallback plus retained authority/ownership assertions |

New source modules, packages, feature edges and test tiers are out of scope. Distribution/projection outputs implied
by a selected bundle-source edit are handled by the existing sync contract during Development, not authored here.

## 5. Acceptance and verification cases

| ID | Given / When | Expected result and check |
| --- | --- | --- |
| AC-R1 | Native skill load and same-child continuation are observed, and the user selects relay | Read-only question phase, every answer confirmed, then same-child writing phase; instruction review and contract assertions |
| AC-R2 | Only gaps are answered, one pre-fill is omitted, or an extra upstream question appears | Dependent writes wait for explicit user answers; packet scenario review and contract assertions |
| AC-R3 | Native loading fails or the plugin is unavailable in the consumer project | Report observed enablement/availability, keep cache reading outside sanctioned routes, use user-session fallback; negative scenario and assertions |
| AC-R4 | Same-child continuation is unavailable, state is lost or relevant brief facts changed | No guessed resume; fallback or refreshed confirmation before writes; negative scenario review |
| AC-R5 | `shape` or `critique` requires nested roles that the child lacks | User-session fallback and limited-coverage report; no claim that inline work ran the roles |
| AC-R6 | A confirmed answer implies `PRODUCT.md` or `DESIGN.md` changes without explicit file permission | Do not authorize those writes; existing rule 19 remains; assertions and brief scenario review |
| AC-R7 | A relay returns changes or partial execution | Existing base comparison, edit-list acceptance and qualified reporting still apply; retain existing tests |
| AC-R8 | Review requests native Impeccable behavior on Claude Code and Codex | Record both live checks as unmet until performed; assertions and continuation probe are not end-to-end evidence |

Development runs the bundle integration test and required repository lint, types and affected tests. Review distinguishes
text-contract assertions and scenario review from model obedience, plugin loading and live interaction. No live
support or performance improvement is claimed from these checks. `dev_effort: medium` remains appropriate for this
instruction/contract change; Planning stays high because the direction revises an accepted authority contract.
