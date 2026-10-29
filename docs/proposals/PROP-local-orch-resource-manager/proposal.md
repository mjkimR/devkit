---
id: PROP-local-orch-resource-manager
title: Reusable resource manager subagent for local orchestration
summary: "Delegates lifecycle operations to one reusable subagent per Host conversation and repository to reduce main-agent intervention and context load. Compares lightweight and mid-tier models before selecting the role default."
status: draft
created_at: 2026-10-29
target_area: delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - docs/capabilities/delivery/
    - docs/capabilities/integration/
    - docs/usecases/delivery/
    - docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    - docs/steering/glossary.md
    - docs/decisions/
  excludes:
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit-dist/src/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-local-orch-resource-manager] Reusable resource manager subagent for local orchestration

## 1. Background & Hypothesis

Local orchestration delegates Planning and Development turns, but the Host still prepares worktrees, performs
handoff, executes integration and cleanup, and investigates partial failures. Recurring operating instructions
and intermediate output occupy the conversation that also owns user interaction and decisions.
`CAP-DLV-delivery-workflows` and `ADR-orchestration-workers` define the current worker boundary.

One reusable lifecycle resource manager per Host conversation and repository should reduce operational
intervention and context load. Create it on the first lifecycle request and reuse it for later requests.
Existing host subagent mechanisms provide background execution and continuation; custom asynchronous execution
is not the research objective. The primary benefit is preserving the Host's attention for discussion and
coordination across multiple units. Lower total model cost is a secondary hypothesis.

A lightweight model is a candidate, not a settled default. A mid-tier model may avoid enough retries and Host
intervention to be preferable. Model selection should follow observed end-to-end behavior.

## 2. Technical Spike Questions

- **Q1 — Adoption benefit:** Against Host execution of the same operations, measure Host operational tool calls,
  instruction loading, intermediate output and interventions over a multi-unit session with matched starting
  states. Distinguish main-context savings from total token use and lifecycle completion time.
- **Q2 — Lightweight versus mid-tier:** Compare a lightweight level (`compact` or `minimal`) with `standard`,
  using the same role contract and fixtures. Cover preparation, handoff, authorized integration, scoped cleanup,
  dirty worktrees, moved refs, partial completion and unknown outcomes. Record correctness, inappropriate
  mutations, avoidable escalation, retries, completion time and total usage including Host recovery. Distinguish
  necessary escalation from failure to handle a routine operation. Select the default from these results rather
  than branch cleanup simplicity or happy-path speed alone.
- **Q3 — Context boundary:** Which operating references can move entirely to the manager while leaving the Host
  enough information to authorize effects, schedule units and accept results?
- **Q4 — Reuse:** Specify per-job state refresh, recovery after context loss and continuation guidance for
  Codex/ChatGPT, Claude Code and Antigravity. Validate native invocation paths; a cross-session daemon or new
  scheduler is not a prerequisite.

## 3. Proposed Design & Impact

- Add a lifecycle resource manager role to the spec bundle as the normal helper for recurring operations in
  `local-orchestrated` mode. Reuse one instance within a Host conversation and repository. Load detailed operating
  instructions in its context and return concise results instead of raw logs.
- Delegate worktree creation/attachment and setup, handoff execution, already-authorized integration execution,
  merged branch/worktree cleanup and recovery inspection. Invoke complete existing CLI operations; do not append
  redundant cleanup to integration that already performs it.
- Keep user decisions, unit scheduling, worker result acceptance and semantic conflict decisions with the Host.
  The manager executes only the current job's authorized effects. Return changed scope, unexpected dirty state,
  semantic conflicts and permission/runtime blockers for Host handling.
- Use existing model levels from `CAP-DIST-agent-projections`; choose the role default after Q2 and retain project
  overrides. A new routing subsystem or automatic escalation between models is outside this feature.
- Reuse guarded CLI operations and stable error codes. Composed handoff already prepares the worktree and checks
  state. Scoped integration already revalidates readiness and performs cleanup under `CAP-INT-mcp-services`.
- Each job identifies the operation, repository/worktree, unit/branch, current relevant refs and Host-carried
  authority for its effects. Include the prepared digest where required. Return completed effects, observed refs,
  remaining work and blockers. Agent memory is procedural continuity, not Git truth or approval authority.
- The Host stops writers before handing their worktree to cleanup. Serialize conflicting jobs within the
  conversation and preserve CLI locks and guards. The manager is not a repository-wide mutex. Inspect unknown
  outcomes before attempting only the remaining operation.
- Update Host-only execution wording through the appropriate decision and contract changes. Preserve business
  approval, host permissions, publication limits, readiness checks and exact cleanup scope under
  `ADR-host-cli-lifecycle-authority` and `ARCH-04-1-ecosystem-boundaries`.
- Verify first creation and reuse, self-contained jobs, compact completion/blocked results and the Q2 scenarios.
  Record model/host versions, unavailable measurements and host coverage gaps. Token or latency savings remain
  unverified until measured; assess adoption through Host burden and correctness together.
- **Scope Excluded:** A persistent service, custom async scheduler, durable approval/recovery store, global lock
  service, general Git repair agent, arbitrary branch deletion and lifecycle CLI engine changes. Reconsider engine
  changes only if Planning identifies a concrete missing boundary that prevents safe use of existing operations.

## 4. Lifecycle & Retirement Criteria

- This is a Backlog draft. Registration neither starts Planning nor approves lifecycle execution or a model level.
- Planning records the operation boundary, Host-context reduction and lightweight versus mid-tier comparison in
  this bundle. Acceptance requires a recommended role contract and model default with evidence and visible gaps.
- If neither model preserves correctness while reducing Host burden, present the failed hypothesis and revised
  scope or rejection for the user's decision.
- On acceptance, follow `sdd-proposal` and hand off to one feature spec. On rejection, retain the rejected draft
  until normal hygiene retires it.
