# Review loop at `high`

Read this when an activity runs at `activity-effort` `high` ([effort](effort.md)): Development code review (`code-reviewer`), reconcile verification (`reconcile-reviewer`) and `high` Planning (`challenger`). Stages, checks and gates are unchanged; the loop is procedure above them (`ADR-bounded-high-effort-review-loop`). It is not the `exception` stage.

## 1. Rounds

A round hands a reviewer the whole batch of work since the previous round; the implementer then handles every finding of that round together, whatever its severity.

| Item | Rule |
| --- | --- |
| Round | A fresh reviewer instance, never a continued one. Round 1 reviews the whole change; each later round reviews every fix made since the previous round and what it affects, never a subset. Input: the earlier rounds' findings, the round's diff scope and the effort ([payload](../../spec-delegate/references/payload.md)). |
| Fixing | The implementer fixes every finding of the round, P1, P2 and P3 together (a P2 or P3 may be waived with a reason), and closes the round before the next is recorded: `reverify` for code; a new `reconcile-check` for reconcile; for Planning, the next `challenger-NN` summary or the `worker` envelope's summary, stating what each finding became. |
| Next round | Runs when any fix of the batch fails the minor-fix conditions (section 2). The whole batch goes to the next round. |
| End | The round returns no finding, or every fix of the batch meets section 2 and is self-verified. |
| Round count | Each round's envelope summary starts with `round <N>;` (round 1 is the initial review), and a reconcile check that closes an earlier one also with `closes reconcile-check-<NN>;`. Counts are read from these markers, never from new fields. A `devkit workflow return` does not reset the count: envelopes it leaves out of the checks still count within the segment. |

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
- Record the self-verification with its reason and evidence: in `reverify` for code, in the new `reconcile-check` for reconcile, in the `worker` envelope's summary for Planning.
- A recurring finding can no longer be closed by self-verification.

## 3. Severity

| Level | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| `P1` | Violates an acceptance criterion or contract; a correctness defect, data loss or a security issue | A missing target for a changed behavior or contract, or a reflection that contradicts the implementation or contract | The design fails, or conflicts with an accepted ADR or capability |
| `P2` | A defect with a workaround | An incomplete or imprecise reflection with no contradiction | A defect in how a decision is specified, with a workaround |
| `P3` | An improvement | An improvement | An improvement |

Every finding of a `review`, `reconcile-check` or `challenger` envelope carries `severity` as exactly `P1`, `P2` or `P3`, at every effort (a `low` self-review included). Severity is the reviewer's: the implementer records it as returned, never relabels it, and `reverify` carries it forward. It has no effect on checks; the stage exits still count every open finding.

A reviewer given earlier findings marks a finding that repeats one of them by starting its `issue` with `recurs: <envelope> #<n>;` (the earlier envelope file and the finding's 1-based position).

## 4. Hand-over to the user

| Cause | Unit path (worker or Host) | Session |
| --- | --- | --- |
| At the cap round, the third after the initial review, the batch does not meet section 2 | `problem` in the `worker` envelope; the recovery names the open findings | Reported in the conversation; not integrated |
| The same P1 recurs after its fix (marked `recurs:`) | `problem` in the `worker` envelope | Reported in the conversation; not integrated |
| A P1 the implementer holds invalid, still asserted after one more round given the implementer's counter-evidence (tests or output) | `questions` entry with the reviewer's and the implementer's positions as options | Asked in the conversation |

- The cap only limits further rounds. At the cap round a batch that fully meets section 2 ends the loop whatever its severity, a minor-fix P1 included; any batch that would need another round is handed over, P2 and P3 included unless each is waived with a reason. No fix leaves `high` unreviewed unless it is provably minor.
- A P1 the user rules invalid is closed with `reverify --waive <N>=<reason>` citing the `answer` envelope: the only waiver a P1 may carry. For reconcile and Planning the same goes into the new `reconcile-check` or the `worker` summary.
- When the user resolves a cap or recurrence problem by asking for a fix, that fix gets one further fresh round outside the cap, named by the `resolution` envelope. Its outcome follows the rules above; a recurrence of the same P1 hands over again.
- `Decision needed:` findings of a `challenger` stay out of the loop and go to `plan-accept`.

## 5. Planning at `high`

`high` Planning compares two or more options and runs `scout` before the first `challenger`, starting from `devkit spec refs <ID> --direction in` for each capability and ADR the proposal touches, so the `challenger` input cites its list. A `challenger` envelope has no reverify: each round is a new `challenger-NN` envelope. The `plan-accept` request names a missing `scout` envelope at `high` as it does a missing `challenger`.
