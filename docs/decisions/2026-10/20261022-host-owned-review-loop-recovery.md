---
id: ADR-host-owned-review-loop-recovery
title: Bounded high-effort review loop with Host-owned recovery
summary: "For the high-effort review loop, we keep capped whole-batch rounds and hand a capped, recurring or contested P1 to the Host as a worker problem it recovers within the authorized scope without a user approval gate, to end loops without user waits, accepting that the Host judges contested findings."
status: accepted
created_at: 2026-10-22
supersedes:
  - ADR-bounded-high-effort-review-loop
---

# [ADR-host-owned-review-loop-recovery] Bounded high-effort review loop with Host-owned recovery

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: the `spec` bundle (`skills/spec/references/review-loop.md`,
  `skills/spec/references/effort.md`), `capabilities/delivery/` (`CAP-DLV-delivery-workflows`,
  `CAP-DLV-workflow-envelopes`), `ARCH-04-delivery-strategy`

---

## 1. Context & Problem Statement

`ADR-bounded-high-effort-review-loop` defined the `high` loop for code review, reconcile verification and `high`
Planning, and handed a P1 the implementer contests to the user as a `worker` question; a P1 the user then ruled
invalid was closed by a waiver citing the `answer` envelope. The shipped `spec` skill reference `review-loop.md`
(section 4, "Bounded recovery") instead makes a contested P1 a `problem` for the Host, lets the Host own recovery
within the authorized goal, scope and constraints, and adds no user approval gate. The user decided that the shipped
rule holds. Stages, checks, gates and envelope schemas are unchanged by either rule.

---

## 2. Decision Drivers

- `high` ends deterministically and stays stricter than `medium`.
- No fix ships at `high` unseen by a reviewer unless it is provably minor.
- Hand-over uses records that already exist (`worker` problems and `resolution` envelopes), not new kinds or keys.
- The Host already holds authority within the approved scope (sequencing, workers, fixes); the user is asked only
  for what changes the agreement.
- The finding schema is closed (`issue`, `evidence`, `failure_condition`, `suggested_action`, `resolution`, `waiver`,
  `severity`).

---

## 3. Considered Options

### Option 1: Whole-batch loop with Host-owned recovery (Selected)
- **Overview**: the loop of `ADR-bounded-high-effort-review-loop`, with every hand-over, the contested P1 included,
  recorded as a `worker` problem the Host recovers from within the authorized scope.
- **Pros**: a contested finding is judged against the agreed contract without a user round trip; the user decides
  only changes to the agreement.
- **Cons**: the Host, not the user, judges whether a contested P1's failure condition applies.

### Option 2: Contested P1 as a worker question to the user (`ADR-bounded-high-effort-review-loop`)
- **Cons**: adds a user approval step inside approved scope and a P1 waiver path; disagrees with the shipped
  `review-loop.md`.

### Option 3: Fixed round limit or unbounded loop
- **Cons**: a fixed limit of two re-review rounds hands over loops that still converge; an unbounded loop keeps
  running on P3 improvements. Both were rejected by `ADR-bounded-high-effort-review-loop` and stay rejected.

---

## 4. Decision Outcome

We adopt **Option 1**. It replaces `ADR-bounded-high-effort-review-loop` as a whole: the hand-over rules below replace
its contested-P1 question, its answer-citing P1 waiver and its user-requested extra round; its other rules are carried
over unchanged.

### Rounds (carried over)

- A fresh reviewer per round, given the earlier findings, the round's diff scope and the effort; round 1 reviews the
  whole change, each later round every fix since the previous one, never a subset.
- The implementer fixes every finding of a round together (P2/P3 may be waived with a reason) and closes the round
  before the next is recorded. A P1 the implementer holds invalid stays open in the closing record with
  counter-evidence and sends the batch to the next round.
- The next round is skipped only when every fix of the batch meets the four minor-fix conditions (location, nature,
  contract, evidence); those fixes are self-verified. The initial reviewer calls stay mandatory.
