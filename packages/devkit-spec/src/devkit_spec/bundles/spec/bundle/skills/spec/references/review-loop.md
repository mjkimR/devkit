# Review loop at `high`

Read this when an activity runs at `activity-effort` `high` ([effort](effort.md)): Development code review (`code-reviewer`), reconcile verification (`reconcile-reviewer`) and `high` Planning (`challenger`). Stages, checks and gates are unchanged; the loop is procedure above them.

## 1. Rounds

| Item | Rule |
| --- | --- |
| Round | A fresh reviewer instance, never a continued one. Round 1 reviews the whole change; each later round reviews every fix made since the previous round and what it affects, never a subset. Input: the earlier rounds' findings, the round's diff scope and the effort ([payload](../../spec-delegate/references/payload.md)). |
| Fixing | The implementer fixes every finding of the round, P1, P2 and P3 together (a P2 or P3 may be waived with a reason), and closes the round before the next is recorded: `reverify` for code; a new `reconcile-check` for reconcile; for Planning, a `reverify --from envelopes/challenger-NN.yaml` after the fold, stating what each finding became. A P1 the implementer holds invalid is not fixed: it stays open in that closing record with the counter-evidence (tests or output) and sends the whole batch to the next round, the one more round of section 4. |
| Next round | Runs, on the whole batch, when any fix of the batch fails the minor-fix conditions (section 2) or a P1 stays open as contested. |
| End | The round returns no finding, or every fix of the batch meets section 2 and is self-verified. |
| Round count | Each round's envelope summary starts with `round <N>;` (round 1 is the initial review), and a reconcile check that closes an earlier one also with `closes reconcile-check-<NN>;`. Each loop counts its own kind (`challenger`, `review`, `reconcile-check`), marked rounds by their marker. A round recorded without the marker counts, in sequence order of its kind, only when it precedes the loop's first marked round in the segment and a `worker` envelope of the segment written before that marker records `activity_effort: high`; otherwise unmarked rounds never count, and a `high` loop that follows them starts at round 1. When a marker disagrees with the inferred count, the higher number holds. A `reverify` is never a round. A `devkit workflow return` does not reset the count. |

The initial `code-reviewer`, `reconcile-reviewer` and `high` Planning `challenger` calls are mandatory; nothing replaces round 1 with a self-check.

A finding is out of scope of its round when its `evidence` path is not in the round's diff file list: it is fixed with the rest of the batch and never counts as a recurrence.

## 2. Minor-fix self-verification

After a round, its batch MAY be self-verified instead of starting the next round only when every fix in it meets all four conditions:

| Condition | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| Location | Only the location the finding's `evidence` names | Only the document or entry the finding names | Only the proposal section the finding names |
| Nature | Typo, comment, formatting, in-scope rename, test-only addition, or the `suggested_action` applied as written when it names a concrete edit | Wording only, or a concrete `suggested_action` applied as written | Wording only, or a concrete `suggested_action` applied as written |
| Contract | No public API, schema, error code, CLI output or other package touched | The contract's meaning is unchanged | No decision changed |
| Evidence | Behavior fixes: a test or check reproducing the `failure_condition` passes (for a P1, it failed before the fix). Text-only kinds: the diff is limited to the named location | The edited text and the actual diff are shown to agree | The edited text is shown to agree with the finding |

- Uncertainty on any condition, for any fix, requires the next round for the whole batch.
- Record the self-verification with its reason and evidence: in `reverify` for code, in the new `reconcile-check` for reconcile, in the closing `reverify` of the `challenger` round for Planning.
- A recurring finding can no longer be closed by self-verification.

## 3. Severity

| Level | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| `P1` | Violates an acceptance criterion or contract; a correctness defect, data loss or a security issue | A missing target for a changed behavior or contract, or a reflection that contradicts the implementation or contract | The design fails, or conflicts with an accepted ADR or capability |
| `P2` | A defect with a workaround | An incomplete or imprecise reflection with no contradiction | A defect in how a decision is specified, with a workaround |
| `P3` | An improvement | An improvement | An improvement |

