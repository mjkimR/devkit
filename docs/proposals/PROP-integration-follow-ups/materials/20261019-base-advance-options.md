# Base advances: options compared (Planning, 2026-10-19)

Evidence read: `packages/devkit/src/devkit/integration/models.py`, `service.py`, `providers.py`,
`packages/devkit/src/devkit/worktree/lifecycle.py` (`finish`), `packages/devkit-spec/src/devkit_spec/integration.py`,
`CAP-INT-mcp-services`, `ADR-integration-approval-asserted`. Scout and challenger findings are in this proposal's
`envelopes/`.

## Current behaviour (facts)

- `IntegrationRequest.approval_scope()` and `to_dict()` fix `merge_method: "ff-only"`; `finish()` runs
  `git merge --ff-only --quiet <tip>` in the base checkout and raises `WORKTREE_MERGE_NOT_FF` otherwise.
- `providers.policy()` digests the raw bytes of `.devkit/config.toml` and `.devkit/installation.json`; `_validate`
  compares that digest before the merge and `_current_policy_digest()` against `post_policy_digest` after it.
  `installation.json` lists every managed file hash, so any bundle asset edit on the base makes the request stale.
- `_validate` requires `providers.check(provider, request.context) == request.readiness` before the merge;
  `providers.check` requires `Readiness.target_sha == context.finish.target_sha`, and `validate_finish(plan)` checks
  the base still points at `plan.target_sha`. Any base advance is therefore `INTEGRATION_REQUEST_STALE` three ways.
- devkit-spec's provider runs the CI rules on the source tree with the diff from `merge-base(target, source)`; it never
  sees the tree that lands when the base advanced. Unit readiness is read from the source tree.

## E1 merge method

| Option | History | When the base advanced | Envelope SHAs | Notes |
| --- | --- | --- | --- | --- |
| `ff-only` (today) | linear | refused | kept | every advance needs a re-integration in the source and a new confirmation |
| `ff` (merge commit only when needed) | linear or merge, by timing | merge commit | kept | history shape depends on a race; `--first-parent` gains nothing |
| `no-ff` always | one merge commit per unit on `--first-parent` | merge commit | kept | the Backlog leaning; unit stage commits stay reachable and bisectable |
| squash / rebase | one commit / rewritten | new commits | lost or rewritten | breaks every SHA the unit's records cite; not offered for local integration |

Evaluation of the leaning: `no-ff` is the only option whose history shape does not depend on timing, keeps the
records' SHAs (`head`, `diff_scope`, review and reconcile envelopes, decision heads) reachable and ancestors of the
base (so `git branch -d`, `is_ancestor` checks and `WORKTREE_UNMERGED` tests keep working), and gives one
first-parent line per unit. Cost: one extra commit per integration even with no advance, and a merge commit message
devkit must compose. `ff-only` stays useful for a project that requires linear history, so the recommendation is a
`[worktree] merge = "no-ff" | "ff-only"` key with default `"no-ff"`; `ff` is not offered (timing-dependent shape).

## E2 where the merge runs

| Option | Base checkout on conflict | Source branch | First-parent of the base | Tree readiness sees |
| --- | --- | --- | --- | --- |
| A: `git merge --no-ff` in the base checkout | left mid-merge, needs `git merge --abort` | unchanged | base | not checked before it lands |
| B: merge base into the source worktree, then fast-forward the base | never touched | gains a merge commit after approval; the worktree may be in use by a worker | the source side (defeats E1) | the merge commit, if re-checked |
| C: build the merge in the object store (`git merge-tree --write-tree`, `git commit-tree -p <target> -p <source>`), check it, then `git merge --ff-only <merge>` in the base | never sees a conflict (only a fast-forward runs there) | unchanged | base | exactly the commit that lands |

Recommendation: C. It needs Git 2.38 or later for `merge-tree --write-tree`; `commit-tree` runs no commit hooks, so
the merge commit's message must be fixed by devkit and acceptable to the project's commit rules (see scout).
Under `ff-only` the result commit is the source tip itself, so one code path serves both methods.

## E3 to E6 (direction)

- E3: the policy digest covers parsed values devkit owns, not bytes: `[workflow.approvals]`, `[worktree]`
  (`pull_request`, `delete_branch`, `merge`) and `[integration] provider`, computed for the base at confirmation, the
  base at execution and the result commit. Provider, guard and cleanup extension identities stay their own fields.
  Asset hashes are excluded. A path recorded in the receipt (or the receipt itself) changed on both sides since the
  merge base is refused (`fail closed`): the merged bytes would match neither receipt record.
- E4: readiness is re-run at execution against the new target and the result commit. Source-bound evidence must equal
  the approved evidence; target-bound evidence is recomputed and must pass with no reasons. The provider contract
  gains the result commit; devkit-spec runs its CI rules on the result tree with the diff from the current target.
- E5: the form shows the target SHA at confirmation and states that later commits on the target are merged in without
  another confirmation only if the merge is clean, the effective policy is unchanged and readiness passes again.
- E6: at most three attempts per call while the base keeps moving between building the merge and the fast-forward,
  then a refusal with nothing changed on the base; `integration_resume` may try again under the same approval.
