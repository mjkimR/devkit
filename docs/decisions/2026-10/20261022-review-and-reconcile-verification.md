---
id: ADR-review-and-reconcile-verification
title: Verification records for reconcile checks and challenger rounds
summary: "For reconcile and Planning verification, we record every reconcile check as a reconcile-check envelope the living-spec-draft exit reads and let a reverify close challenger rounds, counting unmarked high rounds in order, to enforce and close verification in records, accepting more envelopes per unit."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-reconcile-check-envelope
  - ADR-reverify-closes-challenger-rounds
---

# [ADR-review-and-reconcile-verification] Verification records for reconcile checks and challenger rounds

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `CAP-DLV-delivery-workflows`

---

## 1. Context & Problem Statement

The strategy layer's master flow (workbench `docs/strategy-layer/01-master-flow.md` §2.3) has the implementer write
the Living Spec reflection and `reconcile.md` at every `activity-effort`, verified by the implementer at `low`, by the
`reviewer` at `medium` and by a separate `reconciler` at `high`. Nothing recorded or enforced that verification: a
walkthrough of the local flow found no defined place for the `medium` reviewer's reconcile check, and recording it as
a `review` envelope with a finding sent `devkit workflow next` back to `review-refine`, whose exit reads the latest
review round.

A Planning worker folds every `challenger` finding into the proposal, but the record kept them `open`: only a
`reverify` closed findings, and it had to name a `review-NN.yaml` (`CAP-DLV-workflow-envelopes` section 1). The
`plan-accept` request then showed open counts for settled findings (`FB-challenger-findings-stay-open`). Separately,
`references/review-loop.md` read round counts only from the `round <N>;` marker, so rounds recorded before the marker
existed had no defined count, and folding the user's answers into a reviewed proposal was named neither a batch nor a
fresh loop (`FB-review-loop-round-count-across-procedure-change`). Evidence:
`docs/materials/2026-10/20261020-envelope-record-gaps/spike-evidence.md`.

---

## 2. Decision Drivers

- The verification is enforced by the workflow, not only described.
- One stage exit for every effort; only who verifies changes.
- A reconcile finding is fixed in the reconcile, never by reopening the code review.
- The closure of challenger findings must work at `medium`, where there is one `challenger` pass and no later round.
- The challenger envelope stays the reviewer's return as recorded; the implementer's disposition is a separate record
  (`references/worker-records.md`: what another actor does later is a separate envelope).
- 25 existing `reverify` files use the `review` key; no rename (no migration paths, AGENTS.md "Compatibility").
- No gate or policy change: no `sdd-proposal` check starts reading challenger findings.

---

## 3. Considered Options

### Recording the reconcile verification (`ADR-reconcile-check-envelope`)

- **A `reconcile-check` envelope read by the `living-spec-draft` exit** (selected): `living-spec-draft` (shared by
  `sdd-spec-feature` and `sdd-spec-bugfix`) exits on `envelope-completed(reconcile-check)` besides the resolved record
  and the completed spec. Pros: enforced at every effort with devkit's existing `envelope-completed` primitive; no
  devkit change; the review round is untouched. Cons: one more envelope per Unit-path Development.
- **Record it as a `review` round** (rejected): a finding reopens `review-refine`; nothing requires the check at `low`
  or `high`.

### Closing challenger findings (`ADR-reverify-closes-challenger-rounds`)

- **A. `reverify` closes a challenger round** (selected): `devkit workflow envelope reverify --from challenger-NN.yaml`
  carries its findings, `--resolve`/`--waive` dispose of them.
- **B. `--resolve` on the next `challenger-NN`** (rejected): impossible at `medium`, and mixes dispositions into a
  reviewer return.
- **C. The next round's summary resolves the findings by rule** (rejected): no record change; `open_findings` stays
  wrong.
- **D. `envelope check` omits `open_findings` for kinds no check reads** (rejected): hides the count instead of
  recording what happened.

### Counting rounds (`ADR-reverify-closes-challenger-rounds`)

- **R1. Unmarked rounds count in envelope order** (selected, scoped).
- **R2. Only marked rounds count** (rejected).
- **R3. Each segment restarts the count** (rejected).

---

## 4. Decision Outcome

### The `reconcile-check` envelope

- Every effort writes a `reconcile-check` envelope at `living-spec-draft`, whose exit requires it: at `low` the
  implementer's self-check, stated as such; at `medium` the reviewer's check of the written reconcile, returned
  separately from its code review; at `high` the `reconciler`'s independent verification. The roles stay read-only:
  the implementer records their returned fields. (ADR-reconcile-check-envelope)
- On findings the implementer fixes the reflection or `reconcile.md` and writes a new `reconcile-check`; the latest
  one decides. (ADR-reconcile-check-envelope)
