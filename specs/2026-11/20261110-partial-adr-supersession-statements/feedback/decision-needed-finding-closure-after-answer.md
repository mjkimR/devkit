---
id: FB-decision-needed-finding-closure-after-answer
title: Planning does not say who closes a Decision needed finding once an answer settles it
scope: repo
kind: suggestion
category: spec-ambiguity
target: the spec skill's references/planning.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-10
---

# [FB-decision-needed-finding-closure-after-answer] Planning does not say who closes a Decision needed finding once an answer settles it

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `planning.md` step 3 closes a folded `challenger` round with `reverify` and says "leave
  `Decision needed:` findings open for `plan-accept`". A turn that turned such findings into questions ends with
  them `open`. Step 2 tells the next turn to record the answers and fold them; it names no reverify.
- **Proposed Procedure**: add to step 2 that the turn which folds an answer also closes the `Decision needed:`
  findings the answer settles, with a later `reverify --from envelopes/challenger-NN.yaml --resolve <N>`; a finding
  whose decision is still pending stays open.
- **Expected Benefit**: `devkit workflow envelope check` shows no open challenger finding for a decided question when
  the `plan-accept` request lists the envelopes, without the caller spelling the step out in each payload.
- **Cost & Risk**: one sentence in the reference; a worker could close a finding the answer settles only in part, so
  the sentence has to limit closure to what the answer decides.
- **Attempted**: the caller's payload named the reverify explicitly in this run; the reference alone was not tried.

## Diagnostic Details

- **Reproduction**: a `medium` Planning turn records a challenger round, closes it in part and asks the two
  `Decision needed:` findings as questions; the next turn receives the answers.
- **Expected / Actual**: expected the reference to say whether the answered findings are closed by reverify or stay
  open until `plan-accept`; it states only the first turn's rule.
- **Versions**: the repository at `c84a5485`.
- **Conditions**: a Planning that spans two turns with `Decision needed:` findings asked as questions.
- **Workarounds Attempted**: followed the caller's explicit instruction; succeeded.
- **Related Assets**: the `spec` skill's `references/planning.md` steps 2 and 3, `references/worker-records.md` §2,
  `devkit workflow envelope reverify`.

## Evidence

```text
planning.md step 3: "--resolve <N> per folded finding, --waive "<N>=<reason>" for a P2 or P3 not taken; leave
`Decision needed:` findings open for `plan-accept`."
planning.md step 2: "When answers to earlier questions arrived, record them first per worker records §2, then fold
the decisions into `proposal.md` and the PADRs." (no reverify named)
devkit workflow envelope check before this turn: reverify-01.yaml ... open_findings=2 review=challenger-01.yaml
```

- **Disposition**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md: Names reverify of the original challenger round after an answer fully settles an open finding; partial and pending findings stay open. Verified by source/contract diff review, `uv run devkit rules check` and `just test-affected --base 5134e082d8296b1c68086638c72ab6abaa98674e` (2422 passed).
