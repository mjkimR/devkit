---
id: PADR-reverify-closes-challenger-rounds
title: Reverify closes challenger rounds
summary: Lets a reverify close a challenger round, so folded Planning findings end resolved or waived in the record, and counts review-loop rounds recorded without the round marker in envelope order.
proposal: PROP-envelope-record-gaps
status: draft
created_at: 2026-10-19
---

# [PADR-reverify-closes-challenger-rounds] Reverify closes challenger rounds

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

A Planning worker folds every `challenger` finding into the proposal, but the record keeps them `open`: only a
`reverify` closes findings, and it must name a `review-NN.yaml` (`CAP-DLV-workflow-envelopes` section 1). The
`plan-accept` request then shows open counts for settled findings (`FB-challenger-findings-stay-open`). Separately,
`references/review-loop.md` reads round counts only from the `round <N>;` marker, so rounds recorded before the
marker existed have no defined count, and folding the user's answers into a reviewed proposal is named neither a
batch nor a fresh loop (`FB-review-loop-round-count-across-procedure-change`). Evidence: `materials/spike-evidence.md`.

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

- **Option A.** `reverify --from` accepts a `challenger-NN.yaml` (or a reverify that closes one) besides review
  files; the `review` key then names that challenger file, and the reference pattern becomes `review-NN.yaml` or
  `challenger-NN.yaml`. `--from latest` keeps meaning the review state. The deciding state of `challenger` becomes
  the latest challenger or the last reverify naming it, as for `review`; the review state ignores reverifies of
  challenger rounds. `review` stays the key name.
- Planning closes each `challenger` round after its fold with one such `reverify` (`--resolve` for each folded
  finding, `--waive N=<reason>` for a P2 or P3 not taken, `Decision needed:` findings left open for `plan-accept`),
  at `medium` and `high`. At `high` the next `challenger-NN` round still follows when section 2 of the review loop
  requires it; its summary no longer has to restate the dispositions.
- **Round count R1.** Within one segment, a `challenger`, `review` or `reconcile-check` envelope whose summary has
  no `round <N>;` marker counts as one round in envelope sequence order; the next marked round's `N` continues from
  that count. A `reverify` is never a round.
- **Folding user answers**: pending the user's answer to question `answer-fold-round` of this Planning's `worker`
  envelope.

## 5. Consequences

- Engine (`devkit.workflow`, devkit-agt): `REVIEW_REF`, `carried_findings`, `Envelopes.deciding`; tests for a
  challenger reverify, its malformed variants and the unchanged review state.
- Contract: `CAP-DLV-workflow-envelopes` sections 1 and 2; bundle text: `references/review-loop.md` sections 1, 2 and
  5, the `planning-worker` contract step 4 and the `plan-accept` request in `sdd-proposal.md` (support-role envelopes
  shown with their closing reverify).
- Existing challenger envelopes stay open; no back-fill.
