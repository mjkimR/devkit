---
id: ADR-delivery-decision-boundaries
title: Delivery decision boundaries, approval gates and agent autonomy
summary: "For delivery approvals, we use devkit gates with plan-accept, proposal-handoff and dev-integration as ask-or-auto boundaries, let auto authorize verified local integration and keep agents autonomous between them, to stop only where decisions are due, accepting assertion-based consent."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-approval-gates-intent-direction-integration
  - ADR-integration-approval-asserted
  - ADR-autonomy-between-approval-gates
  - ADR-policy-authorized-local-integration
  - ADR-policy-delegated-decision-boundaries
---

# [ADR-delivery-decision-boundaries] Delivery decision boundaries, approval gates and agent autonomy

Superseded in part by `ADR-host-cli-lifecycle-authority`: its native MCP lifecycle execution and confirmation clauses.
Independent `plan-accept`, `proposal-handoff` and `dev-integration` gates, policy-owned `auto` authority and Host autonomy between gates remain in force.

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @mjkimR, Repository owner
- **Involved Components/Capabilities**: `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`, `ARCH-06-runtime-view`

---

## 1. Context & Problem Statement

Earlier delivery workflows had three human decision points (the user's intent, the direction among alternatives and
approval to integrate) expressed as human exit checks. devkit's workflow engine has approval gates: a stage declares
`human_gate: <name>`, `[workflow.approvals]` sets each gate to `ask`, `auto` or `off` (default `ask`), and
`devkit workflow answer` records the user's decision. A gate is satisfied by an accepted decision record of the current
segment, by `--given <gate>` for one invocation, or by the `auto` policy.

The integration gate is asked after the final change report, so its record is written after the change is committed:
in a session it costs one more file and one more commit after the user's OK, and on a PR it records the PR ready state
a second time. In use the integration record of `SPEC-subagent-procedure-in-contract` left the worktree dirty, so
`devkit worktree finish` could not run until a commit holding only that file was made and pushed.

Denying merge and deletion authority to every policy value kept repeated business confirmations necessary even when
the repository opted into `auto` (`SPEC-policy-authorized-integration`). Human-only acceptance rules create duplicate
consent requests and conflate internal worker sequencing with user decisions; direction acceptance and starting
Development also need to remain independently schedulable. A decision boundary identifies which effects are
authorized; it does not require a human interruption in every execution.

Native MCP approval surfaces make gate decisions concrete and reviewable. Existing guidance assigned implementation
choices inside agreed intent to the agent, but left the implication for helper commands and routine failures
implicit; treating every validation finding or failed command as a new human decision undermines autonomous work and
makes users coordinate execution details.

---

## 2. Decision Drivers

- Gate decisions are recorded or explicitly asserted, never inferred, and a policy can delegate them explicitly.
- devkit stays SDD-agnostic: its defaults are not tuned for one methodology.
- Stage definitions shared by several workflows stay identical (`devkit workflow validate`).
- Approving integration must not create work that needs another commit after the change is final.
- One fact, one record: a PR's ready state and the session's explicit OK already carry the integration decision.
- One explicit shared setting supplies local gate and execution authority without repeated business confirmation.
- Preserve readiness, exact cleanup scope, state checks and host permissions.
- Reuse the existing executor and recovery contract; avoid a second integration engine or permission setting.
- Keep publication and cloud mutation outside local authority.
- Retain the three main scope decisions while allowing deliberate policy delegation.
- Permit an accepted proposal to wait in Backlog, or accept and start it in one user decision.
- Preserve exact source, report, readiness, host permission and recovery guards under automatic execution.
- Human attention belongs at defined approval and review points and at problems that need human judgment or authority.
- Agents need actionable results and actual partial state to choose and execute follow-up work.
- Required checks, reviews, delegated boundaries and host permissions remain effective.

---

## 3. Considered Options

### Option 1: devkit approval gates instead of human exit checks (Selected by `ADR-approval-gates-intent-direction-integration`)
- **Pros**: policy per gate, recorded decisions, `[WAITING: human gate:<gate>]` from `devkit workflow next`.
- **Cons**: devkit's default `ask` differs from a default `auto` for direction.

### Option 2: Keep human exit checks (Rejected by `ADR-approval-gates-intent-direction-integration`)
- **Cons**: no gate policy, no decision records; `--given` would assert approvals.

### Option 3: Change devkit's default for direction to `auto` (Rejected by `ADR-approval-gates-intent-direction-integration`)
- **Cons**: a methodology default inside the SDD-agnostic foundation.

### Option 4: Record the intent and direction gates, assert the integration gate (Selected by `ADR-integration-approval-asserted`)
- **Pros**: no file and no commit after the final change; earlier gates keep a durable record at no extra cost; the
  authority for integration stays visible in the integration report and the merge.
- **Cons**: the integration OK is not in the unit's history; every `next` after it must repeat the `--given` flag.

### Option 5: Record every gate (Rejected by `ADR-integration-approval-asserted`)
- **Pros**: every approval is in the unit's `decisions/`, the form devkit recommends for hosts.
- **Cons**: an extra commit for every session integration, and a second record of the PR ready state.

