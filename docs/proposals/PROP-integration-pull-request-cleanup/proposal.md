---
id: PROP-integration-pull-request-cleanup
title: Integration through pull requests with squash or rebase cleanup
summary: Adds remote push and pull request merge authority separate from local integration, and verifies squash or rebase merges before the worktree and branch are removed.
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

# [PROP-integration-pull-request-cleanup] Integration through pull requests with squash or rebase cleanup

- **Split from**: `PROP-integration-follow-ups` (its question Q3), split during that proposal's Planning, which kept
  only the base advances. Created without `decomposed_from`: `devkit spec proposal new --decomposed-from` refuses a
  source in Planning (`SPEC_PROPOSAL_IN_PLANNING`).
- **Source feedback**: `FB-pr-remote-and-squash-integration`.
- **Related**: `CAP-INT-mcp-services`, `CAP-WT-task-worktrees`, `ADR-integration-approval-asserted`,
  `ADR-branch-guards-and-close-discard` (supersedes `ADR-worktree-and-pull-request-levels`).

## 1. Background & Hypothesis

`SPEC-hook-driven-integration-cleanup` shipped local, approval-bound integration and deferred remote work (its
Non-Goal 3). The integration service forbids network operations, refuses `[worktree] pull_request = "required"`
(`WORKTREE_PR_POLICY`) and executes only local merges. When a branch is merged through a pull request with squash or
rebase, `devkit worktree finish <branch>` reports `WORKTREE_UNMERGED`, because its merge test is commit ancestry, and
the worktree and branch must be removed by hand.

`PROP-integration-follow-ups` lands local integrations as merge commits (`[worktree] merge = "no-ff"` by default), so
local ancestry checks keep working there; it does not provide any proof for squash or rebase merges.

Hypothesis: remote push and pull request merge can get their own explicit authority, separate from local-only
integration, and a squash or rebase merge can be verified (recorded pull request state, tree or patch equivalence)
before any deletion, without ever removing unmerged work.

## 2. Technical Spike Questions

- **Q1 (Authority)**: how is remote push or pull request merge authority separated from local-only integration in the
  confirmation form and the request scope, and how are remote targets disclosed?
- **Q2 (Verification)**: how is a squash or rebase merge verified before the worktree and branch are removed:
  recorded pull request state, tree equivalence, patch equivalence, or a combination?
- **Q3 (Cited SHAs)**: a squash with branch deletion leaves the commit SHAs a unit's envelopes cite unreachable. Does a
  squash path keep the source under another ref, or is it not offered for spec units?
- **Q4 (Policy)**: how `pull_request = "required"` and `ADR-branch-guards-and-close-discard` constrain the design, and
  whether an ADR is needed.

## 3. Proposed Design & Impact

To be designed in this proposal's Planning. Starting points: the merge-commit and effective-policy decisions of
`PROP-integration-follow-ups` (its PADRs, promoted at its handoff) and the remote operations
`ADR-integration-approval-asserted` excludes today.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-pull-request-cleanup "<title>" --summary "<what it decides>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-pull-request-cleanup`.
- On rejection: `status: rejected` with the user's reason in the commit message.
