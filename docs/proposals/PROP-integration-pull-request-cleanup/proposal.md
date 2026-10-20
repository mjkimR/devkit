---
id: PROP-integration-pull-request-cleanup
title: Integration through pull requests with no-ff merge and cleanup
summary: "Defines one approval for push, no-ff PR merge and cleanup, fixing the source SHA while allowing checked target advances. Reports partial completion and actionable failures for agent-led recovery."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - integration/
    - worktree/
    - packages/devkit/src/devkit/integration/
    - packages/devkit/src/devkit/worktree/
    - packages/devkit-spec/src/devkit_spec/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-pull-request-cleanup] Integration through pull requests with no-ff merge and cleanup

- **Split from**: `PROP-integration-follow-ups` (its question Q3), split during that proposal's Planning, which kept
  only the base advances. Created without `decomposed_from`: `devkit spec proposal new --decomposed-from` refuses a
  source in Planning (`SPEC_PROPOSAL_IN_PLANNING`).
- **Source feedback**: `FB-pr-remote-and-squash-integration`.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`,
  `ADR-branch-guards-and-close-discard` (supersedes `ADR-worktree-and-pull-request-levels`).

## 1. Background & Hypothesis

`SPEC-hook-driven-integration-cleanup` shipped local, approval-bound integration and deferred remote work (its
Non-Goal 3). The integration service forbids network operations, refuses `[worktree] pull_request = "required"`
(`WORKTREE_PR_POLICY`) and executes only local merges.

`PROP-integration-follow-ups` defines local integration with merge commits (`[worktree] merge = "no-ff"` by default).
This proposal uses the same no-ff history shape for pull request integration: the target receives a merge commit
and every source SHA cited by the unit's records stays reachable as an ancestor of the target.

Hypothesis: remote push and pull request merge can get their own explicit authority, separate from local-only
integration, and verified PR merge state plus source ancestry in the fetched target can authorize cleanup without
removing unmerged work.

## 2. Planning Scope

The direction is settled: one approval covers the complete PR integration, the merge method is no-ff, target
advances follow the local integration principles of `PROP-integration-follow-ups`, and the agent handles failures
from actionable operation results. Planning specifies the implementation within these decisions:

- Bind the remote repository, PR identity, source/target branches and cleanup targets into the approval request.
- Define the remote checks that enforce the approved source SHA, target ancestry, unchanged effective policy and
  readiness on the merge result, including platform limitations and races.
- Apply `pull_request = "required"` and `ADR-branch-guards-and-close-discard`; refuse this route when project or
  platform policy forbids no-ff merge commits, including an applicable `ff-only` constraint.
- Identify any ADR change needed to permit remote operations under the existing approval contract.

## 3. Proposed Design & Impact

### 3.1 One approval for the complete operation

One approval MUST cover the disclosed remote and local scope: push the approved source branch, create or update its
PR, merge it with a no-ff merge commit, fetch and fast-forward the local target, then remove the linked worktree,
local source branch, remote source branch and package-owned scope records as permitted by the effective cleanup
policy. Remote branch deletion is part of that same approval when selected, not a separate approval step. The form
MUST disclose the remote repository, source/target branches, merge method and selected cleanup targets.

The platform's PR merge updates the remote target; no separate push of the local target is needed. Required CI,
review and branch protection remain conditions of the merge. A failure stops the dependent steps and is reported
to the agent.

### 3.2 No-ff and SHA rules shared with local integration

PR integration MUST use a no-ff merge commit, preserving source commits and every SHA cited by the unit's records.
Squash and rebase merge methods MUST NOT be offered by this route. A policy that forbids merge commits prevents this
route; it does not permit a fallback to squash or rebase.

The approved source SHA stays fixed. A changed source requires a new approval. The target may advance from the
confirmation target during the approving call when it remains a descendant, the merge is clean, effective policy
is unchanged and readiness passes again on the merge result. A target reset or rewrite is refused. Planning MUST
apply these conditions to the remote merge rather than freezing the target at its confirmation SHA or silently
accepting a platform merge that cannot enforce them. The result discloses what was checked on the merge result.

After the merge, cleanup verifies the confirmed PR merge (its state and a merge commit whose second parent is the
approved source) and that the fetched target contains the approved source; exact equality with either SHA is not
required. Later target commits do not by themselves prevent cleanup, and neither does a merge that landed on a target
devkit did not check: that landing is reported as a notice, never as a checked success (decided, `answer-01.yaml`
q-unchecked-landing). Cleanup stops only when the fetched target does not contain the approved source. Updating the local target requires a fast-forward; divergent or dirty local state is
reported without overwriting it. Source ancestry preserves cited SHAs without an archival ref.

### 3.3 Failures are handed back to the agent

The operation reports completed steps, the failing or unconfirmed step, observed Git/PR state and a stable failure
code with a deterministic next action. Failure diagnostics follow `CAP-ADV-agent-advisory-protocol`; default output
contains what changes the agent's next step, with detailed diagnostics available through the normal inspection or
verbose path. Unknown remote outcomes MUST NOT be reported as successful or followed by destructive cleanup.

The agent inspects the result and chooses the next command. This proposal does not add an automatic retry loop, a
background recovery service or a separate recovery workflow. Inspection and re-entry reuse existing operation
mechanisms where practical. Re-entry after a confirmed merge continues only the remaining approved cleanup after
revalidating its scope and merge evidence. An unmerged request resumed outside its approving call needs a new
approval if the target has advanced, matching `PROP-integration-follow-ups`' approval lifetime.

**Non-Goals**: squash/rebase integration or cleanup, tree/patch-equivalence proofs for rewritten commits, archival
refs for otherwise unreachable source SHAs, and automated failure recovery.

### 3.4 Route design (Planning)

Evidence: `envelopes/scout-01.yaml`, `envelopes/challenger-01.yaml`, `envelopes/challenger-02.yaml`, the comparison in
[materials/20261020-pull-request-merge-options.md](materials/20261020-pull-request-merge-options.md) and the PADRs
under `decisions/`. Premise: `PROP-integration-follow-ups` as accepted (no-ff result built outside the checkout,
execution context, effective policy digest, readiness on the result, cleanup-only request, approval tolerating
advances only within its call). The user's decisions on q-checks-wait and q-unchecked-landing are recorded in
`envelopes/answer-01.yaml` and folded below.

- **Route selection**: `integration_prepare` takes `route = "local" | "pull-request"`. `[worktree] pull_request =
  "required"` (base or source policy) refuses `local` with `WORKTREE_PR_POLICY`, whose fix names the pull request
  route; under `auto` the caller chooses. The CLI `devkit worktree finish --merge` stays local and keeps refusing under
  `required`; the pull request route exists only behind native confirmation. No policy value grants authority:
  `pull_request` only restricts the route and `delete_branch` only selects a cleanup target, both shown in the form
  (`ADR-integration-approval-asserted`).
- **Platform** (`PADR-github-pull-request-adapter-in-devkit-worktree`): GitHub only, through `gh` behind an
  injectable port in `devkit.worktree`. Every call passes `-R <owner>/<repo>` resolved from the bound remote by `gh`
  (SSH host aliases and GitHub Enterprise hosts that `gh` resolves are accepted), runs without a prompt within a bound
  and returns exit status, stdout and stderr.
- **Remote target at prepare**: `prepare` does one fetch of the target's remote ref (only the remote-tracking ref is
  updated). The remote target ref is the local target branch's upstream; a target without an upstream, or whose
  upstream has another name, is refused. The fetched remote target SHA is the **confirmation target**; the source
  must contain it (else `WORKTREE_MERGE_NOT_FF` with the follow-ups' SHA-preserving fix), and the target policy
  (`pull_request`, `merge`, `delete_branch`, `[integration] provider`) is read from that commit. A local target ahead
  of its upstream is refused (its commits would never reach the remote through this route). The base checkout must
  be on the target branch and clean, as for every finish (a `--no-worktree` task switches it back with the existing
  `WORKTREE_BASE_ON_BRANCH` fix first).
- **Refusals at `prepare`**, nothing changed, before any form: `gh` missing or unauthenticated; a remote `gh` cannot
  resolve; a fork (cross-repository) PR; an open PR for the branch whose base is not the target, or that is a draft;
  a merge queue on the target; any readable merge-commit prohibition (`[worktree] merge = "ff-only"` in either policy,
  `mergeCommitAllowed = false`, a linear-history rule, allowed merge methods excluding merge via `gh ruleset check`).
  Rules devkit cannot read (classic protection without admin rights) are disclosed as unverified; the platform's
  refusal of the merge lands nothing. The PR route skips the local route's `WORKTREE_BRANCH_UNPUSHED` refusal (the
  push makes the remote branch equal the source); a remote branch that is neither absent, equal to nor an ancestor of
  the source (read with `ls-remote` and fetched) is refused.
- **Approval binding**: the request additionally binds the route, the remote name and resolved repository, the remote
  source and target refs, the confirmation target, the exact PR number or "create", the merge method `no-ff`, and the
  selected cleanup targets with the remote branch's expected SHA (the source). A PR that appears, closes or changes
  base after `prepare` refuses execution (new `prepare`). A created PR gets a devkit-composed title from validated
  names (`Integrate <branch> into <target>`) and a fixed body naming the task ID; no caller text is published. The
  form says "Approve pull request integration of <branch> into <owner>/<repo> <target> with a merge commit?", shows
  the confirmation target, lists push, PR create or use, merge, fetch, local fast-forward and each cleanup target,
  states that `deleteBranchOnMerge = true` deletes the remote branch on the platform regardless of `delete_branch`,
  says that the merge runs in this call when the PR's required checks and reviews already pass and otherwise later
  through `integration_resume` while the target is unchanged, and carries the race disclosure: a target commit
  landing between devkit's last check and the platform merge is merged without devkit's checks, reported as such,
  and does not stop cleanup.
- **Execution**: push an explicit refspec `<source>:refs/heads/<branch>` without `-u` and without force (the bound
  `source_upstream` stays unchanged); create the PR when bound to "create"; then the merge section: fetch the target,
  require it to descend from the confirmation target, build the prospective merge and run guards, the receipt check,
  the policy digests and readiness on it as the local route does, recheck the remote target with `ls-remote` is still
  that build target, and call `gh pr merge <n> --merge --match-head-commit <source> --subject "chore(merge):
  integrate <branch> into <target>" --body "<task ID>"`. Never `--auto`, `--admin` or `--delete-branch`.