### Option 6: Ask integration before the final commit (Rejected by `ADR-integration-approval-asserted`)
- **Cons**: the order breaks whenever the user commits first or approves on a PR; the final report's head is not the
  approved head.

### Option 7: Autonomous execution within approved scope (Selected by `ADR-autonomy-between-approval-gates`)
- **Overview**: use existing decision points, let agents resolve routine findings and failures, and design helper
  tools to support that work.
- **Cons**: requires clear result reporting and escalation boundaries.

### Option 8: Additional confirmations for execution details (Rejected by `ADR-autonomy-between-approval-gates`)
- **Cons**: adds human coordination without necessarily improving the evidence at existing gates.

### Option 9: Existing MCP `integration_integrate` with policy dispatch in `IntegrationService` (Selected by `ADR-policy-authorized-local-integration`)
- **Pros**: reuses request, locks, merge checks, scoped cleanup and process-local progress.
- **Cons**: requires a connected and permitted MCP runtime.

### Option 10: An executing CLI on the shared service (Excluded by `ADR-policy-authorized-local-integration`)
- **Cons**: requires explicit owning-workspace/environment binding and restart recovery; current explicit manual CLI
  authority remains separate.

### Option 11: Change only the workflow gate or agent wording (Rejected by `ADR-policy-authorized-local-integration`)
- **Cons**: insufficient because the executor accepted `ask` only.

### Option 12: Always ask at every boundary (Rejected by `ADR-policy-delegated-decision-boundaries`)
- **Cons**: repeats authorization even when the owning project delegates it.

### Option 13: Remove decision boundaries (Rejected by `ADR-policy-delegated-decision-boundaries`)
- **Cons**: loses the distinction between accepted direction and scheduled Development.

### Option 14: Independent boundaries with `ask` or `auto` policy (Selected by `ADR-policy-delegated-decision-boundaries`)

---

## 4. Decision Outcome

- **Gates**: the delivery workflows' human decision points are devkit approval gates (a stage's `human_gate`)
  governed by `[workflow.approvals]`; human exit checks are not used, and `entry` lists name the gate stage's
  predecessor checks. devkit keeps its default `ask` for every gate. (ADR-integration-approval-asserted, kept by
  ADR-policy-authorized-local-integration)
- **Main boundaries**: the main decision boundaries are `plan-accept`, `proposal-handoff` and `dev-integration`, each
  defaulting to `ask` and allowing `auto`, and each evaluated independently: acceptance may finish while handoff waits.
  (ADR-policy-delegated-decision-boundaries)
- **Task intent**: `plan-intent` remains an authorization record rather than a fourth mandatory interruption: an
  explicit task instruction already supplies intent. It also permits policy satisfaction. No unrequested task is
  implicitly scheduled. (ADR-policy-delegated-decision-boundaries)
- **Replaced restriction**: this replaces the human-only policy restriction described for direct acceptance; the
  validated acceptance writer and carry guards of `ADR-proposal-acceptance` remain in force.
  (ADR-policy-delegated-decision-boundaries)
- **Planning acceptance**: Planning acceptance includes its checked merge; it does not consume Development result
  approval. A native form can approve acceptance and handoff together. (ADR-policy-delegated-decision-boundaries)
- **Integration consent under `ask`**: the user's integration OK is not recorded as a decision file: the executor
  passes `--given dev-integration` to each `devkit workflow next` after it, and a runner binds the gate to the PR ready
  state. The integration report names the user's OK as the authority. A decision record a host UI writes still
  satisfies the gate. An integration objection takes the stage's return path (`devkit workflow return`) instead of a
  recorded decline. (ADR-integration-approval-asserted, kept by ADR-policy-authorized-local-integration)
- **Policy reporting**: under `auto` a gate passes by policy (`source=policy`), reported as delegation, never as a
  human approval; policy records name policy, never user. Under devkit's `off` a stage is skipped. The `exception`
  stage has no gate. (ADR-integration-approval-asserted; ADR-policy-delegated-decision-boundaries)
- **Origin of auto authority**: auto authority must originate in the owning base configuration and remain in the
  prospective source. A branch cannot grant itself authority or silently revoke it during execution. Neither caller
  declarations, local overlays, a source-only policy change nor tool-call permission grant authority.
  (ADR-policy-delegated-decision-boundaries; ADR-policy-authorized-local-integration)
- **Policy-authorized local integration**: shared `[workflow.approvals] dev-integration = "auto"` in the retained base
  checkout authorizes verified local merge and exactly scoped worktree, selected local branch and extension cleanup.
  The existing MCP service prepares and validates the request, grants `authority: policy` without calling the
  confirmation callback, then uses its common execution engine. `ask` remains the default and keeps native
  confirmation. (ADR-policy-authorized-local-integration)
