---
id: PADR-bounded-high-effort-review-loop
title: Bounded high-effort review loop
summary: At high, fresh review rounds run until no P1 remains, every fix is closed in a round or by bounded self-verification, severity is the reviewer's P1/P2/P3, and stalled or contested loops are handed to the user through existing worker questions and problems.
proposal: PROP-high-effort-review-loop
status: draft
created_at: 2026-10-19
---

# [PADR-bounded-high-effort-review-loop] Bounded high-effort review loop

- **Status**: Draft
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
2. **P1-driven loop with stall detection** (chosen): rounds continue while a P1 is open or an unreviewed non-minor
   fix exists; hand-over on recurrence, no progress, a contested P1 or a safety cap.
3. **Unbounded loop until no finding**: rejected: P3 improvements would keep it running.

## 4. Decision Outcome

Option 2, as specified in `PROP-high-effort-review-loop` §3.1 to §3.5:

- A fresh reviewer per round, given the earlier findings, the round's diff scope and the effort; every finding of a
  round is closed before the next round is recorded.
- A fix is self-verified only under the four minor-fix conditions (location, nature, contract, evidence); every other
  fix joins the next round (D1, recommended). The initial reviewer calls stay mandatory.
- `P1`/`P2`/`P3` with one P1 definition per review kind; the reviewer owns the label and the implementer records it
  unchanged.
- Recurrence is a fixed `recurs:` prefix in `issue`; out-of-scope findings are derived from the round's diff files.
- Round counts survive `devkit workflow return` within a segment.
- Stall or cap is a `worker` problem; a contested P1 still asserted after one counter-evidence round (D2, recommended) is
  a `worker` question; a session reports either in the conversation and does not integrate. This is not the `exception` stage.

Open until the user answers (proposal §3.8): D1 closing non-minor P2/P3 fixes, D2 contested P1, D3 the relation to
`ADR-medium-review-delegation`, D4 the round cap, D5 the severity scope.

## 5. Consequences

- `high` costs a subagent round only for non-minor fixes and open P1s; trivial fixes close with recorded evidence.
- Reviewer payloads grow by the earlier findings and the round's diff scope.
- The `medium` rules are unchanged; `ADR-reconcile-check-envelope` keeps holding, since the initial reconcile
  verification at `high` stays independent.
