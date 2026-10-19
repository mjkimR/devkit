# Worktree procedure

Read this before work that runs in a task worktree: every `spec` and `proposal` activity in `direct` mode under `[GIT_POLICY: worktree=required ...]` (`[tool.spec] worktree`), and any task the `GIT_POLICY` levels in [git policy](git-policy.md) put in a worktree under `auto`, from the first step to the cleanup after merge. A request that names the checkout ("on main", "in this worktree") overrides the policy for that task only; record the deviation as a user request, without its wording, in the final change report's assumptions.

Policy is read from the checkout a command runs in, so a running branch sees a base policy change only after merging the base. `devkit worktree` performs the deterministic steps; the session only changes directory. `<base>` is the checkout the request arrived in; `<branch>` is the activity branch, `plan-<slug>` or `dev-<slug>` ([branches](branches.md)). The worktree is created from the base HEAD; the base working tree is never touched. On a setup or sync warning from `start`, run its `[FIX]` before any work.

## 1. Start (in `<base>`, before any bundle or edit)

- `proposal` depth, Planning: `devkit worktree start plan-<slug>` and the printed `cd`; the proposal bundle is the unit.
- `proposal` depth, Development: once the accepted proposal is merged into the base, run `devkit worktree start dev-<slug>` and the printed `cd` (or `--no-worktree`, which switches the base checkout), then hand off **on** `dev-<slug>` as Development's first step: `devkit spec proposal handoff <slug>` (refused on any other branch; run any `[FIX]` it prints), then check the proposal's premises against the current base. The base keeps the proposal until the merge.
- `session` depth bound for a PR: the `dev-<slug>` branch, in a worktree (`devkit worktree start dev-<slug>` and the printed `cd`) only when the `GIT_POLICY` levels call for one, else with `--no-worktree`; no bundle.
- `spec` depth (inline Planning): `devkit worktree start dev-<slug>`, the printed `cd`, then `devkit spec new <slug>` (`--workflow sdd-spec-bugfix` for a defect), which creates and binds `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`, then `devkit spec scope register --spec <dir>` (linked worktrees only), record `plan-intent` and commit: that state is Development's input.
- A refused `start` changes nothing. For `WORKTREE_BRANCH_EXISTS` (the branch exists locally or on a remote, also with its worktree registered) continue it ([branches](branches.md) §3, which reuses the worktree) or choose another slug.

## 2. Work (in the worktree)

- Run the stages (`spec-specify`, `spec-plan`, `spec-tasks`, build, `spec-review`, `spec-sync`), checking each stage boundary with `devkit workflow next --unit <dir>`. `spec-tasks` and `spec-sync` run `devkit spec scope update --spec <dir>`; `devkit spec scope query` shows other tasks' overlaps, which inform scheduling and integration order, never block.
- Commit on `<branch>` in this worktree at every stage boundary (`git commit`; the commit gate runs there). Nothing is pushed to the remote or merged into the base before `dev-integration`; preparing and checking the branch against the local base may precede native approval.

## 3. Request native approval, integrate and finish (in `<base>`)

Authority for each path is the [completion policy](completion.md#policy).

- `devkit worktree finish` and `integration_integrate` run devkit-spec's post-finish cleanup in the base. Run a failed cleanup's `[FIX]` in the base once its cause is resolved (or `integration_resume` when `integration_integrate` stopped in `status: "partial"`). On `POST_FINISH_EXTENSION_FAILED` run both by hand: `devkit spec scope sweep --apply` and `devkit spec proposal prune <slug>`. A refused finish runs no cleanup, so the task stays registered; `devkit spec scope release -w <worktree path>` withdraws an abandoned task.
- A conflict in `.devkit/installation.json` when integrating the base (two tasks re-synced bundle assets): keep either side, run `devkit sync`, stage the receipt it writes.
- Local merge (`pull_request=auto`, no PR):
  - **MCP path (primary when `devkit` MCP tools are available)**: after branch preparation, verification and the final report, call `integration_integrate` with `branch`, `task_kind="unit"`, `task_id` and `unit` (session tasks: `task_kind="session"`, `task_id` and `claims`). It verifies the exact scope, confirms natively, fast-forwards the base locally (no fetch, push or PR) and finishes the worktree. `integration_prepare` is an optional read-only preflight; inspect a run with `integration_status(request_id, detail=true)` and resume a `partial` one with `integration_resume`.
  - **CLI fallback / manual recovery** (`INTEGRATION_CONFIRMATION_UNAVAILABLE`, or invoked directly after `dev-integration` approval): `devkit worktree finish <branch> --merge --local-only`, or without `--local-only` to also fetch the base's upstream and push the base (never forced). It refuses a branch whose units hold an unresolved problem or unanswered question (`WORKTREE_BLOCKED`, [worker records](worker-records.md)). Follow the `push=` field of `[WORKTREE_FINISHED: ...]` and any `[FIX]`; on `push=no-upstream` report that nothing was pushed. Then run `devkit rules check --ci --base <merge-base>` on the result and assert the runner checks yourself, since no CI runs without a PR: `devkit workflow next --unit <dir> --given dev-integration --given lint-ci-clean --given merged`.
- Through a PR (`pull_request=required`, or chosen under `auto`): push `<branch>`, open the PR and let it merge only while `devkit workflow envelope check --unit <dir> --format json` on its head reports `"blocked": false` and no `pending_questions`; after the merge run `devkit worktree finish <branch>` (no `--merge`). The merge test is an ancestor test, so a PR merged by squash or rebase stays `WORKTREE_UNMERGED`: remove that worktree and branch only with the user's authorization.
- A refusal names its cause and `[FIX]` and leaves earlier steps done; the same command resumes once it is resolved. `WORKTREE_MERGE_NOT_FF`: integrate the base into the branch (`spec-integrate` Step 1). Never remove a dirty worktree by force (`WORKTREE_DIRTY`: commit or discard in the worktree). Unlock a `WORKTREE_LOCKED` worktree only once the user agrees. `WORKTREE_NOT_FOUND` for a merged branch devkit did not create: delete it (`git branch -d <branch>`) only with the user's agreement.

## Leftovers

Leftover worktrees and branches, and stale activity branches: [branches](branches.md) §4.
