---
id: PROP-integration-pull-request-cleanup
title: Integration through pull requests with no-ff merge and cleanup
summary: "Defines one approval for push, no-ff PR merge and cleanup, fixing the source SHA while allowing checked target advances. Reports partial completion and actionable failures for agent-led recovery."
status: draft                         # draft | reviewing | accepted | rejected
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

- **Split from**: `SPEC-integration-follow-ups` (its question Q3), split during that proposal's Planning, which kept
  only the base advances. Created without `decomposed_from`: `devkit spec proposal new --decomposed-from` refuses a
  source in Planning (`SPEC_PROPOSAL_IN_PLANNING`).
- **Source feedback**: `FB-pr-remote-and-squash-integration`.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`,
  `ADR-branch-guards-and-close-discard` (supersedes `ADR-worktree-and-pull-request-levels`).

## 1. Background & Hypothesis

`SPEC-hook-driven-integration-cleanup` shipped local, approval-bound integration and deferred remote work (its
Non-Goal 3). The integration service forbids network operations, refuses `[worktree] pull_request = "required"`
(`WORKTREE_PR_POLICY`) and executes only local merges.

`SPEC-integration-follow-ups` defines local integration with merge commits (`[worktree] merge = "no-ff"` by default).
This proposal uses the same no-ff history shape for pull request integration: the target receives a merge commit
and every source SHA cited by the unit's records stays reachable as an ancestor of the target.

Hypothesis: remote push and pull request merge can get their own explicit authority, separate from local-only
integration, and verified PR merge state plus source ancestry in the fetched target can authorize cleanup without
removing unmerged work.

## 2. Planning Scope

The direction is settled: one approval covers the complete PR integration, the merge method is no-ff, target
advances follow the local integration principles of `SPEC-integration-follow-ups`, and the agent handles failures
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
approval if the target has advanced, matching `SPEC-integration-follow-ups`' approval lifetime.

**Non-Goals**: squash/rebase integration or cleanup, tree/patch-equivalence proofs for rewritten commits, archival
refs for otherwise unreachable source SHAs, and automated failure recovery.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-pull-request-cleanup "<title>" --summary "<what it decides>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-pull-request-cleanup`.
- On rejection: `status: rejected` with the user's reason in the commit message.
