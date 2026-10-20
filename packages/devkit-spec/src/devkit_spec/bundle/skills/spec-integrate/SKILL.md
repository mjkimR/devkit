---
name: spec-integrate
description: Integrate a verified branch by merging the base, re-verify what changed, confirm reconcile, run the cumulative check, then merge via native MCP approval, CLI or PR.
---

# spec-integrate: Integration Preparation, Approval and Merge

Use this skill to prepare the local MCP integration before its single native approval, or once CLI/PR `dev-integration` authorization exists. Read `devkit spec policy` and the `spec` skill's [completion policy](../spec/references/completion.md#policy) first: it defines the `ask`/`auto` authority, the native confirmation as the OK and `--given dev-integration` (never recorded) on every later `devkit workflow next --unit <dir>`, which then names this stage (`integrate`). Integration is a stage, not a persona: the main-session Developer runs it, or an agent an external runner delegates. Stage definition: `devkit workflow show --unit <dir>`.

---

## 1. Entry conditions and inputs

- Implementation, review and fixes complete; implementation checks passed. The native MCP path may prepare the branch and request its approval while `gate:dev-integration` is waiting; CLI/PR execution requires existing `dev-integration` authorization. Never assert native acceptance before the form returns it.
- Inputs: the approved change and its spec directory, the review envelope and check results, docs impact and reconcile targets, the current base branch.
- `reconcile.md` is already `resolved` and the spec `completed` before `dev-integration`. A pending record carried by intermediate commits does not satisfy this condition or the final cumulative check.

## 2. Authority

| Scope | Allowed | Not allowed |
| :--- | :--- | :--- |
| Code | Conflict resolution needed to integrate the approved change with the base, and the fixes and verification that resolution requires | New features, refactors, lowering AC, documenting a defect instead of fixing it |
| Docs | Capability, story, architecture and ADR reflection the approved change requires; `reconcile.md` record | Adopting a new policy (separate decision), editing other features' specs |
| Git | Stage agreed paths; `git commit` (the commit gate runs the staged checks) | Bypass flags (`--no-verify`), `git add .`, force operations |

Trust the prior review: do not restart code review. Re-verify only what conflict resolution and docs reflection changed.

---

## 3. Procedure

