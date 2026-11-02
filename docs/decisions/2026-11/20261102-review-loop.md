---
id: ADR-review-loop
title: Review roles, bounded review loop and verification records
summary: "For code review, reconcile and Planning verification, we separate read-only reviewer roles, bound medium delegation, cap high whole-batch rounds with Host-owned recovery and record reconcile checks and challenger reverifies, to enforce and end verification, accepting more rounds and envelopes."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-medium-review-delegation
  - ADR-bounded-high-effort-review-loop
  - ADR-host-owned-review-loop-recovery
  - ADR-review-and-reconcile-verification
  - ADR-reconcile-check-envelope
  - ADR-reverify-closes-challenger-rounds
---

# [ADR-review-loop] Review roles, bounded review loop and verification records

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: the `spec` bundle (`skills/spec/references/review-loop.md`,
  `skills/spec/references/effort.md`), `capabilities/delivery/` (`CAP-DLV-delivery-workflows`,
  `CAP-DLV-workflow-envelopes`), `ARCH-04-delivery-strategy`

---

## 1. Context & Problem Statement

Code review and reconcile verification compare different artifacts and require different instructions. Requiring a
subagent after every fix repeats independent review even when the implementer can verify the correction directly.

The implementer writes the Living Spec reflection and `reconcile.md` at every `activity-effort`, verified by the
implementer at `low`, by the reviewer at `medium` and by a separate `reconcile-reviewer` at `high` (workbench
`docs/strategy-layer/01-master-flow.md` §2.3). That verification needs a recorded and enforced place: recording it as
a `review` envelope with a finding sends `devkit workflow next` back to `review-refine`, whose exit reads the latest
review round.

The `high` loop for code review, reconcile verification and `high` Planning needs a round scope, an end and a
hand-over, and findings need a priority (`CAP-DLV-workflow-envelopes`: `severity` is otherwise a free label), without
changing envelope schemas, stages, checks or gates. The shipped `spec` skill reference `review-loop.md` (section 4,
"Bounded recovery") makes a contested P1 a `problem` for the Host, lets the Host own recovery within the authorized
goal, scope and constraints, and adds no user approval gate; the user decided that this rule holds.

A Planning worker folds every `challenger` finding into the proposal, but only a `reverify` closed findings, and it
had to name a `review-NN.yaml` (`CAP-DLV-workflow-envelopes` section 1), so the `plan-accept` request showed open
counts for settled findings (`FB-challenger-findings-stay-open`). Round counts were read only from the `round <N>;`
marker, so rounds recorded before the marker existed had no defined count, and folding the user's answers into a
reviewed proposal was named neither a batch nor a fresh loop (`FB-review-loop-round-count-across-procedure-change`).
Evidence: `docs/materials/2026-10/20261020-envelope-record-gaps/spike-evidence.md`.

---

## 2. Decision Drivers

- `high` ends deterministically and stays stricter than `medium`.
- No fix ships at `high` unseen by a reviewer unless it is provably minor.
- Hand-over uses records that already exist (`worker` problems and `resolution` envelopes), not new kinds or keys.
- The Host already holds authority within the approved scope (sequencing, workers, fixes); the user is asked only
  for what changes the agreement.
- The finding schema is closed (`issue`, `evidence`, `failure_condition`, `suggested_action`, `resolution`, `waiver`,
  `severity`).
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

### Review loop

- **Whole-batch loop with Host-owned recovery** (selected): every hand-over, the contested P1 included, is recorded
  as a `worker` problem the Host recovers from within the authorized scope. Pros: a contested finding is judged
  against the agreed contract without a user round trip; the user decides only changes to the agreement. Cons: the
  Host, not the user, judges whether a contested P1's failure condition applies.
- **Contested P1 as a worker question to the user** (rejected in `ADR-host-owned-review-loop-recovery`): adds a user
  approval step inside approved scope and a P1 waiver path; disagrees with the shipped `review-loop.md`.
- **Fixed round limit**: hand over after two re-review rounds; hands over loops that still converge (rejected in
  `ADR-bounded-high-effort-review-loop`, kept rejected in `ADR-host-owned-review-loop-recovery`).
- **Unbounded loop until no finding**: P3 improvements would keep it running (rejected in
  `ADR-bounded-high-effort-review-loop`, kept rejected in `ADR-host-owned-review-loop-recovery`).

