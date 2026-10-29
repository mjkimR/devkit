# Activity branches: start, continue, leftovers and stale branches

Read this to start an activity's branch without a worktree, continue an existing branch, or report leftover and stale branches in `/spec-next`. Worktree start and finish: [worktree](worktree.md).

## 1. Names

- Proposal Planning runs on `plan-<slug>`; proposal Development and a `session` task bound for a PR on `dev-<slug>`. Pass the full branch name to every `devkit worktree` command.
- One slug's activity runs in one place only: continue an existing branch (§3), never start it again.

## 2. Branch only (`direct`, no worktree)

- Start with `devkit worktree start <branch> --no-worktree`; it switches this checkout and carries uncommitted changes.
- Integrate from the base branch: `git switch <from>`, then `devkit worktree finish <branch> --merge` (or the PR path). On `WORKTREE_CONFLICT` (finishing from a third branch), ask the user before switching: that checkout is someone's work in progress.

## 3. Continue an existing branch

Resuming after a stop, switching an activity's mode and handing an inline-Planned `dev-<slug>` to a worker or cloud run all continue the branch:

```bash
devkit worktree start <branch> --existing-branch <branch|remote/branch> --unit <dir>
```

- `<dir>` on `plan-<slug>` is `docs/proposals/PROP-<slug>`; on `dev-<slug>` the spec bundle, or the accepted proposal before handoff. The run continues from the stage `devkit workflow next --unit <dir>` names.
- Fetch first to see a branch made elsewhere. Synchronize a behind or diverged branch with the user, never by reset.
- Continue a branch only once its earlier run ended; before taking a cloud run's branch local, confirm its pull request has no active run.
- To cite by ID a document added to the base after the branch started, merge the base into the branch first; otherwise name its slug without the ID prefix.

## 4. Leftovers and stale branches

From `devkit worktree status`:

- Clean a linked worktree with `merged=yes dirty=no` with `devkit worktree finish <branch>`.
- Remove anything else (`merged=no`, `dirty=yes`, `dirty=-`, `prunable=yes`, a `[BRANCH]` line) only with the user's authorization; drop an unmerged activity branch only with `devkit worktree finish <branch> --discard`.

Report each `[STALE_BRANCH: ...]` from `devkit worktree status --stale` with both paths, taking neither unasked:

- **Resume** with the printed `--existing-branch` command. When its unit is `-`: `plan-<slug>` → `docs/proposals/PROP-<slug>`; `dev-<slug>` → the spec bundle whose path matches `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/spec.md` exactly in `git ls-tree -r --name-only <branch> -- specs` (`-login` never matches `...-user-login`), else the accepted proposal.
- **Discard**, once the user decides: close its pull request, run the printed `--discard` command, and for an accepted proposal follow a [close](depth-and-close.md).
