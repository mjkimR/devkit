---
id: ADR-reverify-closes-challenger-rounds
title: Reverify closes challenger rounds
summary: Lets a reverify close a challenger round, so folded Planning findings end resolved or waived in the record, and counts review-loop rounds an earlier high run recorded without the round marker in sequence order.
proposal: SPEC-envelope-record-gaps
status: accepted
created_at: 2026-10-19
---

# [ADR-reverify-closes-challenger-rounds] Reverify closes challenger rounds

- **Status**: Accepted
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

A Planning worker folds every `challenger` finding into the proposal, but the record keeps them `open`: only a
`reverify` closes findings, and it must name a `review-NN.yaml` (`CAP-DLV-workflow-envelopes` section 1). The
`plan-accept` request then shows open counts for settled findings (`FB-challenger-findings-stay-open`). Separately,
`references/review-loop.md` reads round counts only from the `round <N>;` marker, so rounds recorded before the
marker existed have no defined count, and folding the user's answers into a reviewed proposal is named neither a
batch nor a fresh loop (`FB-review-loop-round-count-across-procedure-change`). Evidence: `docs/materials/2026-10/20261020-envelope-record-gaps/spike-evidence.md`.

## 2. Decision Drivers

- The closure must work at `medium`, where there is one `challenger` pass and no later round.
- The challenger envelope stays the reviewer's return as recorded; the implementer's disposition is a separate record
  (`references/worker-records.md`: what another actor does later is a separate envelope).
- 25 existing `reverify` files use the `review` key; no rename (no migration paths, AGENTS.md "Compatibility").
- No gate or policy change: no `sdd-proposal` check starts reading challenger findings.

## 3. Considered Options

- **A. `reverify` closes a challenger round**: `devkit workflow envelope reverify --from challenger-NN.yaml` carries
  its findings, `--resolve`/`--waive` dispose of them.
- **B. `--resolve` on the next `challenger-NN`**: impossible at `medium`, and mixes dispositions into a reviewer return.
- **C. The next round's summary resolves the findings by rule**: no record change; `open_findings` stays wrong.
- **D. `envelope check` omits `open_findings` for kinds no check reads**: hides the count instead of recording what
  happened.

For the round count: **R1** unmarked rounds count in envelope order; **R2** only marked rounds count; **R3** each
segment restarts the count.

## 4. Decision Outcome

This decision refines `ADR-bounded-high-effort-review-loop` (the closing record of a Planning round, and the count of
rounds recorded before its marker existed) without superseding it.

- **Option A.** `reverify --from` accepts a `challenger-NN.yaml` (or a reverify that closes one) besides review
  files; the `review` key then names that challenger file, and the reference pattern becomes `review-NN.yaml` or
  `challenger-NN.yaml`. `review` stays the key name. `--from latest` keeps meaning the review state; when the unit has
  no review, its refusal names `--from envelopes/challenger-NN.yaml` in the fix. The deciding state of `challenger`
  becomes the latest challenger or the last reverify naming it, as for `review`; the review state ignores reverifies
  of challenger rounds.
- `envelope new --kind challenger` refuses findings whose `resolution` is not `open`, as `review` does, so the
  reverify is the only closing path. `envelope check` prints `review=<file>` on reverify lines (and the JSON entry
  carries `review`), so the `plan-accept` request shows each challenger round with its closing reverify.
- Planning closes each `challenger` round after its fold with one such `reverify` (`--resolve` for each folded
  finding, `--waive N=<reason>` for a P2 or P3 not taken, `Decision needed:` findings left open for `plan-accept`),
  at `medium` and `high`. At `high` the next `challenger-NN` round still follows when section 2 of the review loop
  requires it; its summary no longer has to restate the dispositions.
- **Round count R1, scoped.** Each loop counts its own kind (`challenger`, `review`, `reconcile-check`). Marked
  rounds count by their marker. A round recorded without a `round <N>;` marker counts, in sequence order of its kind,
  only when it precedes the loop's first marked round in the segment and a `worker` envelope of the segment written
  before that marker records `activity_effort: high`; otherwise unmarked rounds (a `medium` or `low` run's) never
  count, and a `high` loop that follows them starts at round 1. When a marker disagrees with the inferred count, the
  higher number holds, so the cap is never extended. A `reverify` is never a round.
- **Folding user answers** (the user's answer `answer-fold-round`, historical Git
  `5551f9f4fc2920b973276aa43a2b0e36778c2f7a:docs/proposals/PROP-envelope-record-gaps/envelopes/answer-01.yaml`): a Planning turn that
  folds the user's answers into a proposal already reviewed in a `high` loop treats the fold as a new batch of the
  same loop, never a fresh loop; the round count continues. When the fold's batch reaches the cap round and would need
  another round, it gets one further fresh round outside the cap, as a fix the user requested does (section 4 of the
  review loop); that round's `challenger-NN` summary cites the `answer` envelope in place of a `resolution`. Its outcome follows the loop's rules:
  a recurrence of the same P1 or a batch that still fails section 2 hands over again. An answer alone therefore never
  forces a hand-over, and the loop stays bounded: one extra round per answered fold at most, and only the user starts
  a new answer round.

## 5. Consequences

- Engine (`devkit.workflow`, devkit-agt): `REVIEW_REF`, `carried_findings` and its fix text, `Envelopes.deciding`,
  the challenger resolution refusal and the reverify `review=` output; tests for a challenger reverify, its malformed
  variants and the unchanged review state.
- Contract: `CAP-DLV-workflow-envelopes` sections 1 to 3; `CAP-DLV-delivery-workflows` (the high review-loop rule
  naming Planning's closing record); bundle text: `references/review-loop.md` sections 1, 2, 4 (the answer fold) and 5, the
  `planning-worker` contract step 4 and the `plan-accept` request in `sdd-proposal.md`; the test that pins the
  review-loop wording (`packages/devkit-spec/tests/test_effort_procedure.py`).
- Existing challenger envelopes stay open; no back-fill.
