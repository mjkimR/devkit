---
id: US-drive-development-to-integration
title: Drive Development to Integration
summary: An AI coding agent executes an agreed development task through workflow stages, review and reconcile verification loops, and integrates verified changes locally or through a pull request.
area: delivery
actor: AI coding agent
status: active
created_at: 2026-10-21
capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-DLV-project-policy
  - CAP-DLV-workflow-envelopes
  - CAP-INT-mcp-services
  - CAP-WT-task-worktrees
---

# [US-drive-development-to-integration] Drive Development to Integration

## 1. User Story Narrative

- **As a**: AI coding agent or developer working in a repository with `devkit-spec` installed
- **I want to**: advance a development task through its workflow stages, execute review and reconcile verification proportional to the chosen effort, and integrate the verified result
- **So that**: implementation conforms strictly to agreed requirements and Living Spec contracts, and verified changes land cleanly with complete evidence.

---

## 2. Background & Context

Development begins once task intent is agreed. For `session` tasks, the agent implements, tests, self-reviews (or calls `code-reviewer` under `medium`/`high`), and reports results in the conversation without writing envelope or reconcile files. For Unit-bearing tasks (`spec` and `proposal`), the agent operates within `dev-<slug>`, runs `devkit workflow next --unit <dir>` to diagnose stages, executes tests, and records stage completion in structured envelopes. Review subagents (`code-reviewer`, `reconcile-reviewer`) run as nested roles returning messages that the working actor logs into envelopes. Integration is finalized via MCP services (`integration_integrate`) or PR workflows per project policy.

---

## 3. Acceptance Criteria (Given / When / Then)

### Scenario 1: A session task completes directly without durable artifacts
- **Given**: a task classified as `planning-depth = session` and `activity-effort = low`
- **When**: the agent implements changes, runs affected tests, and conducts self-review
- **Then**: no `spec.md`, envelope files, gate record files, or reconcile documents are created, and the agent reports verification results directly in its final response.

### Scenario 2: A unit task executes code and reconcile review under medium effort
- **Given**: an active spec Unit on `dev-<slug>` under `activity-effort = medium`
- **When**: the implementation stage completes and the agent reaches review and reconcile stages
- **Then**: an initial `code-reviewer` subagent is executed and recorded as a `review` envelope, the agent updates `reconcile.md`, and an independent `reconcile-reviewer` validates contract coverage unless self-verification conditions are explicitly met and documented.

### Scenario 3: Bounded high-effort review loop terminates on minor fixes
- **Given**: a spec Unit executing under `activity-effort = high`
- **When**: a review round reports findings that the implementer resolves entirely through minor fixes meeting all four minor-fix criteria
- **Then**: the loop safely terminates without redundant reviewer re-invocation, recording the final resolution in a `reverify` envelope.

### Scenario 4: Local MCP integration authorizes fast-forward merge and scoped cleanup
- **Given**: a completed task branch satisfying all readiness checks under `[workflow.approvals] dev-integration = "auto"`
- **When**: the agent calls the `integration_integrate` MCP tool on the default `local` route
- **Then**: `IntegrationService` fast-forwards the base branch without network operations (no fetch/push), removes the task worktree, deletes the local `dev-<slug>` branch, and executes scoped post-finish cleanup.

### Scenario 5: Pull request policy integrates changes through remote PR
- **Given**: a project configured with `[worktree] pull_request = "required"`
- **When**: the agent attempts `finish --merge` or local integration
- **Then**: the local command is refused with `WORKTREE_PR_POLICY`, and the agent opens a pull request for platform review and CI.