- `P1`/`P2`/`P3` with one P1 definition per review kind; the reviewer owns the label and the implementer records it
  unchanged. Severity is required on every finding at every effort and has no effect on checks.
- Recurrence is a fixed `recurs:` prefix in `issue`; out-of-scope findings are derived from the round's diff files.
- Round numbers live in a fixed summary marker (`round <N>;`, `closes reconcile-check-<NN>;`), never in new fields.
  Round counts survive `devkit workflow return` within a segment.

### Bounded recovery

- The cap (3 rounds after the initial review) only limits further rounds: at the cap round a fully minor batch ends
  the loop; any other batch is a `problem` in the `worker` envelope naming the open findings. A recurring P1 is a
  `problem` too. (carried over)
- A contested P1 still asserted after one more round with the implementer's counter-evidence is a `problem` in the
  `worker` envelope with the disagreement and the evidence, not a `worker` question.
- The Host owns recovery within the authorized goal, scope and constraints; recovery adds no user approval gate. The
  Host preserves the failed range, head, open findings and attempted remedies and never resets the count.
- A contested P1 is closed only with evidence that its failure condition does not apply under the agreed contract.
  Changing an acceptance criterion or waiving an agreed constraint needs the user's decision.
- A Host-directed recovery gets one further fresh round outside the cap, named by its `resolution` envelope (for a
  Planning fold of answers, by the `answer` envelope). If it fails, the Host chooses another remedy or reports a
  blocker, and never integrates while required findings remain open.
- The Host asks the user only for information it cannot obtain, a change to the agreed goal, scope or constraints, or
  a main boundary whose policy is `ask`.
- A session reports a cap or recurrence hand-over in the conversation and does not integrate; the Host resolves a
  contested P1 against the agreed contract. None of this is the `exception` stage.

### Effort rules (carried over from `ADR-medium-review-delegation`)

- Distinct read-only `code-reviewer` and `reconcile-reviewer` contracts. The implementer writes, fixes and resolves the
  Living Spec reflection and `reconcile.md` at every effort; reviewers only return verification results.
- At `medium`, the initial code review is mandatory for session and Unit paths regardless of change size.
- Only `medium` Unit-path reconcile verification may omit its initial subagent call, when all affected contracts and
  documents can be identified, agreement with the actual diff can be directly demonstrated, and no unresolved
  contract interpretation or cross-component impact remains. A confirmed no-impact or wording-only reflection may
  qualify; small size alone does not; uncertainty requires the reconcile reviewer. The omission reason and the
  self-verification evidence are recorded in the existing `reconcile-check` envelope.
- After the initial `medium` review, the implementer verifies fixes and later changes and decides whether to call
  either reviewer again; expanded scope, uncertain correctness or contract interpretation are reasons to call.
  Findings still need evidence of resolution, later verification is attributed to its actual executor, and a failed
  or stale initial call never fulfills the required first review.
- `low` keeps self-review and a self-checked reconcile.
- Stage ids, order, entry and exit checks, gates, returns and effort selection are unchanged; required repository
  policies remain binding.

---

## 5. Consequences

- **Positive**: the ADR, `CAP-DLV-delivery-workflows` and `review-loop.md` state one hand-over rule; a contested
  finding no longer waits on the user inside approved scope.
- **Negative / Risks**: `high` costs a subagent round per batch that holds a non-minor fix; reviewer payloads grow by
  the earlier findings and the round's diff scope; a wrong Host judgment on a contested P1 is caught only by later
  review or the integration gate.
- Like `ADR-bounded-high-effort-review-loop`, this decision supplements the verifier assignment of
  `ADR-review-and-reconcile-verification`, whose challenger-round and count rules refine it: `medium` may self-verify
  the initial reconcile under the stated conditions and `high` may self-verify a batch of minor reconcile fixes; the
  initial reconcile verification at `high` stays independent.
- **Follow-ups**: none.

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py` (the loop ships once in
  `review-loop.md` and the other bundle files cite it).
- Review only for the agreement between this ADR, `CAP-DLV-delivery-workflows` and `review-loop.md` section 4.
