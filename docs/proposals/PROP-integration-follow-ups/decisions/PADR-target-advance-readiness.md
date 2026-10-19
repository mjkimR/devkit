---
id: PADR-target-advance-readiness
title: Approval tolerates target advances with readiness on the result
summary: The approval shows and records the target SHA at confirmation without requiring it to hold; execution merges later target commits only when the merge is clean, the effective policy is unchanged and readiness passes again on the result commit, within three attempts per call.
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

The third option. `IntegrationContext` gains `result_sha` and `Readiness` binds source, target and result. At
execution the provider must return no reasons and evidence equal to the approved evidence except items it declares
target-bound; devkit-spec declares `TARGET_SHA` and `RESULT_SHA`, evaluates the unit from the source tree (a target
change inside the unit directory is a reason) and runs its CI rules on the result tree with the diff from the current
target. The form shows the target SHA at confirmation and states the conditions under which later target commits are
merged in. If the target moves between building and fast-forwarding, the executor rebuilds at most three times per
call, then refuses with `INTEGRATION_TARGET_MOVED` and nothing changed; `integration_resume` may retry under the same
approval.

## 5. Consequences

- The provider contract changes (released before devkit-spec updates, as today).
- Readiness runs up to four times per integration; CI rules cost is bounded by the diff.
- The approval's meaning changes from "this target" to "this source onto the target as it will be, under these
  conditions"; `CAP-INT-mcp-services` section 2 is rewritten accordingly.
