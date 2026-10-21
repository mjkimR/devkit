# Classification, Backlog, depth changes and close

## 1. Classify (Backlog)

Decide in this order and state the result. Record the authorized intent at `plan-intent`; an existing explicit task instruction needs no repeated confirmation. Choose activity effort within that intent, preserving explicit user choices and required review.

| Axis | Values | Criterion |
| --- | --- | --- |
| `task-kind` | `feature` (default), `bugfix` | `bugfix` only for a defect against an agreed contract; it adds the characterization (spec depth) and the Red then Green evidence. Provisional until `plan-accept` or the spec Unit's creation. |
| `planning-depth` | `session`, `spec`, `proposal` | What must be settled before implementation, not size. Nothing (no design choice, no contract impact, verifiable in the session): `session`. The contract, with a clear direction: `spec`. The direction, with options to compare: `proposal`. Large but clear work is `spec`; small work whose direction is open is `proposal`. |
| `activity-effort` | `low`, `medium` (default), `high` | How thorough the activity's review and verification are ([effort](effort.md)); none for Backlog and inline Planning. Never lowers gates, exit checks or `required` policies. |

- **Backlog is `direct`** and follows [repository Backlog](backlog.md). State effort hints with `plan-intent`; record actual user instruction with `devkit workflow answer --by user` without inventing a new approval. Commit only the draft and its intent record before starting Planning from the base HEAD.
- **A request requiring independently delivered outcomes is decomposed first**: decompose it into drafts ([repository Backlog](backlog.md)). A `needs_decompose` draft never starts Planning; one proposal hands off to one spec.
- **A queued draft may skip Planning or the Unit, within the authorized scope**: a settled direction by a direct acceptance, `session`-depth work by the session reclassification at pickup ([repository Backlog](backlog.md)).
- **Draft proposals may be added from any activity**, outside the worktree and PR `required` policies, in the current checkout; a follow-up found during other work is feedback by default, a draft is also allowed. Backlog changes only a `draft` that Planning does not own ([repository Backlog](backlog.md); stop on `SPEC_PROPOSAL_IN_PLANNING`).

## 2. Inline Planning (`session`, `spec`) and the problem rule

- **`spec`**: start `dev-<slug>` and the Unit per [worktree](worktree.md) §1 (`--no-worktree` when `GIT_POLICY` needs no worktree, [branches](branches.md); `devkit spec new` is refused off `dev-<slug>`), agree the intent with the user, record `plan-intent`, commit. That committed state is Development's input; a worker or cloud run continues the branch (`--existing-branch dev-<slug> --unit <dir>`, [branches](branches.md) §3).
- **`session`**: agree the intent in the conversation, no Unit. With a PR the work runs on `dev-<slug>`, else on the current branch (on the base under `ask` integration: `dev-<slug>` or the OK first). A `session` task runs in `direct` or the `cloud-pr` general PR path only; in `local-orchestrated` handle it yourself in `direct`.
- **Split work for execution, not extra approval.** Keep one cohesive unit when its outcome can be implemented and verified together. Sequence shared contracts and conflicting files; parallelize independent scopes; use separate units for independently delivered outcomes. The Host chooses implementation tasks, subagents, review and rework within the agreed scope. A worker return or stage boundary does not require user acceptance. Preserve committed heads, unresolved work and recovery state when pausing or resuming. Request a new decision only at an `ask` approval boundary not already authorized, or when the agreed goal, scope or constraints must change.
- **Development decides inside the agreement.** A choice inside the agreed goal, scope and contract takes the recommended option and is recorded. Only a problem that cannot be solved without changing the agreement, or at all, stops the work: a worker records it and you resolve it per [worker records](worker-records.md) §3; a `session` task reports it in the conversation or the cloud run's problem report and does not integrate. A change of scope needs the user and a close (§4).

### Source feedback at entry

