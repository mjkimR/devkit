# Review loop at `high`

Read this when code review (`code-reviewer`), reconcile verification (`reconcile-reviewer`) or Planning criticism (`challenger`) runs at `activity-effort` `high`. The loop changes no stage, check or gate.

## 1. Rounds

| Item | Rule |
| --- | --- |
| Round | A fresh reviewer instance, never a continued one. Round 1 reviews the whole change; each later round reviews every fix since the previous round and what it affects. Pass the earlier rounds' findings and the round's diff scope ([payload](../../spec-delegate/references/payload.md)). |
| Fixing | Fix every finding of the round together (waive a P2 or P3 only with a reason), then close the round: `reverify` for code, a new `reconcile-check` for reconcile, `reverify --from envelopes/challenger-NN.yaml` for Planning. A P1 you hold invalid stays open in that record with counter-evidence (tests or output). |
| Next round | Runs on the whole batch when any fix fails section 2 or a contested P1 stays open. |
| End | The round returns no finding, or every fix of the batch meets section 2. |
| Count | Each round's summary starts with `round <N>;` (round 1 is the initial review); a reconcile check that closes an earlier one adds `closes reconcile-check-<NN>;`. Each kind counts separately. An unmarked round counts only when it precedes the first marked round and the segment's `worker` envelope records `activity_effort: high`; when counts disagree, the higher holds. A `reverify` is never a round, and `devkit workflow return` does not reset the count. |

Round 1 is never replaced by a self-check. A finding whose `evidence` path is outside the round's diff is fixed with the batch and never counts as a recurrence.

## 2. Minor-fix self-verification

A batch MAY skip the next round only when every fix meets all four conditions:

| Condition | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| Location | Only the location the finding's `evidence` names | Only the document or entry the finding names | Only the proposal section the finding names |
| Nature | Typo, comment, formatting, in-scope rename, test-only addition, or a concrete `suggested_action` applied as written | Wording only, or a concrete `suggested_action` applied as written | Wording only, or a concrete `suggested_action` applied as written |
| Contract | No public API, schema, error code, CLI output or other package touched | The contract's meaning is unchanged | No decision changed |
| Evidence | Behavior fixes: a test reproducing the `failure_condition` passes (for a P1, it failed before the fix). Text-only: the diff is limited to the named location | The edited text and the actual diff agree | The edited text agrees with the finding |

If any condition is uncertain for any fix, run the next round for the whole batch. Record the reason and evidence in the record that closes the round. A recurring finding cannot be self-verified.

## 3. Severity

| Level | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| `P1` | Violates an acceptance criterion or contract; a correctness defect, data loss or a security issue | A missing target for a changed behavior or contract, or a reflection that contradicts the implementation or contract | The design fails, or conflicts with an accepted ADR or capability |
| `P2` | A defect with a workaround | An incomplete or imprecise reflection with no contradiction | A defect in how a decision is specified, with a workaround |
| `P3` | An improvement | An improvement | An improvement |

Every `review`, `reconcile-check` and `challenger` finding carries one level, at every effort. The reviewer sets it; the implementer never relabels it. Severity changes no check: stage exits count every open finding.

A reviewer marks a finding that repeats an earlier one by starting its `issue` with `recurs: <envelope> #<n>;` (the earlier file and the finding's 1-based position). Recurrence means the same failure condition survives an attempted fix or returns; a shared file or topic is not enough, and a new defect the fix introduced is a new finding. Example: a fix that still lets cleanup delete another owner's work recurs; a fix that checks ownership but calls an unsupported option is new.

## 4. Bounded recovery

| Cause | Unit path (worker or Host) | Session |
| --- | --- | --- |
| The cap round, the third after the initial review, ends with a batch that fails section 2 | `problem` in the `worker` envelope naming the open findings | Report the open findings; do not integrate |
| The same P1 recurs after its fix | `problem` in the `worker` envelope | Report the recurrence; do not integrate |
| A contested P1 is still asserted after one more round with your counter-evidence | `problem` with the disagreement and evidence | The Host resolves it against the agreed contract |

- The Host owns recovery within the authorized goal, scope and constraints; recovery adds no user approval gate. Preserve the failed range, head, open findings and attempted remedies, and never reset the count.
- Close a contested P1 only with evidence that its failure condition does not apply under the agreed contract. Changing an acceptance criterion or waiving an agreed constraint needs the user's decision.
- A Host-directed recovery gets one further fresh round outside the cap, named by its `resolution` envelope (for a Planning fold of answers, by the `answer` envelope). If it fails, choose another remedy or report a blocker. Never integrate while required findings remain open.
- Ask the user only for information the Host cannot obtain, a change to the agreed goal, scope or constraints, or a main boundary whose policy is `ask`.
- A Planning turn that folds answers into a reviewed proposal continues the same loop with a new batch; a new worker or session resets nothing.
- `Decision needed:` findings of a `challenger` stay out of the loop and go to `plan-accept`.

## 5. Planning at `high`

Compare two or more options and run `scout` before the first `challenger`, starting from `devkit docs refs <ID> --direction in` for each capability and ADR the proposal touches, so the `challenger` input cites the list. Each round is a new `challenger-NN` envelope, closed after its fold as in [planning](planning.md) step 3.
