---
id: PADR-target-advance-readiness
title: Approval tolerates target advances with readiness on the result
summary: The approval shows and records the target SHA at confirmation without requiring it to hold; execution merges later target commits only when the merge is clean, the effective policy is unchanged and readiness passes again on the result commit, in one build per call.
proposal: PROP-integration-follow-ups
status: draft
created_at: 2026-10-19
---

# [PADR-target-advance-readiness] Approval tolerates target advances with readiness on the result

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

`_validate` requires the provider's evidence to equal the approved evidence before the merge, and evidence binds the
exact source and target SHAs; `validate_finish` requires the target to still point at the approved SHA. The
devkit-spec provider runs CI rules on the source tree, so when the target moved the tree that lands is never checked.
Repeated confirmations can be overtaken again on a busy base.

## 2. Decision Drivers

- One confirmation per change; never a broader authority than the form showed.
- What lands is checked; a failure changes nothing on the target.
- Bounded work per call.

## 3. Considered Options

- Keep exact target binding (a new confirmation per advance).
- Bind the target at confirmation and accept any later target without re-checks.
- Show and record the target at confirmation, accept later targets only when the merge is clean, the effective
  policy is unchanged and readiness passes again on the result commit.

## 4. Decision Outcome

The third option. The request stays immutable with the confirmation target; an execution context (approved
context plus build target and result SHA) goes to the provider, guards and cleanup, and the latest build is kept
outside the digest. Every build target must descend from the confirmation target, and the base must still point at
the build target immediately before the fast-forward (else `INTEGRATION_TARGET_MOVED`). The provider must return no
reasons and evidence equal to the approved evidence except the codes it declared target-bound at confirmation (the
declared set is digested); devkit-spec declares `TARGET_SHA` and `RESULT_SHA`, evaluates the unit from the source
tree, binds its `[tool.spec]` policy through a source-bound `SPEC_POLICY` item and runs its CI rules on the result
tree. `prepare` still requires the source to contain the target, so only advances after it are tolerated. Tests are not re-run on the result:
only the CI rules run on it, and the form and the integration report say that tests and review ran on the source
only (user decision). One build per call (no in-call retry); the approval tolerates target advances only within the
integrate call that asked for it (user decision): `integration_resume` continues only onto the last build target, and
a later target needs a new confirmation.
Recovery: the base containing the latest result means merged, equal to the last build target means not merged,
anything else is stale or ambiguous.

## 5. Consequences

- The provider contract changes (released before devkit-spec updates, as today).
- Readiness runs twice per integration (prepare and the build); CI rules cost is bounded by the diff.
- A semantic break that no CI rule catches can land after a clean merge of a later target; main's own CI finds it.
- The approval's meaning changes from "this target" to "this source onto the target as it will be, under these
  conditions, within one call"; `CAP-INT-mcp-services` section 2 is rewritten accordingly, and Development updates
  the exit condition of `MS-multi-host-native-integration` to the same binding (user decision).