When the agreed work addresses named feedback, record its full FB IDs and the intended scope in a `Source feedback`
section of the proposal/spec body; for a session keep them in the agreed conversational scope (no new file).
Keep that section when drafting a handed-off spec: handoff carries proposal body references and never resolves them.
Resolve open direct-fix sources to actual files before planning boundaries and include paths needing completion
updates in delegated write scope. Terminal sources remain traceability and require no completion edits. Do not infer sources from a matching target alone. Follow
[Source feedback resolution](completion.md#source-feedback-resolution) at completion.

## 3. Raising the depth

Raising is yours to decide (`[ROUTING_POLICY: depth_escalation=auto]`); under `ask` confirm it with the user first. Lowering never happens except through a proposal's handoff (after `plan-accept`, a direct acceptance included) or the session reclassification of a queued draft by the Host within the authorized scope at pickup ([repository Backlog](backlog.md)); a proposal in review or accepted and a spec Unit are never lowered. Workers and Cloud Agents never raise it: they report the need as a problem.

- Before Development: change the classification only.
- **`session` → `spec` during Development** keeps the work, with no close, new slug or new worktree: add a spec Unit in the current work environment (`devkit spec new <slug>` on `dev-<slug>`; without that branch, first `devkit worktree start dev-<slug> --no-worktree` in this checkout, which keeps the uncommitted work), record the agreed intent and the work so far, and continue from the workflow's next stage. Ask the agreement again only if goal or scope change; record `plan-intent` on the strength of the session's approval: `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user --note "approved in the session; depth session -> spec: <reason>"` (under `depth_escalation = ask`, name the user's confirmation too). Raise it when a lasting design record, a contract change or a Living Spec change is needed; a higher review effort alone never raises the depth.
- **To `proposal`** (the direction must be decided first) is a close by depth escalation (§4).

## 4. Close (end Development without a merge)

Development never returns to Planning. Only a party that can talk to the user closes; a worker or Cloud Agent leaves a problem instead.

| Close | When | Steps | Who decides |
| --- | --- | --- | --- |
| Depth escalation | A `session` or `spec` task needs its direction decided first | Add a draft proposal under a **new slug**, carrying what the attempt learned in its `materials/`; close its dev PR and drop its branch if it has them | You (`depth_escalation = ask`: the user confirms) |
| Supersede | An accepted proposal's direction is wrong | Add a draft proposal under a new slug with `--supersedes PROP-<old>` and the attempt's material in `materials/`; delete the old accepted proposal from the base in the same commit; close the dev PR and drop the branch | The user: it reverses `plan-accept` |
| Abandon | The accepted work is dropped | Write a rejection ADR and delete the accepted proposal from the base; close the dev PR and drop the branch | The user |

- **Drop the branch with `devkit worktree finish dev-<slug> --discard`** from the base checkout, on the table's decider's authority, once what it learned is copied out: it removes the worktree (refused while it has uncommitted changes, never forced), deletes the unmerged branch (`git branch -D`, the only place it is allowed) and releases the scope record. Close the remote branch and PR yourself (`gh pr close`, `git push <remote> --delete dev-<slug>`).
- A close commit is Backlog work, committed to the base directly. A new draft starts over: `plan-intent` again in Backlog, then a new Planning.
- A rejected proposal (status only, the user's reason in the commit message) is cleaned up by a later hygiene pass (`SPEC_PROPOSAL_REJECTED_PENDING` in `devkit rules check -p hygiene`): a rejection ADR outside the proposal directory, referencing the proposal and the rejection commit, with the proposal deleted in the same commit. The rejection commit closes open questions ([worker records](worker-records.md) §2).

Before deleting any proposal, follow [feedback retirement](feedback-retirement.md).


Before direct-spec intake or explicit proposal pickup, inspect optional unit depends_on using the single local
base snapshot procedure in `spec-next/references/next-work.md`, even when idle selection is not running. Record an
explicit order override's unsatisfied IDs/reasons in the ordinary intent decision; do not waive malformed
references or cycles. Before supersede, reject, delete or session reclassification, follow Backlog's per-dependent
incoming prerequisite disposition in the same authorized change; provenance never selects successors.
