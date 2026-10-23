---
id: PROP-cli-host-lifecycle
title: CLI execution for Host lifecycle operations
summary: "Move Host acceptance, handoff and integration execution to CLI commands and conversational workflow approval. Retain MCP for worker access to shared resources without adding a durable recovery runtime."
status: reviewing
created_at: 2026-10-23
target_area: capabilities/integration/
priority: high
size: L
planning_effort: medium
dev_effort: high
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/integration/
    - packages/devkit/src/devkit_agt/features/worktree/
    - packages/devkit/tests/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/
    - packages/devkit-spec/tests/
    - packages/devkit-mcp/
    - packages/devkit-core/src/devkit_core/base/
    - packages/devkit-core/tests/
    - docs/capabilities/
    - docs/usecases/delivery/
    - docs/development/reference/
    - docs/architecture/
    - docs/decisions/
    - guides/
  excludes:
    - packages/devkit-dist/src/devkit_dist/features/shared/
    - packages/devkit-spec/src/devkit_spec/features/scope/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-cli-host-lifecycle] CLI execution for Host lifecycle operations

## 1. Background & Hypothesis

Host lifecycle execution depends on native MCP forms and process-local approval records. The public integration
CLI only prepares requests. Proposal acceptance and Development preparation also expose composed operations through
MCP. Workflow instructions require those tools even when shared policy delegates the decision.

The operating model assigns worktree creation, acceptance, integration and cleanup to the Host. Workers operate in
their own worktrees and use MCP to reach shared resources outside their sandbox. The Host uses its existing shell
permissions and permission review. Business decisions under `ask` can be requested in the conversation.
The CLI does not need to authenticate the origin of that conversational response.

Hypothesis: one CLI execution path can preserve domain validation and composed lifecycle operations while removing
native approval UI, retained approval sessions and duplicate transport behavior. The Host can recover from partial
failure using CLI inspection and targeted operations. A dedicated durable recovery engine is unnecessary for this
operating model.

## 2. Planning Decisions

Planning settles the CLI surface and the identity and recovery checks below. One authority decision remains for `plan-accept`:

- **D1 — `ask` authority**: The Host presents the exact source, report, target and effects in conversation, obtains the user's decision, then invokes the CLI. The CLI revalidates operation scope but accepts no approval credential and does not authenticate the conversational answer. This changes accepted authority guidance; the user selected this model in `answer-01`; the plan-accept gate is recorded separately. See `PADR-host-cli-lifecycle-authority`.
- **D2 — composed operations**: Extend the existing `devkit spec proposal accept` and `devkit spec proposal handoff` surfaces to expose their composed lifecycle behavior. Expose the existing integration CLI group, currently hidden and limited to preparation, for scoped integration execution. Do not make the Host reproduce internal checks by manually assembling lower-level commands.
- **D3 — identity binding**: Each operation receives or recomputes the proposal slug, exact report URI and source SHA, task and Unit identity, target branch and commit, route, effective base policy, and exact worktree and cleanup identity it needs. Reject stale identities or expanded effects before mutation. `auto` authority is read from the retained base; caller claims and CLI tool permission confer no business authority.
- **D4 — inspection and recovery**: Keep preparation read-only. Use `devkit worktree status` and Git or PR inspection to establish actual state. After a merge followed by cleanup failure, use the existing already-merged `devkit worktree finish` path to perform only remaining guarded cleanup. Do not add `integration_status`, `integration_resume`, a request journal or an approval session. An operation reports completed effects and the failing step; after an unknown outcome the Host inspects actual state before invoking another operation.
- **D5 — MCP boundaries and decisions**: Remove MCP registrations for `spec_plan_accept`, `spec_handoff`, `integration_prepare`, `integration_integrate`, `integration_resume`, `integration_status` and `spec_proposal_report_template` after CLI coverage exists. Retain `spec_proposal_report` for publication and the shared artifact tools `shared_put`, `shared_get`, `shared_list`, `shared_sweep` and `shared_sweep_apply`. Do not add scope-registry MCP operations. Supersede only the native lifecycle execution and process-local approval/recovery clauses in `ADR-delivery-decision-boundaries` and `ADR-local-and-pull-request-integration`; retain their gate, policy, local merge, PR, readiness and cleanup constraints. `ADR-mcp-runtime-and-shared-artifacts` remains in force.

## 3. Proposed Design & Impact

### Host and worker responsibilities

The Host creates Planning and Development worktrees, reviews the exact operation scope, obtains conversational decisions under `ask`, and executes lifecycle commands. Workers use Git CLI in their assigned worktrees and retain access to shared MCP resources. Host filesystem permission, MCP tool permission and workflow business approval remain separate controls.

