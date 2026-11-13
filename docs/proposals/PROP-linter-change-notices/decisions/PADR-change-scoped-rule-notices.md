---
id: PADR-change-scoped-rule-notices
title: Change-scoped rule notices and explicit read context
summary: "For contextual rule guidance, we add a nonblocking notice severity and snapshot-bound change evidence with an explicit read surface, to preserve warning meaning, accepting opt-in read-time delivery."
proposal: PROP-linter-change-notices
status: draft
created_at: 2026-11-13
---

# [PADR-change-scoped-rule-notices] Change-scoped rule notices and explicit read context

## 1. Context & Problem Statement

A contextual consideration is useful when its construct changes and does not prove a defect. Warning semantics
and strict rule checks cannot express that distinction. File-target membership cannot distinguish an edited handler
from an unchanged handler in the same file; native host hooks supply no cross-host typed file-read contract.

## 2. Decision Drivers

- Preserve existing warning, INFO, strict, commit-gate and exact-snapshot compatibility.
- Deliver only relevant considerations, including deletion-triggered ones.
- Keep explicit checks deterministic and inspectable, without acknowledgements or repair obligations.
- Bound read-time delivery to an explicit host-neutral surface and transient session lifetime.

## 3. Considered Options

1. Reuse warning: smaller API but a notice-only strict check can fail and warning meaning weakens.
2. Alias INFO to notice: fewer severity names but changes wire/configuration semantics for existing consumers.
3. Add NOTICE, independent change evidence and an explicit read companion: additive, with opt-in delivery cost.
4. Intercept every native read: automatic delivery but requires unsupported host-specific integration and exceeds scope.

## 4. Decision Outcome

Choose option 3 for compatibility and relevant-change targeting.

1. Rule NOTICE findings express consideration without repair, acknowledgement or unresolved-work obligations;
   INFO remains distinct and notice-only checks pass strict mode, gates and lint-clean.
   → `CAP-GOV-rules-engine` severity and finding contract (MUST).
2. Change targeting is independent from severity, uses exact before/after source identities and old/new ranges,
   and omits unavailable evidence rather than scanning historical triggers.
   → `CAP-GOV-evaluation-lifecycle` change-scoped evaluation (MUST).
3. Change-scoped rules are excluded from hygiene and validate affected-construct evidence, including deleted text.
   → `CAP-GOV-rule-authoring` change-scope contract (MUST).
4. The explicit read companion returns changed-file status and bounded hunk context even without matching notices;
   only caller-selected transient sessions suppress identical delivered notice fingerprints.
   → `CAP-GOV-rules-engine` explicit read-context contract (MUST).
5. Gate notice delivery uses NOTICE-level advisories and preserves warning/error behavior.
   → `CAP-GATE-commit-gates` rule-check findings (MUST).

These traces name the intended restating sections after Development, not existing implemented behavior.
No existing accepted ADR is replaced; the current host observer remains unchanged.

## 5. Consequences

Positive: warning meaning and legacy INFO wire values remain stable. Staged and CI results remain independent of
unstaged bytes. Explicit checks never hide a notice because another session saw it.

Negative: a third non-error rule severity remains for compatibility. An agent must call the explicit context
command alongside a read; native reads alone receive no automatic context. Session suppression uses derived local
state and cannot guarantee delivery across a crash between memo commit and host display.

Risk: an overly broad rule-provided semantic span can still produce a noisy notice despite structural overlap.
The representative fixture and authoring review verify unrelated-change suppression. If automatic native-read
coverage becomes a requirement, revisit the host-specific scope in a later direction review before implementation.

## 6. Confirmation

AC-N1 to AC-N9 of `PROP-linter-change-notices` map to rule/evaluator, snapshot, CLI, gate, workflow and memo tests in
`packages/devkit/tests/`. Document rules validate structure; Development code review checks semantic-span relevance.
Planning has not run the future implementation tests.