### Recording the reconcile verification

- **A `reconcile-check` envelope read by the `living-spec-draft` exit** (selected): `living-spec-draft` (shared by
  `sdd-spec-feature` and `sdd-spec-bugfix`) exits on `envelope-completed(reconcile-check)` besides the resolved record
  and the completed spec. Pros: enforced at every effort with devkit's existing `envelope-completed` primitive; no
  devkit change; the review round is untouched. Cons: one more envelope per Unit-path Development.
- **Record it as a `review` round** (rejected in `ADR-reconcile-check-envelope`): a finding reopens `review-refine`;
  nothing requires the check at `low` or `high`.

### Closing challenger findings

- **A. `reverify` closes a challenger round** (selected): `devkit workflow envelope reverify --from challenger-NN.yaml`
  carries its findings, `--resolve`/`--waive` dispose of them.
- **B. `--resolve` on the next `challenger-NN`** (rejected in `ADR-reverify-closes-challenger-rounds`): impossible at
  `medium`, and mixes dispositions into a reviewer return.
- **C. The next round's summary resolves the findings by rule** (rejected in `ADR-reverify-closes-challenger-rounds`):
  no record change; `open_findings` stays wrong.
- **D. `envelope check` omits `open_findings` for kinds no check reads** (rejected in
  `ADR-reverify-closes-challenger-rounds`): hides the count instead of recording what happened.

### Counting rounds

- **R1. Unmarked rounds count in envelope order** (selected, scoped).
- **R2. Only marked rounds count** (rejected in `ADR-reverify-closes-challenger-rounds`).
- **R3. Each segment restarts the count** (rejected in `ADR-reverify-closes-challenger-rounds`).

---

## 4. Decision Outcome

### Review roles and effort rules

- Distinct read-only `code-reviewer` and `reconcile-reviewer` contracts. The implementer writes, fixes and resolves the
  Living Spec reflection and `reconcile.md` at every effort; reviewers only return verification results.
  (`ADR-host-owned-review-loop-recovery`)
- At `medium`, the initial code review is mandatory for session and Unit paths regardless of change size.
  (`ADR-host-owned-review-loop-recovery`)
- Only `medium` Unit-path reconcile verification may omit its initial subagent call, when all affected contracts and
  documents can be identified, agreement with the actual diff can be directly demonstrated, and no unresolved
  contract interpretation or cross-component impact remains. A confirmed no-impact or wording-only reflection may
  qualify; small size alone does not; uncertainty requires the reconcile reviewer. The omission reason and the
  self-verification evidence are recorded in the existing `reconcile-check` envelope.
  (`ADR-host-owned-review-loop-recovery`)
- After the initial `medium` review, the implementer verifies fixes and later changes and decides whether to call
  either reviewer again; expanded scope, uncertain correctness or contract interpretation are reasons to call.
  Findings still need evidence of resolution, later verification is attributed to its actual executor, and a failed
  or stale initial call never fulfills the required first review. (`ADR-host-owned-review-loop-recovery`)
- `low` keeps self-review and a self-checked reconcile. (`ADR-host-owned-review-loop-recovery`)
- Stage ids, order, entry and exit checks, gates, returns and effort selection are unchanged; required repository
  policies remain binding. (`ADR-host-owned-review-loop-recovery`)

### High-effort rounds

- A fresh reviewer per round, given the earlier findings, the round's diff scope and the effort; round 1 reviews the
  whole change, each later round every fix since the previous one, never a subset.
  (`ADR-host-owned-review-loop-recovery`)
- The implementer fixes every finding of a round together (P2/P3 may be waived with a reason) and closes the round
  before the next is recorded. A P1 the implementer holds invalid stays open in the closing record with
  counter-evidence and sends the batch to the next round. (`ADR-host-owned-review-loop-recovery`)
- The next round is skipped only when every fix of the batch meets the four minor-fix conditions (location, nature,
  contract, evidence); those fixes are self-verified. The initial reviewer calls stay mandatory.
  (`ADR-host-owned-review-loop-recovery`)
- `P1`/`P2`/`P3` with one P1 definition per review kind; the reviewer owns the label and the implementer records it
  unchanged. Severity is required on every finding at every effort and has no effect on checks.
  (`ADR-host-owned-review-loop-recovery`)