In a worktree (the `spec` skill's `references/worktree.md`): Steps 1 to 4 run there, Step 5 merges into the base checkout, and Step 6 cleans up only after the merge is confirmed.

### Step 1: Integrate the base branch
For local MCP integration, use the current local base without fetching or pushing; fetch/pull only with existing network authorization on a path that needs it. This preparation grants no authority to advance the base or delete anything.

```bash
git merge -m "<subject the commit-msg gate accepts>" <base-branch>   # the base checkout's branch (it may be ahead of origin)
```
Merge, never rebase: the unit's records cite its commit SHAs. Step 1 is required before `prepare` when the branch does not contain the target, and again after an integration refused on a later target (`WORKTREE_MERGE_CONFLICT`, `INTEGRATION_RECEIPT_CONFLICT`, readiness on the merged result); target commits that land during the native confirmation are merged in by the approved call itself.
Resolve conflicts within the approved intent. A conflict that needs a design choice the agreed intent does not cover is a problem for the Host: stop and hold the PR.

### Step 2: Re-verify what changed
- When bundle sources changed, the Host runs official `devkit sync` in the integration worktree after incorporating
  the latest base, inspects and commits the resulting tracked receipt/projection changes, then verifies that final
  content before requesting integration approval. Workers report changed source assets; this grants them no
  `.devkit/` write exception. A sync failure leaves preparation incomplete.
- After incorporating a moved base or resolving conflicts, inspect all resulting changes (`git diff --name-only <pre-merge-head> HEAD`), including a clean merge's incoming changes.
- Verify the final integration content under the repository's test policy (e.g., `just test-affected --base <base-ref>`), plus checks covering the changed paths. Run `spec-review` Step 1 and Step 3 on the changed part only; preserve selector fallbacks and frontend checks.
- A defect beyond integration scope returns to the Developer (the build stage: `build-verify`, or `fix-verify` in `sdd-spec-bugfix`); integration is not reported complete.

### Step 3: Confirm reconciliation
- Re-check `reconcile.md` targets against the impact after conflict resolution; add targets if resolution touched contracts, and apply the docs reflection they require.
- Confirm `status: resolved` only when every target is in the comparison diff or has a substantive waiver (never for a required contract mismatch), and `spec.md` `status: completed` (set by `spec-sync`).
- On a shared checkout, write and commit shared Living Spec files in integration order, one at a time. If the index or HEAD changed during a check, re-run the check.

### Step 4: Final checks
```bash
devkit rules check --ci --base <base-ref>    # cumulative Git evidence, merge-base..HEAD
```
plus the repository's required local checks (tests, types and lint). Reuse valid results for unchanged content; do not repeat the full suite solely because this is integration. A merge of the same verified content needs no post-merge test run; changed base or content requires fresh affected checks. Nightly/release CI follows repository policy. A plain `devkit rules check` does not count. Unresolved reconciliation means no merge.

### Step 5: Report, obtain native approval if applicable, merge and hand over
Before requesting native approval, present the verified change report and the intended merge/cleanup effects. After execution, give the integration result report (the `spec` skill's `references/envelope.md`, section 4) in the conversation, not as a file: base integrated, conflicts resolved, what was re-verified, the Step 4 result and the actual `dev-integration` authority. State code review completed (latest review round or reverify) and integration completed as separate facts, each only when it has occurred. Repository CI re-runs the cumulative check as `lint-ci-clean` (`[WAITING: runner lint-ci-clean]`); without a PR there is no CI run: after the local check passes, declare it (`--given lint-ci-clean`) and say so in the report.

Who merges follows the policy. Through a PR (`pull_request=required`, or chosen under `auto`), call native
`integration_integrate` with `route="pull-request"` and the same task fields below. Its single form covers push,
PR create/use, pinned no-ff merge, fetch, local fast-forward and selected cleanup; no prior publication authority is
inferred. An already-published ready PR may merge in this call. `INTEGRATION_CHECKS_PENDING` is incomplete success:
wait for checks with the returned bounded-watch directive, then resume on the unchanged checked target. Report a
required check that never starts. `INTEGRATION_TARGET_MOVED` returns to Step 1, re-verification and new approval;
report repeated movement to the user. On `INTEGRATION_LANDED_UNCHECKED`, cleanup still runs: execute the declared
landed-target check in the retained base (`devkit rules check` for spec), report the landing as unchecked, and fix a
failure in a new unit. A timeout or unknown mutation requires `integration_status` before recovery. A process restart
requires fresh preparation/approval; no file restores authority. Without native confirmation, use the existing
manual PR path only under separately existing push/merge authority, with envelope check unblocked on its head.
For a local merge (`pull_request=auto`, no PR):
- **Primary path (`devkit` MCP tools available)**: call `integration_integrate` directly from the base checkout with `branch`, `task_kind="unit"`, `task_id` and `unit` (a session task: `task_kind="session"`, `task_id` and `claims`), without a chat approval first; `integration_prepare` is an optional read-only preflight. After native acceptance pass `--given dev-integration` to later workflow checks; a decline or cancel leaves integration unapproved. The task lands as a merge commit (`[worktree] merge = "ff-only"`: a fast-forward); target commits that land during the confirmation are merged in when the merge is clean, the integration policy is unchanged and readiness passes again on the merged result, where the spec provider runs the CI rules only: tests and review ran on the source only, and the integration report says so. On `status: "partial"`, inspect with `integration_status` (`detail=true` for full evidence) and resume with `integration_resume`, which continues only onto the target its approving call built on; a later target needs a new `integration_integrate`. `INTEGRATION_CONFIRMATION_UNAVAILABLE` falls back to the CLI path.
- **Fallback / manual CLI**: with the user's conversational `dev-integration` OK, run `devkit worktree finish <branch> --merge --local-only` (without `--local-only` when remote fetch/push is wanted) in the base checkout and follow the `[FIX]` of any refusal (`WORKTREE_BLOCKED`: resolve the problem; a moved base, `WORKTREE_MERGE_NOT_FF`: Step 1). It lands a merge commit built from the base HEAD and the branch, or a fast-forward under `merge = "ff-only"`. Rerun the cumulative check on the result; with no runner to report the merge, declare it (`devkit workflow next --unit <dir> --given dev-integration --given lint-ci-clean --given merged`). If head, base or approval changed before the merge, return to Step 1.

### Step 6: Clean up after the confirmed merge
- After bundle changes land, the Host runs official `devkit sync` in the base checkout to refresh its installed
  projections, checks the result and reports any failure. It inspects any unexpected tracked change before further
  integration; synchronization is not permission for unrelated modifications.
- `integration_integrate` has already cleaned up when it completed (`integration_resume` when `partial`).
- On the CLI path (after a PR merge or a manual local merge), run `devkit worktree finish <branch>` in the base checkout (`--merge`, optionally `--local-only`, when the local merge is still to be done). Follow the `[FIX]` of each refusal or warning (finish, push and post-finish cleanup codes; the `spec` skill's `references/worktree.md`) and rerun the same command once it is resolved. Report what could not be removed or pushed and why.

### Returns
- Design choice the agreed intent does not cover → a problem for the Host.
- Implementation defect beyond integration scope → Developer (the build stage).
- Retry cap exceeded, tool or execution failure, unresolved semantic conflict → `exception`: hold the work, report cause and evidence. Do not create a new task to bypass a cap.