- **Required checks and review** (decided, `answer-01.yaml` q-checks-wait option a): the approving call never waits.
  At the merge step, after the build and checks, devkit reads the PR (`headRefOid` must be the source; check, review
  and mergeability state). When the platform reports it mergeable with required checks and reviews satisfied (the
  agent already pushed the branch and opened a ready PR, as `spec-integrate`'s PR path does today, and they passed),
  the same call merges. When checks are pending, a review is missing or mergeability is not yet computed, the call
  returns `INTEGRATION_CHECKS_PENDING` with the push and PR steps `completed` and the merge `not_run`; the last build
  target and its checked result stay in the process-local result. A failed required check, a requested change or a
  conflict is `INTEGRATION_MERGE_REFUSED` (a fix changes the source, so a new `prepare`).
  `INTEGRATION_CHECKS_PENDING` is a successful, incomplete result (exit `0`, step states as above), not an error; it
  lists the PR number and URL and the names of the pending checks and missing reviews, and its `[ACTION]` is to wait
  with `gh pr checks <n> --watch` (bounded by the agent) and then call `integration_resume`, and to report to the user
  when a required check does not start. The lock is not held while waiting.
- **Resume of a pending request**, in this order: take the lock (`timeout=0`, `LOCK_HELD` as in the follow-ups); read
  the PR. `MERGED` with `mergeCommit^2` the source goes to landing verification and cleanup (a person merged it);
  `MERGED` otherwise (squash or rebase by a person) is `INTEGRATION_MERGE_UNCONFIRMED` with nothing deleted; closed,
  draft or a changed base is `INTEGRATION_PR_CONFLICT`; `headRefOid` other than the source is
  `INTEGRATION_REMOTE_BRANCH_DIVERGED`; all with nothing changed. Then fetch the target: merge only while it still
  equals the last build target, reusing that build's checked result (same source and target); otherwise
  `INTEGRATION_TARGET_MOVED`, nothing changed. Then read the check state (pending again is
  `INTEGRATION_CHECKS_PENDING`), recheck the remote target with `ls-remote` and merge.
- **Cost of a moved target** (follows from the decision and the follow-ups prepare scope, which requires the source
  to contain the confirmation target): after `INTEGRATION_TARGET_MOVED` the source no longer contains the target, so
  the next step is `spec-integrate` Step 1 (merge the target into the source), re-verification and a new `prepare`;
  the push restarts the PR's checks. On a target that receives commits more often than its checks take, this route
  may never merge; the form and `CAP-INT-mcp-services` state this, and the agent reports it to the user after a repeated
  `INTEGRATION_TARGET_MOVED`. A process restart drops a pending request; a fresh `prepare` merges in its approving
  call only when the target has not moved since the source last contained it and the PR's checks have passed.
- **Landing verification** (`PADR-pull-request-merge-with-pinned-source-and-verified-landing`; decided,
  `answer-01.yaml` q-unchecked-landing): fetch and read the PR's merge commit `M`. The merge is **confirmed** when the
  PR is `MERGED` and `M^2` is the source. `M^1` equal to the checked build target, `M`'s tree equal to the checked tree
  and `M` contained in the fetched target is a **checked landing**. Every other confirmed merge is an **unchecked
  landing**, with a `landing` reason: `advanced` (`M^1` descends from the build target: a commit landed in the window
  between the last check and the merge, which devkit cannot close), `tree-mismatch` (equal first parent, different
  tree), `rewritten-base` (`M^1` does not descend from the confirmation target), `merge-not-contained` (`M` is not in
  the fetched target) or `not-recorded` (a cleanup-only request after a restart, below). An unchecked landing does not hold cleanup: the result carries the notice
  `INTEGRATION_LANDED_UNCHECKED` (level `WARNING`, under `notices`, exit code unchanged) with the reason, `M`, its first
  parent and the fetched target, and an `[ACTION]` that names a command runnable after cleanup and says not to report
  the integration as checked. The readiness provider declares that landed-target check at confirmation beside its
  result-check disclosure (bound by the request digest; devkit-spec: `devkit rules check` in the fast-forwarded base
  checkout, the CI rules it runs on a result); a failure is fixed in a new unit, since the branch is gone. devkit does
  not re-run guards, readiness or the policy digest on `M`. On this route the cleanup scope is the one bound in the
  approved request, never re-read from the target: neither the approved cleanup nor the PR-route cleanup-only request
  compares the local base's policy after the fast-forward (an amendment of the follow-ups' execution policy check for
  this route only; the cleanup-only request's policy is read from the fetched remote target at its `prepare`), so
  later foreign commits or config changes on the target do not block it. The only stop is the source not being an ancestor of the fetched
  target (the target was rewritten so the source commits are no longer reachable from it):
  `INTEGRATION_SOURCE_NOT_CONTAINED`, cleanup `not_run`, nothing deleted, because removing the branches could lose
  commits. A PR that is `MERGED` with another second parent is not a confirmed merge (`INTEGRATION_MERGE_UNCONFIRMED`,
  nothing deleted).
- **Local target and cleanup order**, after a confirmed merge with the source an ancestor of the fetched target,
  checked or unchecked landing alike: (1) fast-forward the local target
  to the fetched target (`merge --ff-only` in the clean base checkout; dirty or divergent state stops here with a code
  and nothing deleted, and `integration_resume` continues once it is fast-forwardable); (2) worktree removal and
  `git branch -d`, with the local target now containing the source; (3) the remote branch, when selected, deleted with
  `git push --force-with-lease=refs/heads/<branch>:<source> <remote> --delete <branch>` (already gone counts as done;
  an open PR using it as base refuses deletion, the branch stays and the result is partial); (4) package-owned scope
  records through the cleanup extensions, which keep `integration_local_only` (only the executor touches the remote).
- **Failures, unknown outcomes and re-entry**: each step reports `completed`, `failed`, `not_run` or `unknown`. A
  nonzero exit of push, PR creation, merge or remote deletion that is not a recognised refusal is `unknown` and
  resolved only from the remote (`ls-remote`, PR state and `mergeCommit`); while the merge is unknown nothing
  destructive runs. `integration_resume` follows the follow-ups lifetime: before the merge only onto the last build
  target (the pending path above), after a confirmed merge only the remaining cleanup, which rechecks that the fetched
  target still contains the source. After a process restart a fresh PR-route `prepare` fetches the target and yields
  the cleanup-only request when the PR is `MERGED`, `mergeCommit^2` is the source and the fetched target contains the
  source; its first step is the local fast-forward, and since no checked landing survives the restart its result
  carries `INTEGRATION_LANDED_UNCHECKED` with reason `not-recorded`.
- **Lock and time budget**: the Git common-directory lock is held for the merge section (fetch, build and checks,
  PR state read, recheck, merge call, landing verification) and for the local fast-forward and cleanup, not across
  push and PR creation and never while checks are pending. Every network step has a bound; Development measures the total of one call against Codex and Claude Code
  MCP tool-call timeouts, documents that a host-side timeout leaves the server-side execution running (inspected with
  `integration_status`), and lowers bounds where a host would cut the call.
- **Codes** (names proposed; Development keeps them consistent with the follow-ups codes):

  | Code | Step | State | Next action |
  | --- | --- | --- | --- |
  | `INTEGRATION_GH_UNAVAILABLE` | prepare | nothing changed | install or authenticate `gh`, prepare again |
  | `INTEGRATION_REMOTE_UNSUPPORTED` | prepare | nothing changed | use the local route, or a GitHub remote `gh` resolves; no fork PRs |
  | `INTEGRATION_TARGET_UPSTREAM` | prepare | nothing changed | set the target's upstream or push its local commits |
  | `INTEGRATION_MERGE_COMMIT_FORBIDDEN` | prepare | nothing changed | integrate outside devkit; no squash or rebase fallback |
  | `INTEGRATION_PR_CONFLICT` | prepare, execute | nothing changed | resolve the PR (base, draft, closed, new), prepare again |
  | `INTEGRATION_REMOTE_BRANCH_DIVERGED` | prepare, push | nothing changed | merge the remote branch into the source, re-verify |
  | `INTEGRATION_CHECKS_PENDING` (success, incomplete) | merge (approving call, resume) | published, not merged | `gh pr checks <n> --watch`, then `integration_resume`; report to the user when a required check does not start |
  | `INTEGRATION_TARGET_MOVED` (follow-ups) | resume before the merge | published, not merged | `spec-integrate` Step 1 (merge the target into the source), re-verify, `prepare` again; report to the user when it repeats |
  | `INTEGRATION_MERGE_UNCONFIRMED` | landing, resume | PR merged without the source as second parent, nothing deleted | report to the user; the branches stay; clean up outside this route |
  | `INTEGRATION_MERGE_REFUSED` | merge | published, not merged | read the platform reason (failed check, requested change, conflict, protection); fix the source and prepare again |
  | `INTEGRATION_STEP_UNKNOWN` | any network step | unknown | `integration_status`; no destructive retry |
  | `INTEGRATION_LANDED_UNCHECKED` (notice, `WARNING`) | landing | merged, cleanup runs | run the unit's readiness checks on the landed target; do not report the integration as checked |
  | `INTEGRATION_SOURCE_NOT_CONTAINED` | landing, cleanup, resume | merged, nothing deleted | report to the user and keep the branches; `integration_resume` once the fetched target contains the source |
  | `INTEGRATION_LOCAL_TARGET_BLOCKED` | cleanup (1) | merged, cleanup not run | make the base checkout clean and fast-forwardable, `integration_resume` |
  | `INTEGRATION_REMOTE_DELETE_BLOCKED` | cleanup (3) | partial | remote branch kept; inspect dependent PRs or the lease |

- **Tests offline**: a scripted fake of the PR port backed by a local bare repository as the remote, whose merge
  writes a merge commit with a configurable first parent, tree, exit status and timeout, and whose PR check and
  review state is scripted. Acceptance covers a pre-pushed PR with passing checks merged in the approving call,
  `INTEGRATION_CHECKS_PENDING` then a resume that merges onto the unchanged target, a resume refused after the target
  moved, a resume finding the PR merged by a person (merge commit and squash), closed, draft, rebased onto another
  base or with a re-pushed head, `LOCK_HELD` on resume, a restart during the pending window, a failed check refused, a checked landing, each unchecked landing reason continuing cleanup with
  `INTEGRATION_LANDED_UNCHECKED` (including `not-recorded`), a rewritten target that drops the source stopping before cleanup, an unknown merge,
  a rejected push, a diverged remote branch, a lease failure, a blocked local fast-forward, restart re-entry and the
  prepare refusals.
- **Contracts**: no ADR is superseded. Development amends `CAP-INT-mcp-services` (sections 1, 2, 4, 5 and 6: the
  network exclusion becomes route-scoped; the MCP tools that reach the network declare `openWorldHint`),
  `CAP-WT-task-worktrees` (section 5: devkit pushes and opens a PR only on the approved pull request route; the
  `WORKTREE_PR_POLICY` fix), `CAP-DLV-project-policy` (`delete_branch` also selects remote deletion on the PR route),
  the `spec-integrate` skill's PR path and `docs/development/reference/integration.md` and `worktree.md`; the handoff
  promotes the PADRs.
- **Platform facts to verify first**: this Planning ran without network; only local `gh` 2.96.0 help was verified.
  Development verifies against GitHub's documentation (and a test repository where possible) before relying on them:
  merge commit parent order, no base pin in the merge API, head-pin refusal status, required-check and mergeability
  timing after a push, which `gh pr view --json` fields (`mergeStateStatus`, `statusCheckRollup`, `reviewDecision`)
  distinguish pending from failed and from mergeable, what a required check skipped by a path filter reports,
  whether the target ref is updated synchronously with the merge, self-approval prohibition, readability of rulesets and classic protection, `deleteBranchOnMerge`
  and dependent-PR effects of branch deletion, and whether GitHub's merge tree equals `git merge-tree` for clean
  merges. A fact that turns out otherwise and changes this design is a problem for the Host, not a silent adaptation.
- **Coordination**: Development starts after `PROP-integration-follow-ups`' Development lands on `main`; it builds on
  that execution context, build and recovery code rather than the current ff-only code.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-pull-request-cleanup "<title>" --summary "<what it decides>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-pull-request-cleanup`.
- On rejection: `status: rejected` with the user's reason in the commit message.
