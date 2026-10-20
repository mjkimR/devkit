# Pull request merge and race options

Evidence: `envelopes/scout-01.yaml` (local `gh` 2.96.0 help verified; GitHub REST, protection, ruleset and merge
queue behaviour unverified, no network in this Planning).

## Platform facts used

- `gh pr merge` offers `--merge`, `--match-head-commit <sha>` (head must match), `--subject`, `--body`, `--auto`,
  `--admin` and `--delete-branch` (local and remote). Nothing pins the base.
- `gh pr view --json` exposes `state`, `headRefOid`, `baseRefOid`, `mergeCommit`, `mergeStateStatus`,
  `statusCheckRollup`, `isCrossRepository`; `gh repo view --json` exposes `mergeCommitAllowed`,
  `deleteBranchOnMerge`; `gh ruleset check <branch>` lists the rules that apply.
- On GitHub a PR merge commit has the base tip at merge time as first parent and the PR head as second.

## Options

| Option | Source pinned | Target advance | Result checked | PR gate kept | Cost |
| --- | --- | --- | --- | --- | --- |
| A: check prospective merge, merge with head pin, verify landing | server-side | tolerated within the call; residual window between last check and merge | before (prospective) and verified after (parents, tree) | yes | residual race, detected not prevented |
| B: platform "up to date" rule | server-side | every advance refuses; new approval | equals source tree | yes | a repository setting devkit cannot impose; contradicts the settled advance tolerance |
| C: push local merge commit to target with lease | exact | exact compare-and-swap | exactly | no (bypassed or refused by protection) | defeats the route's purpose |

Selected: A (`decisions/PADR-pull-request-merge-with-pinned-source-and-verified-landing.md`).

Refined by the user's answers (`envelopes/answer-01.yaml`): A merges only when required checks and reviews already
pass, otherwise it publishes and returns `INTEGRATION_CHECKS_PENDING` for a resume onto the unchanged target; after
the merge the landing is classified, not re-checked, and an unchecked landing is a notice that does not hold cleanup.

## Platform abstraction

| Option | Pros | Cons |
| --- | --- | --- |
| Entry-point provider group | ready for a second platform | no second platform exists; more contract surface |
| `gh` behind a port in `devkit.worktree` | follows `run_gh`/`GhRunner`; testable offline; layering-safe | GitHub only |
| Direct REST with a devkit-read token | no `gh` dependency | devkit would own credentials |

Selected: the `gh` port (`decisions/PADR-github-pull-request-adapter-in-devkit-worktree.md`).