- **Limits of authority**: no policy value grants new commit or publication authority, and local delegation grants no
  host permission bypass. Auto PR execution is refused, required PR policy still blocks local merge, and cloud remains
  read-only. No host sandbox, trust or tool policy is changed. (ADR-policy-authorized-local-integration;
  ADR-policy-delegated-decision-boundaries)
- **Integration request and resume**: the immutable request binds policy and Git/cleanup identities. The current
  initial-call descendant-target rule and the stricter retained resume rule are preserved. Resume revalidates authority
  kind and effective policy, never widens scope or repeats completed effects. Prospective auto-to-ask revocation
  refuses before the merge; external revocation stops remaining work. After process loss, inspect and prepare a new
  request only for provable remaining scope; no approval or journal file restores authority. Cleanup whose evidence is
  lost is reported as incomplete. (ADR-policy-authorized-local-integration)
- **Internal work**: the Host decides sequential or parallel internal tasks, reviews and fixes within the authorized
  scope. Splitting workers creates no extra user approval requirement. Changes to authorized goals, scope or
  constraints require fresh authority. Completion checks and partial-effect recovery remain mandatory under both `ask`
  and `auto`. (ADR-policy-delegated-decision-boundaries)
- **Autonomy between decision points**: human intervention is concentrated at the workflow's defined approval and
  human review points. Within agreed intent and existing authority, agents SHOULD choose implementation details,
  execute commands, inspect failures, correct defects, revalidate and retry autonomously. A routine negative result
  alone does not require user input. Automated checks and agent reviews remain execution work; they do not by
  themselves create a human review point. (ADR-autonomy-between-approval-gates)
- **Helper commands**: helper commands and validation procedures MUST NOT introduce a human approval or
  acknowledgment solely to process routine findings. They SHOULD report completed work, failures or unknown outcomes,
  stable codes and deterministic next actions so the responsible agent can continue. A required check may still
  prevent an invalid transition; the agent resolves its cause within scope rather than asking the user to manage each
  step. This principle does not require an automatic retry engine or background recovery service.
  (ADR-autonomy-between-approval-gates)
- **Escalation**: escalate when a defined human decision is due, agreed goal/scope/contract must change, necessary
  authority is missing, an existing explicit stop rule applies, or the responsible agent cannot resolve the problem
  within the agreement. In local orchestration, a worker reports to the Host/main agent; that agent resolves matters
  within its authority and brings only necessary decisions to the user. Preserve and report actual partial state.
  (ADR-autonomy-between-approval-gates)
- **Autonomy limits**: autonomy grants no new commit, merge, publication or deletion authority and does not bypass an
  approval refusal, sandbox restriction, required check/review, bounded review-loop stop or delegated write boundary;
  the gate decisions above and effective `CAP-DLV-project-policy` remain in force. Reuse authorization already given
  for its approved scope; do not ask again for the same authorized action merely because a helper step or recoverable
  failure intervened. An action outside that scope still requires its own authority.
  (ADR-autonomy-between-approval-gates)

---

## 5. Consequences

- **Positive**:
  - Integrating after an OK in a session needs no further commit; `devkit worktree finish` runs on the approved head.
    (ADR-integration-approval-asserted)
  - Auto removes devkit business confirmation for eligible local integration.
    (ADR-policy-authorized-local-integration)
  - Policy introspection exposes all three boundaries; native services evaluate each independently.
    (ADR-policy-delegated-decision-boundaries)
  - Agents complete routine execution and recovery without repeated human confirmations; helper-tool design favors
    concise actionable evidence over incidental human gates. (ADR-autonomy-between-approval-gates)
- **Negative / Risks**:
  - Without configuration every gate waits for the user. (ADR-integration-approval-asserted)
  - `--given dev-integration` is an assertion an agent could make without an OK; the rule that an approval is never
    inferred carries that gate alone, and the integration report names the user's OK as the authority.
    (ADR-integration-approval-asserted)
  - Actual unattended operation also requires the host to permit the MCP tool and the server to have OS access; host
    refusal remains authoritative and cannot be worked around by switching execution routes. Without the MCP runtime
    there is no automatic CLI substitute. No extra settings, transport profile or durable recovery journal are added.
    (ADR-policy-authorized-local-integration)
  - Agents must distinguish safe recovery within authority from a changed scope or unresolved outcome; unknown
    outcomes remain unknown until inspected and cannot justify destructive follow-up work.
    (ADR-autonomy-between-approval-gates)
- **Follow-ups**:
  - Existing required checks and explicit review stops remain; autonomy adds no new gate, exception stage or approval
    mechanism. The detailed principle remains in this ADR; Planning discovers applicable decisions through the
    existing ADR search step without adding per-decision references to the constitution.
    (ADR-autonomy-between-approval-gates)

---

## 6. Confirmation

- Development verifies the no-form transport path and actual merge/cleanup on both Codex CLI and Claude Code,
  recording permission prompts separately; ask-mode tests and host evidence establish reusable pieces, not auto
  behavior. (ADR-policy-authorized-local-integration)
- Tests cover mixed policies, declines, stale state, source-only auto and revocation.
  (ADR-policy-delegated-decision-boundaries)
- Otherwise review only.