- Recurrence is a fixed `recurs:` prefix in `issue`; out-of-scope findings are derived from the round's diff files.
  (`ADR-host-owned-review-loop-recovery`)
- Round numbers live in a fixed summary marker (`round <N>;`, `closes reconcile-check-<NN>;`), never in new fields.
  Round counts survive `devkit workflow return` within a segment. (`ADR-host-owned-review-loop-recovery`)

### Bounded recovery

- The cap (3 rounds after the initial review) only limits further rounds: at the cap round a fully minor batch ends
  the loop; any other batch is a `problem` in the `worker` envelope naming the open findings. A recurring P1 is a
  `problem` too. (`ADR-host-owned-review-loop-recovery`)
- A contested P1 still asserted after one more round with the implementer's counter-evidence is a `problem` in the
  `worker` envelope with the disagreement and the evidence, not a `worker` question.
  (`ADR-host-owned-review-loop-recovery`)
- The Host owns recovery within the authorized goal, scope and constraints; recovery adds no user approval gate. The
  Host preserves the failed range, head, open findings and attempted remedies and never resets the count.
  (`ADR-host-owned-review-loop-recovery`)
- A contested P1 is closed only with evidence that its failure condition does not apply under the agreed contract.
  Changing an acceptance criterion or waiving an agreed constraint needs the user's decision.
  (`ADR-host-owned-review-loop-recovery`)
- A Host-directed recovery gets one further fresh round outside the cap, named by its `resolution` envelope (for a
  Planning fold of answers, by the `answer` envelope). If it fails, the Host chooses another remedy or reports a
  blocker, and never integrates while required findings remain open. (`ADR-host-owned-review-loop-recovery`)
- The Host asks the user only for information it cannot obtain, a change to the agreed goal, scope or constraints, or
  a main boundary whose policy is `ask`. (`ADR-host-owned-review-loop-recovery`)
- A session reports a cap or recurrence hand-over in the conversation and does not integrate; the Host resolves a
  contested P1 against the agreed contract. None of this is the `exception` stage.
  (`ADR-host-owned-review-loop-recovery`)

### The `reconcile-check` envelope

- Every effort writes a `reconcile-check` envelope at `living-spec-draft`, whose exit requires it: at `low` the
  implementer's self-check, stated as such; at `medium` the reviewer's check of the written reconcile, returned
  separately from its code review; at `high` the `reconcile-reviewer`'s independent verification. The roles stay
  read-only: the implementer records their returned fields. (`ADR-reconcile-check-envelope`)
- On findings the implementer fixes the reflection or `reconcile.md` and writes a new `reconcile-check`; the latest
  one decides. (`ADR-reconcile-check-envelope`)
- A contradiction between the implementation and a contract still takes the stage's return to the build stage.
  (`ADR-reconcile-check-envelope`)

### Reverify closes challenger rounds

- These rules refine the review loop above (the closing record of a Planning round, and the count of rounds recorded
  before its marker existed) without superseding it. (`ADR-reverify-closes-challenger-rounds`)
- `reverify --from` accepts a `challenger-NN.yaml` (or a reverify that closes one) besides review files; the `review`
  key then names that challenger file, and the reference pattern becomes `review-NN.yaml` or `challenger-NN.yaml`.
  `review` stays the key name. `--from latest` keeps meaning the review state; when the unit has no review, its refusal
  names `--from envelopes/challenger-NN.yaml` in the fix. The deciding state of `challenger` becomes the latest
  challenger or the last reverify naming it, as for `review`; the review state ignores reverifies of challenger rounds.
  (`ADR-reverify-closes-challenger-rounds`)
- `envelope new --kind challenger` refuses findings whose `resolution` is not `open`, as `review` does, so the reverify
  is the only closing path. `envelope check` prints `review=<file>` on reverify lines (and the JSON entry carries
  `review`), so the `plan-accept` request shows each challenger round with its closing reverify.
  (`ADR-reverify-closes-challenger-rounds`)
- Planning closes each `challenger` round after its fold with one such `reverify` (`--resolve` for each folded
  finding, `--waive N=<reason>` for a P2 or P3 not taken, `Decision needed:` findings left open for `plan-accept`), at
  `medium` and `high`. At `high` the next `challenger-NN` round still follows when section 2 of the review loop
  requires it; its summary no longer has to restate the dispositions. (`ADR-reverify-closes-challenger-rounds`)