### CLI execution

Extend `devkit spec proposal accept` to validate the exact committed review report and perform the selected `accept_only` or `accept_and_handoff` operation, including the checked Planning merge. Keep acceptance and handoff policy boundaries independent. Make the selected mode and Development effort explicit inputs.

Extend `devkit spec proposal handoff` to compose Development worktree creation and proposal-to-spec handoff. It reports the worktree path and selected effort so the Host can continue there and record the run input.

Expose `devkit integration prepare` for read-only inspection and add one `devkit integration integrate` operation for local or pull-request execution. It performs the existing readiness, policy, source, target, cleanup and landing checks before mutation. The Host invokes it only after `ask` approval or when `auto` policy authorizes it. It requires no interactive stdin, MCP request ID or approval token.

Use `devkit worktree status`, Git and PR state to inspect execution results. Use existing guarded worktree finish for cleanup after a verified merge. Add another inspection or cleanup command only if Development identifies a concrete state or effect that these operations cannot represent.

### Identity, authority and failure handling

Every mutation revalidates the current source and target, report URI where applicable, effective policy, readiness evidence, worktree identity and exact cleanup targets. A changed source or report, policy change, failed readiness check or mismatched cleanup identity refuses the affected mutation with a stable code. The CLI does not infer `ask` approval from a flag or host permission. Under `auto`, it derives authority from the retained base configuration and preserves the existing refusal of automatic pull-request execution and remote publication authority.

A result identifies completed effects, the failing step and actionable errors using the existing agent output protocol. No durable request store or process-local approval session remains. For an unknown result, the Host inspects the actual proposal, Git, worktree and PR state. It runs only a remaining operation whose inputs and cleanup scope can be revalidated. If the merge completed but cleanup failed, the existing already-merged finish path must skip another merge and remove only its validated worktree and branch.

### Shared services and contracts

Retain `shared_put`, `shared_get`, `shared_list`, `shared_sweep` and `shared_sweep_apply`. Retain `spec_proposal_report` for publication to shared storage. Replace the template MCP call with the existing `devkit spec proposal report <slug> --source-sha <sha> --template` CLI output.

Reconcile `CAP-INT-mcp-services`, `CAP-MCP-runtime-registration`, `CAP-WT-task-worktrees`, `CAP-COLL-work-scope-registry`, affected delivery proposal contracts and delivery use cases. Update source skills, workflow guidance, references, package documentation and installation guides that require lifecycle MCP tools. Record the authorization change in `PADR-host-cli-lifecycle-authority` and supersede the conflicting ADR clauses identified in D5.

### Acceptance criteria

- **AC-1**: With lifecycle MCP tools unavailable, the Host can accept a reviewed proposal, create its Development worktree through composed handoff, and integrate and clean up a verified result through CLI.
- **AC-2**: Under `ask`, Host instructions present the exact operation scope and require a conversational decision before invoking a mutating CLI command. Under `auto`, the CLI uses the same execution path without native forms or interactive stdin.
- **AC-3**: A stale source or report, changed policy, failed readiness check or mismatched cleanup identity refuses the affected mutation with a stable error code. Removing lifecycle MCP does not bypass required PR policy.
- **AC-4**: When an injected failure occurs after the base fast-forward and before cleanup completes, the Host can inspect actual state and rerun only guarded cleanup. Verification proves the merge is not repeated and an unrelated branch or worktree is not removed.
- **AC-5**: Shared artifact access and proposal report publication still work through MCP. Removed lifecycle and report-template tools are absent from registration and workflow instructions.
- **AC-6**: Local and pull-request integration retain applicable readiness checks, effect disclosure and authority limits. CLI execution requires neither an MCP connection nor an MCP process-local request ID.

**Scope Excluded**: Approval authenticity infrastructure, durable recovery orchestration, optional native approval UI, changes to shared artifact semantics, scope-registry transport additions, host permission configuration, new remote-publication authority and unrelated lifecycle features.

## 4. Lifecycle & Retirement Criteria

Keep this proposal in `reviewing` until the `plan-accept` decision. The user selected conversational Host authorization under `ask` in `answer-01`; `devkit spec proposal accept` records the plan-accept gate. The acceptance gate approves the CLI lifecycle and stated exclusions. Development begins only through the normal handoff boundary.

Retire the proposal through handoff when its decisions and requirements are carried into a spec bundle.
Development completes when CLI lifecycle coverage, shared MCP regression checks, relevant package checks and
Living Spec reconciliation pass. Dedicated recovery infrastructure is not an exit condition.