- A contradiction between the implementation and a contract still takes the stage's return to the build stage.
  (ADR-reconcile-check-envelope)

### Reverify closes challenger rounds

- These rules refine `ADR-host-owned-review-loop-recovery` (the closing record of a Planning round, and the count of
  rounds recorded before its marker existed) without superseding it. (ADR-reverify-closes-challenger-rounds)
- `reverify --from` accepts a `challenger-NN.yaml` (or a reverify that closes one) besides review files; the `review`
  key then names that challenger file, and the reference pattern becomes `review-NN.yaml` or `challenger-NN.yaml`.
  `review` stays the key name. `--from latest` keeps meaning the review state; when the unit has no review, its refusal
  names `--from envelopes/challenger-NN.yaml` in the fix. The deciding state of `challenger` becomes the latest
  challenger or the last reverify naming it, as for `review`; the review state ignores reverifies of challenger rounds.
  (ADR-reverify-closes-challenger-rounds)
- `envelope new --kind challenger` refuses findings whose `resolution` is not `open`, as `review` does, so the reverify
  is the only closing path. `envelope check` prints `review=<file>` on reverify lines (and the JSON entry carries
  `review`), so the `plan-accept` request shows each challenger round with its closing reverify.
  (ADR-reverify-closes-challenger-rounds)
- Planning closes each `challenger` round after its fold with one such `reverify` (`--resolve` for each folded
  finding, `--waive N=<reason>` for a P2 or P3 not taken, `Decision needed:` findings left open for `plan-accept`), at
  `medium` and `high`. At `high` the next `challenger-NN` round still follows when section 2 of the review loop
  requires it; its summary no longer has to restate the dispositions. (ADR-reverify-closes-challenger-rounds)

### Round count

- Each loop counts its own kind (`challenger`, `review`, `reconcile-check`). Marked rounds count by their marker. A
  round recorded without a `round <N>;` marker counts, in sequence order of its kind, only when it precedes the loop's
  first marked round in the segment and a `worker` envelope of the segment written before that marker records
  `activity_effort: high`; otherwise unmarked rounds (a `medium` or `low` run's) never count, and a `high` loop that
  follows them starts at round 1. When a marker disagrees with the inferred count, the higher number holds, so the cap
  is never extended. A `reverify` is never a round. (ADR-reverify-closes-challenger-rounds)
- Folding user answers (the user's answer `answer-fold-round`, historical Git
  `5551f9f4fc2920b973276aa43a2b0e36778c2f7a:docs/proposals/PROP-envelope-record-gaps/envelopes/answer-01.yaml`): a
  Planning turn that folds the user's answers into a proposal already reviewed in a `high` loop treats the fold as a
  new batch of the same loop, never a fresh loop; the round count continues. When the fold's batch reaches the cap
  round and would need another round, it gets one further fresh round outside the cap, as a fix the user requested
  does (section 4 of the review loop); that round's `challenger-NN` summary cites the `answer` envelope in place of a
  `resolution`. Its outcome follows the loop's rules: a recurrence of the same P1 or a batch that still fails section 2
  hands over again. An answer alone therefore never forces a hand-over, and the loop stays bounded: one extra round per
  answered fold at most, and only the user starts a new answer round. (ADR-reverify-closes-challenger-rounds)

---

## 5. Consequences

- **Positive**: the reconcile verification is enforced at every effort and its findings never reopen the review
  round; folded Planning findings end resolved or waived in the record, and `plan-accept` shows each challenger round
  with its closing reverify.
- **Negative / Risks**: one more envelope per Unit-path Development; units bound before the `reconcile-check` exit see
  a new unmet exit at `living-spec-draft` (a schema drift to accept with `devkit workflow bind`). Existing challenger
  envelopes stay open; no back-fill.
- **Follow-ups**:
  - The reviewer and reconciler contracts return the fields of a `reconcile-check`; the reconciler's former envelope
    kind `reconciler` is gone.
  - Engine (`devkit.workflow`, devkit-agt): `REVIEW_REF`, `carried_findings` and its fix text, `Envelopes.deciding`,
    the challenger resolution refusal and the reverify `review=` output.
  - Contract: `CAP-DLV-workflow-envelopes` sections 1 to 3; `CAP-DLV-delivery-workflows` (the high review-loop rule
    naming Planning's closing record); bundle text: `references/review-loop.md` sections 1, 2, 4 (the answer fold) and
    5, the `planning-worker` contract step 4 and the `plan-accept` request in `sdd-proposal.md`.

---

## 6. Confirmation

- The `living-spec-draft` exit check `envelope-completed(reconcile-check)` in `sdd-spec-feature` and
  `sdd-spec-bugfix`.
- Engine tests for a challenger reverify, its malformed variants and the unchanged review state.
- `packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py` pins the review-loop wording.