Every finding of a `review`, `reconcile-check` or `challenger` envelope carries `severity` as exactly `P1`, `P2` or `P3`, at every effort (a `low` self-review included). Severity is the reviewer's: the implementer records it as returned, never relabels it, and `reverify` carries it forward. It has no effect on checks; the stage exits still count every open finding.

A reviewer given earlier findings marks a finding that repeats one of them by starting its `issue` with
`recurs: <envelope> #<n>;` (the earlier envelope file and the finding's 1-based position). Recurrence means the same
failure condition remains after an attempted fix, including an incomplete fix, or returns. Explain the shared
failure condition alongside the earlier finding reference; the same file, topic or causal connection alone is
insufficient. The out-of-scope exclusion in section 1 still applies.

- A separate defect the fix introduced is a new finding with its own failure condition, under the same severity,
  minor-fix and round-cap rules. A different proposed remedy does not make an unresolved earlier failure new.
- Example: an earlier finding requires cleanup to check ownership. A fix that still permits deleting another owner's
  work recurs; a fix that checks ownership but calls an unsupported option raises a new finding.

## 4. Bounded recovery

| Cause | Unit path (worker or Host) | Session |
| --- | --- | --- |
| At the cap round, the third after the initial review, the batch does not meet section 2 | `problem` in the `worker` envelope; the recovery names the open findings | Report the open findings; do not integrate |
| The same P1 recurs after its fix (marked `recurs:`) | `problem` in the `worker` envelope | Report the recurrence; do not integrate |
| A P1 the implementer holds invalid, still asserted after one more round given the implementer's counter-evidence (tests or output) | Return the disagreement and evidence as a `problem` for Host resolution | The Host resolves the disagreement against the agreed contract and evidence |

- At the cap round, a batch that fully meets section 2 ends the loop whatever its severity, a minor-fix P1 included.
- At the cap round, any batch that would need another round returns for recovery, P2 and P3 included unless each is waived with a reason.
- The Host owns recovery within the authorized goal, scope and constraints. A round cap, worker return or reviewer disagreement adds no user approval gate. Preserve the failed range, exact head, open findings and attempted remedies; do not restart the loop counter to hide a failed attempt.
- A contested P1 may be closed only with evidence that its failure condition does not apply under the agreed contract. Record that reasoning and verification in `reverify`, or a new `reconcile-check`; unresolved defects remain open. For Planning that is the reverify closing the `challenger` round. Changing an acceptance criterion or waiving an agreed constraint requires the affected user decision, not an implementation-only waiver.
- A Host-directed recovery attempt gets one further fresh round outside the cap, named by its `resolution` envelope. Record the completed attempt and evidence even when it fails. A failed recovery returns to the Host, which chooses a different concrete remedy or reports a genuine blocker instead of starting an unbounded review loop. Never integrate while required findings remain open.
- Ask the user only for missing information the Host cannot obtain, a decision that changes the agreed goal, scope or constraints, or an outstanding main boundary whose effective policy is `ask`. Workers return their evidence to the Host; they do not request business approval for ordinary rework.
- A Planning turn folding answers into an already reviewed proposal treats the fold as a new batch of the same loop, never a fresh loop. When that batch needs recovery at the cap, it gets one further fresh round outside the cap; its summary cites the `answer` envelope in place of a `resolution` when answers caused the recovery. Preserve the count; neither a new worker nor a new session resets the failed history.
- `Decision needed:` findings of a `challenger` stay out of the loop and go to `plan-accept` under its effective policy.

## 5. Planning at `high`

`high` Planning compares two or more options and runs `scout` before the first `challenger`, starting from `devkit spec refs <ID> --direction in` for each capability and ADR the proposal touches, so the `challenger` input cites its list. Each round is a new `challenger-NN` envelope, closed after its fold by a `reverify --from envelopes/challenger-NN.yaml` as at `medium` ([planning](planning.md) step 3); the next round's summary need not restate the dispositions.