### Round count

- Each loop counts its own kind (`challenger`, `review`, `reconcile-check`). Marked rounds count by their marker. A
  round recorded without a `round <N>;` marker counts, in sequence order of its kind, only when it precedes the loop's
  first marked round in the segment and a `worker` envelope of the segment written before that marker records
  `activity_effort: high`; otherwise unmarked rounds (a `medium` or `low` run's) never count, and a `high` loop that
  follows them starts at round 1. When a marker disagrees with the inferred count, the higher number holds, so the cap
  is never extended. A `reverify` is never a round. (`ADR-reverify-closes-challenger-rounds`)
- Folding user answers (the user's answer `answer-fold-round`, historical Git
  `5551f9f4fc2920b973276aa43a2b0e36778c2f7a:docs/proposals/PROP-envelope-record-gaps/envelopes/answer-01.yaml`): a
  Planning turn that folds the user's answers into a proposal already reviewed in a `high` loop treats the fold as a
  new batch of the same loop, never a fresh loop; the round count continues. When the fold's batch reaches the cap
  round and would need another round, it gets one further fresh round outside the cap, as a fix the user requested
  does (section 4 of the review loop); that round's `challenger-NN` summary cites the `answer` envelope in place of a
  `resolution`. Its outcome follows the loop's rules: a recurrence of the same P1 or a batch that still fails section 2
  hands over again. An answer alone therefore never forces a hand-over, and the loop stays bounded: one extra round per
  answered fold at most, and only the user starts a new answer round. (`ADR-reverify-closes-challenger-rounds`)

---

## 5. Consequences

- **Positive**:
  - The ADR, `CAP-DLV-delivery-workflows` and `review-loop.md` state one hand-over rule; a contested finding no longer
    waits on the user inside approved scope.
  - The reconcile verification is enforced at every effort and its findings never reopen the review round; folded
    Planning findings end resolved or waived in the record, and `plan-accept` shows each challenger round with its
    closing reverify.
- **Negative / Risks**:
  - The initial `medium` reconcile check can be self-verification, while its evidence and completion check remain
    mandatory.
  - `high` costs a subagent round per batch that holds a non-minor fix; a batch of trivial fixes closes with recorded
    evidence. Reviewer payloads grow by the earlier findings and the round's diff scope.
  - A wrong Host judgment on a contested P1 is caught only by later review or the integration gate.
  - One more envelope per Unit-path Development; units bound before the `reconcile-check` exit see a new unmet exit
    at `living-spec-draft` (a schema drift to accept with `devkit workflow bind`). Existing challenger envelopes stay
    open; no back-fill.
  - The review loop supplements the verifier assignment of the `reconcile-check` envelope, whose challenger-round and
    count rules refine it: `medium` may self-verify the initial reconcile under the stated conditions and `high` may
    self-verify a batch of minor reconcile fixes; the initial reconcile verification at `high` stays independent, and
    the envelope separation and stage check remain intact.
  - Role names changed in place, without aliases. Active units bound to renamed stage roles must rebind after
    inspecting workflow drift. Completed units remain history (from `ADR-medium-review-delegation`).
- **Follow-ups**:
  - The reviewer and `reconcile-reviewer` contracts return the fields of a `reconcile-check`; the reconcile
    reviewer's former envelope kind `reconciler` is gone.
  - Engine (`devkit.workflow`, devkit-agt): `REVIEW_REF`, `carried_findings` and its fix text, `Envelopes.deciding`,
    the challenger resolution refusal and the reverify `review=` output.
  - Contract: `CAP-DLV-workflow-envelopes` sections 1 to 3; `CAP-DLV-delivery-workflows` (the high review-loop rule
    naming Planning's closing record); bundle text: `references/review-loop.md` sections 1, 2, 4 (the answer fold) and
    5, the `planning-worker` contract step 4 and the `plan-accept` request in `sdd-proposal.md`.

---

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py` (the loop ships once in
  `review-loop.md` and the other bundle files cite it; it pins the review-loop wording).
- The `living-spec-draft` exit check `envelope-completed(reconcile-check)` in `sdd-spec-feature` and
  `sdd-spec-bugfix`.
- Engine tests for a challenger reverify, its malformed variants and the unchanged review state.
- Review only for the agreement between this ADR, `CAP-DLV-delivery-workflows` and `review-loop.md` section 4.
