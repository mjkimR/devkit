---
id: PROP-policy-authorized-integration
title: Authorize automatic integration through repository policy
summary: "Make dev-integration auto authorize verified local merge and scoped branch/worktree cleanup without repeated devkit approval, while respecting host permission boundaries."
status: draft
created_at: 2026-10-20
target_area: delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit/src/devkit/integration/
    - packages/devkit-spec/src/devkit_spec/integration.py
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/completion.md
  excludes:
    - packages/devkit-advisory/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-policy-authorized-integration] Authorize automatic integration through repository policy

## 1. Background & Hypothesis

Repeated integration confirmations add little value in a personal workflow where verified changes are normally
merged and later defects receive feedback and corrective changes. The preferred direction is an explicit repository
policy in which `dev-integration = "auto"` authorizes the complete local integration operation, including scoped
worktree and branch cleanup, without another conversational or native confirmation for every task.

`ADR-integration-approval-asserted` currently distinguishes passing a workflow gate from authority to merge or delete.
An `auto` gate therefore does not currently provide this requested behavior. The intended contract extends `auto`
to execution authority for local merge and scoped cleanup; Planning must define the implementation and verify host
feasibility before implementation. This draft does not change current policy or authorize runtime execution.

## Source feedback

- `FB-auto-integration-dispatch`: receive the complete automatic integration and cleanup authority question.
  The feedback is terminal at promotion; progress and decisions belong to this proposal.


`SPEC-standalone-devkit-mcp` owns the reusable MCP runtime, project registration and default interactive approval
route, using `SPEC-local-config-execution-environment`. This proposal retains the separate authority decision for
unattended merge and cleanup, including whether policy-authorized execution is allowed in cloud. Package presence,
default MCP routing and a noninteractive environment do not themselves grant that authority. Reuse the extracted
runtime if the MCP execution route is selected; do not duplicate its packaging or registration work.

## 2. Technical Spike Questions

- **Q1: Authority boundary.** Define how explicit `[workflow.approvals] dev-integration = "auto"` supplies durable
  user authorization for verified local merge, branch deletion and linked-worktree cleanup. Which existing ADR and
  capability statements must change, and what evidence must the executor report as policy authority rather than
  human confirmation? Honor the configured branch-retention policy and bind cleanup to the integrated task.
- **Q2: Host feasibility.** For Codex CLI and Claude Code, distinguish conversational consent, tool-level approval,
  sandbox write access and devkit's own confirmation. Determine which checks policy can satisfy and which host
  approval requirements remain mandatory. Do not claim repository configuration can override platform controls.
- **Q3: Execution route.** Compare a CLI/service route with an MCP route. Can the same readiness and cleanup checks
  run without elicitation? What triggers execution, and how are failed or partial attempts resumed without duplicate
  mutation or pretending they completed?
- **Q4: Scope and changing state.** Define the checked source, destination, policy and cleanup targets; determine
  when changed state requires re-verification or a stop. Preserve tests, review and unresolved-problem checks.
- **Q5: Publication boundary.** Start with local integration and cleanup. Determine whether push/PR publication must
  remain a separate explicit opt-in rather than inheriting local merge authority.

## 3. Proposed Design & Impact

Use `[workflow.approvals] dev-integration = "auto"` as the explicit policy-authorized execution mode: once required
verification succeeds, the configured executor merges and performs the declared local worktree and branch cleanup,
reporting the outcome without requesting conversational approval or native business confirmation. The same setting
authorizes both gate passage and these execution effects; do not introduce a second opt-in for the same scope.
Keep `ask` as the default and preserve its existing approval route. Branch deletion still follows
`[worktree] delete_branch`; `auto` does not authorize unrelated or forced cleanup. Replace the existing authority
rule through an appropriate successor ADR and update the capability and agent instructions together.

Planning must choose and demonstrate a concrete CLI/service or MCP execution route. The current MCP executor
accepts only `ask` and requires native confirmation, so changing configuration or proposal wording alone cannot
provide automatic execution. Evidence must distinguish devkit business confirmation, which `auto` removes, from
host tool approval and filesystem/network permissions, which repository policy cannot override. If a host requires
a separate permission, report that boundary and the remaining effects explicitly; do not claim unattended success.

Expected acceptance evidence:

- Given `dev-integration = "auto"`, passing review/reconciliation/checks and sufficient host permissions, local
  integration merges and removes the task worktree and, when `delete_branch = true`, the merged local branch,
  without conversational or native devkit confirmation. The executor reports policy authority and actual effects.
- With `delete_branch = false`, the same automatic operation retains the branch and reports the retained scope.
- Ask mode still requests approval; missing opt-in never silently authorizes mutation.
- Dirty worktrees, unresolved findings/problems and invalid cleanup targets prevent unsafe execution.
- Host permission refusal stops the affected operation and reports what remains; no alternate tool or path bypass.
- Interrupted execution can be inspected and resumed under a defined authority and state contract.
- Local opt-in alone does not publish or push remotely.

Defects discovered after a verified merge may be recorded as feedback and fixed in follow-up work. That recovery
preference does not remove checks for defects already known before integration or authorize discarding user data.

Scope excluded: changing current repository policy while drafting, skipping required verification, changing host
sandbox/trust settings, supporting VS Code/SDK/desktop hosts, and automatically publishing remotely.

## 4. Lifecycle & Retirement Criteria

Retain as a draft until the execution contract and Codex CLI/Claude Code feasibility have concrete evidence. Planning
compares execution routes for the agreed `auto` scope and demonstrates local merge and cleanup under host permissions.
Acceptance requires the user's decision on that design; promotion alone authorizes neither acceptance nor development.
If host constraints prevent full automation, present the exact remaining permission boundary and the closest supported
flow instead of equating a workflow gate pass with execution authority.
