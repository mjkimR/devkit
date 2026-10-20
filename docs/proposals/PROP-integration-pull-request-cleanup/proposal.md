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

After the merge, cleanup verifies recorded PR merge state and that the fetched target contains the approved source
and the recorded merge result; exact equality with either SHA is not required. Later target commits do not by
themselves prevent cleanup. Updating the local target requires a fast-forward; divergent or dirty local state is
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

Evidence: `envelopes/scout-01.yaml`, [materials/20261020-pull-request-merge-options.md](materials/20261020-pull-request-merge-options.md)
and the PADRs under `decisions/`. Premise: `PROP-integration-follow-ups` as accepted (no-ff result built outside the
checkout, effective policy digest, readiness on the result, approval tolerating advances only within its call).

- **Route selection**: `integration_prepare` takes `route = "local" | "pull-request"`. `[worktree] pull_request =
  "required"` (base or source policy) refuses `local` with `WORKTREE_PR_POLICY` and admits only `pull-request`;
  under `auto` the caller chooses. The CLI `devkit worktree finish --merge` stays local and keeps refusing under
  `required`; the pull request route exists only behind native confirmation. No policy value grants the authority:
  `pull_request = "required"` only restricts the route (`ADR-integration-approval-asserted`).
- **Platform** (`PADR-github-pull-request-adapter-in-devkit-worktree`): GitHub only, through `gh` behind an
  injectable port in `devkit.worktree`. Refused at `prepare`, before any form, with stable codes: a non-GitHub remote,
  `gh` missing or unauthenticated, a fork (cross-repository) PR, an existing PR for the branch whose base is not the
  target, a merge queue on the target, and any merge-commit prohibition that can be read: `[worktree] merge =
  "ff-only"` in either policy, `mergeCommitAllowed = false`, a linear-history rule or allowed merge methods excluding
  merge (`gh ruleset check`). Rules devkit cannot read (classic protection without admin) are disclosed in the form as
  unverified; the platform's refusal of the merge lands nothing and is reported as a refusal.
- **Approval binding**: the request additionally binds the route, the remote name and URL, the repository, the PR
  number or "create", the remote source and target refs, the merge method `no-ff`, and the selected cleanup targets
  with the remote branch's expected SHA (the approved source). The form says "Approve pull request integration of
  <branch> into <remote>/<target> with a merge commit?", lists push, PR create/update, merge, fetch and local
  fast-forward and each cleanup target, and states the race disclosure below.
- **Execution** (one call): push the source to the remote branch (non-forced; a remote branch that is not an ancestor
  of the source refuses), create or update the PR, fetch the target, require it to descend from the confirmation
  target, build the prospective merge and check policy and readiness on it as the local route does, recheck the remote
  target is still that build target, then `gh pr merge --merge --match-head-commit <source>` with the devkit-composed
  subject `chore(merge): integrate <branch> into <target>`. Never `--auto`, `--admin` or `--delete-branch`.
- **Landing verification** (`PADR-pull-request-merge-with-pinned-source-and-verified-landing`): fetch, read the PR's
  merge commit `M`; `M^2` must be the source and `M` contained in the fetched target. `M^1` equal to the checked build
  target and `M`'s tree equal to the checked tree is a checked landing; otherwise the outcome is the "landed onto an
  unchecked target" case (question q-unchecked-landing).
- **Required checks and review**: decided by question q-checks-wait (the approving call publishes, so checks start
  after the approval).
- **Local target and cleanup**: the local target fast-forwards to the fetched target only when it is checked out clean
  in the base checkout (`merge --ff-only`) or not checked out anywhere (ref update refused unless fast-forward);
  dirty, divergent or otherwise checked-out state is reported without change. Cleanup runs only after PR state
  `MERGED` and the source and `M` contained in the fetched target: worktree removal and `git branch -d` as today,
  the remote branch deleted with a lease on the source SHA (already gone, such as with `deleteBranchOnMerge`, counts as
  done), then package-owned scope records. Remote deletion follows the effective `delete_branch` and is listed in the
  form when selected.
- **Failures and re-entry**: each step reports `completed`, `failed`, `not_run` or `unknown`. A merge call with an
  unknown outcome is resolved only from the PR state; while unknown nothing destructive runs. `integration_resume`
  continues an approved request under the follow-ups lifetime: only onto the last build target before the merge, and
  only the remaining cleanup after a verified merge. After a process restart, a fresh `prepare` of a merged branch
  yields the follow-ups cleanup-only request, which for this route also verifies PR state and offers the remote
  deletion.
- **Contracts**: no ADR is superseded. Development amends `CAP-INT-mcp-services` (sections 1, 2, 4, 5 and 6:
  network exclusion becomes route-scoped), `CAP-WT-task-worktrees` (section 5: devkit pushes and opens a PR only on
  the approved pull request route; the `WORKTREE_PR_POLICY` fix names that route), `CAP-DLV-project-policy`, the
  `spec-integrate` skill's PR path and `docs/development/reference/integration.md` and `worktree.md`; the handoff
  promotes the PADRs. Cleanup extensions keep `integration_local_only` (only the executor touches the remote).
- **Coordination**: Development starts after `PROP-integration-follow-ups`' Development lands on `main`; it builds on
  that execution context, build and recovery code rather than the current ff-only code.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-pull-request-cleanup "<title>" --summary "<what it decides>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-pull-request-cleanup`.
- On rejection: `status: rejected` with the user's reason in the commit message.
