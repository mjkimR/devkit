---
id: ADR-bounded-high-effort-review-loop
title: Bounded high-effort review loop
summary: At high, each fresh review round takes every fix since the previous one, findings are fixed together, the loop ends when a round finds nothing or every fix is minor, and persistent, recurring or contested P1s go to the user via worker questions and problems.
proposal: SPEC-high-effort-review-loop
status: accepted
supersedes: ADR-medium-review-delegation
created_at: 2026-10-19
---

# [ADR-bounded-high-effort-review-loop] Bounded high-effort review loop

- **Status**: Accepted
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

`ADR-medium-review-delegation` bounds `medium` delegation and keeps `high` as "code re-review after fixes and
independent reconcile verification". That clause names no round scope, no end and no hand-over, and findings carry no
priority (`CAP-DLV-workflow-envelopes`: `severity` is a free label). This decision defines the `high` loop for code
review, reconcile verification and `high` Planning without changing envelope schemas, stages, checks or gates.

## 2. Decision Drivers

- `high` must end deterministically and stay stricter than `medium`.
- No fix may ship at `high` unseen by a reviewer unless it is provably minor.
- Hand-over uses records that already exist (`worker` questions and problems), not new kinds or keys.
- The finding schema is closed (`issue`, `evidence`, `failure_condition`, `suggested_action`, `resolution`, `waiver`,
  `severity`).

## 3. Considered Options

1. **Fixed round limit**: hand over after two re-review rounds. Rejected: it hands over loops that still converge.
2. **Whole-batch loop with a minor-fix exit** (chosen): each round reviews every fix since the previous round, all
   findings are fixed together, and the loop ends when a round finds nothing or every fix is minor; hand-over when a
   P1 persists to the cap, recurs, or is contested.
3. **Unbounded loop until no finding**: rejected: P3 improvements would keep it running.

## 4. Decision Outcome

Option 2, as specified in `SPEC-high-effort-review-loop` §3.1 to §3.5:

- A fresh reviewer per round, given the earlier findings, the round's diff scope and the effort; round 1 reviews the
  whole change, each later round every fix since the previous one, never a subset.
- The implementer fixes every finding of a round together (P2/P3 may be waived with a reason) and closes the round
  before the next is recorded.
- The next round is skipped only when every fix of the batch meets the four minor-fix conditions (location, nature,
  contract, evidence); those fixes are self-verified. The initial reviewer calls stay mandatory.
- `P1`/`P2`/`P3` with one P1 definition per review kind; the reviewer owns the label and the implementer records it
  unchanged.
- Recurrence is a fixed `recurs:` prefix in `issue`; out-of-scope findings are derived from the round's diff files.
- Round counts survive `devkit workflow return` within a segment.
- The cap (3 rounds after the initial review) only limits further rounds: at the cap round a fully minor batch ends
  the loop, any other batch is a `worker` problem whatever its severity (P2/P3 may be waived with a reason); a
  recurring P1 is a `worker` problem too; a contested P1 still asserted after one counter-evidence round is a `worker`
  question; a session reports either in the conversation and does not integrate. This is not the `exception` stage.

- A P1 the user rules invalid after a hand-over is closed by a waiver citing the `answer` envelope, the only P1
  waiver; a fix the user asks for after a cap or recurrence problem gets one further fresh round outside the cap.
- Round numbers live in a fixed summary marker (`round <N>;`, `closes reconcile-check-<NN>;`), never in new fields.
- Severity is required on every finding at every effort; it has no effect on checks.
- This decision supersedes `ADR-medium-review-delegation`; its `high` clause is replaced by the rules above and its
  other rules are carried over unchanged:
  - Distinct read-only `code-reviewer` and `reconcile-reviewer` contracts. The implementer writes, fixes and resolves
    the Living Spec reflection and `reconcile.md` at every effort; reviewers only return verification results.
  - At `medium`, the initial code review is mandatory for session and Unit paths regardless of change size.
  - Only `medium` Unit-path reconcile verification may omit its initial subagent call, when all affected contracts
    and documents can be identified, agreement with the actual diff can be directly demonstrated, and no unresolved
    contract interpretation or cross-component impact remains. A confirmed no-impact or wording-only reflection may
    qualify; small size alone does not; uncertainty requires the reconcile reviewer. The omission reason and the
    self-verification evidence are recorded in the existing `reconcile-check` envelope.
  - After the initial `medium` review, the implementer verifies fixes and later changes and decides whether to call
    either reviewer again; expanded scope, uncertain correctness or contract interpretation are reasons to call.
    Findings still need evidence of resolution, later verification is attributed to its actual executor, and a
    failed or stale initial call never fulfills the required first review.
  - `low` keeps self-review and a self-checked reconcile.
  - Stage ids, order, entry and exit checks, gates, returns and effort selection are unchanged; required repository
    policies remain binding.

## 5. Consequences

- `high` costs a subagent round per batch that holds a non-minor fix; a batch of trivial fixes closes with recorded
  evidence.
- Reviewer payloads grow by the earlier findings and the round's diff scope.
- Like `ADR-medium-review-delegation`, this decision supplements the verifier assignment of
  `ADR-review-and-reconcile-verification`: `medium` may self-verify the initial reconcile under the stated conditions and
  `high` may self-verify a batch of minor reconcile fixes.
- The `medium` and `low` rules are unchanged in substance; `ADR-review-and-reconcile-verification` keeps holding, since the initial reconcile
  verification at `high` stays independent.
