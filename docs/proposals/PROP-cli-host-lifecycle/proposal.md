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

## 2. Technical Spike Questions

- **Q1**: Which acceptance, handoff and integration services can become transport-independent operations, and which
  interfaces require `Confirmation` or retained approval records?
- **Q2**: What is the smallest CLI surface for inspection, composed execution and remaining-step cleanup? Prefer
  extending existing commands. Identify a concrete missing operation before introducing another command.
- **Q3**: Which source, report, policy and cleanup identifiers must execution receive or recompute to detect scope
  changes after conversational review without an approval credential or stored approval session?
- **Q4**: Which native form adapters, language assets, registration hooks and approval-specific contracts become
  unused? Preserve dependencies required by shared artifacts and proposal report publication.
- **Q5**: Which ADRs require supersession, and which local/PR policy constraints remain independent of transport?
  Moving to CLI does not itself expand remote publication authority or change `auto` PR policy.

## 3. Proposed Design & Impact

### Host and worker responsibilities

The Host prepares Planning and Development worktrees before assigning workers. It performs acceptance, integration,
branch deletion and worktree removal through CLI commands. Workers commit through Git CLI with the necessary Git
write permissions. This proposal adds no worktree creation/deletion MCP and no scope registry MCP.

Retain `shared_put`, `shared_get`, `shared_list`, `shared_sweep` and `shared_sweep_apply`.
Retain `spec_proposal_report` for publication into shared storage. Shared artifact behavior and external scope
registry access policy remain outside this change.

### CLI execution and MCP removal

Expose the composed behavior of `spec_plan_accept`, `spec_handoff` and `integration_integrate` through application
use cases and CLI adapters. Acceptance mode selection and Development effort become explicit CLI inputs.
Keep one operation for each composed lifecycle action; the Host should not have to reproduce internal checks
and mutations by manually assembling lower-level commands.

Use CLI inspection for `integration_prepare` and a local CLI for `spec_proposal_report_template`.
Remove these lifecycle and template MCP registrations after the CLI covers their behavior. Remove
`integration_status` and `integration_resume` with the process-local integration session model. Provide only the
inspection or targeted execution operations needed to cover concrete gaps in the existing CLI and Git tools.
Do not retain native approval MCP as an optional second lifecycle interface.

Preserve readiness checks, finish guards, policy enforcement, source/report identity checks, integration locking,
worktree identity protections and scoped deletion validation. Keep local and pull-request execution behavior
explicit. Shared-storage operations continue to use their established access boundaries.

### Conversational decisions

Under `ask`, the workflow instructs the Host to present the operation, source/report identity, target branch,
merge or handoff mode, Development effort when relevant, cleanup scope and any remote effects. The Host obtains
that decision before executing those effects and reuses an existing decision for the same scope.

Under `auto`, the Host executes after reporting the result and satisfying applicable policy and readiness checks.
Both modes use the same CLI execution operations. Host permission review remains independent; it is not treated as
proof of business approval. CLI commands do not require interactive stdin or native forms.

Execution validates relevant identities and policy again before mutation. If the source/report changes or requested
effects expand, the Host presents the changed scope for a fresh decision under `ask`. Planning should preserve
existing bounded handling of target advancement unless a concrete CLI constraint requires a change.
No approval token, signed receipt, persisted approval file or service-side proof of user identity is introduced.

### Failure handling

CLI results identify completed effects, the failing step and actionable errors using stable codes and the existing
agent output protocol. The Host inspects actual Git, worktree, proposal and PR state before continuing after an
unknown outcome. It uses existing CLI and Git/PR tools to perform only the remaining work.

Preserve protections against unrelated branch deletion, scope expansion and destructive repetition. Do not build
a durable request store, recovery daemon, cross-command approval session or general automatic resume state machine.
A failure result may contain execution details needed for the Host's next action without making them credentials.

### Contracts and verification

Reconcile CAP-INT-mcp-services, CAP-MCP-runtime-registration, CAP-WT-task-worktrees,
CAP-COLL-work-scope-registry, affected proposal delivery contracts and delivery use cases. Update source skills,
workflow guidance, references, package documentation and installation guides that require native approval tools.
Record the lasting transport and approval policy decision in an ADR; supersede conflicting decisions as needed.

Development acceptance should demonstrate:

- **AC-1**: With lifecycle MCP unavailable, the Host can accept a reviewed proposal, create its Development
  worktree through composed handoff, and integrate and clean up a verified Development result through CLI.
- **AC-2**: `ask` instructions request a conversational decision with the execution scope; `auto` uses the same
  execution path without native forms or interactive stdin.
- **AC-3**: A stale source/report, changed policy, failed readiness check or mismatched cleanup identity refuses
  the affected mutation with a stable error code. Transport removal does not bypass required PR policy.
- **AC-4**: After a representative failure following a successful merge, the Host can inspect actual state and
  complete remaining cleanup with available tools without another merge or deletion outside the requested scope.
- **AC-5**: Shared artifact access and proposal report publication still work through MCP; removed lifecycle tools
  are absent from registration and workflow instructions.
- **AC-6**: Both local and pull-request integration retain applicable validation, effect disclosure and authority
  limits. CLI execution requires neither an MCP connection nor an MCP process-local request ID.

Scope excluded: approval authenticity infrastructure, durable recovery orchestration, optional native approval UI,
changes to shared artifact semantics, scope registry transport additions, host permission configuration, new
remote-publication authority and unrelated lifecycle features.

## 4. Lifecycle & Retirement Criteria

Keep this proposal draft until picked up for Planning. Planning settles command names, input identities, the
minimum missing inspection/cleanup operations, obsolete approval machinery and ADR supersession targets.
Acceptance approves the CLI lifecycle and conversational decision model with the stated exclusions.
Development begins only through the normal handoff boundary.

Retire the proposal through handoff when its decisions and requirements are carried into a spec bundle.
Development completes when CLI lifecycle coverage, shared MCP regression checks, relevant package checks and
Living Spec reconciliation pass. Dedicated recovery infrastructure is not an exit condition.
