---
id: ADR-delivery-approval-and-lifecycle-authority
title: Delivery approval gates, Host CLI lifecycle authority and reusable git-operator execution
summary: "For delivery approvals and lifecycle execution, we keep plan-accept, proposal-handoff and dev-integration as independent ask-or-auto gates, take ask decisions in conversation, run guarded CLI through a reusable git-operator, to stop only where decisions are due, accepting unauthenticated consent."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-delivery-decision-boundaries
  - ADR-host-cli-lifecycle-authority
  - ADR-reusable-lifecycle-resource-manager
  - ADR-approval-gates-intent-direction-integration
  - ADR-integration-approval-asserted
  - ADR-autonomy-between-approval-gates
  - ADR-policy-authorized-local-integration
  - ADR-policy-delegated-decision-boundaries
---

# [ADR-delivery-approval-and-lifecycle-authority] Delivery approval gates, Host CLI lifecycle authority and reusable git-operator execution

Superseded in part by `ADR-post-merge-verification`: the merge-time readiness and report-engine revalidation requirements only. Direction acceptance and retained-base approval authority remain.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: @mjkimR, Repository owner
- **Involved Components/Capabilities**: `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`, `ARCH-06-runtime-view`

---

## 1. Context & Problem Statement

Delivery workflows have three human decision points (the user's intent, the direction among alternatives and
approval to integrate). devkit's workflow engine has approval gates: a stage declares `human_gate: <name>`,
`[workflow.approvals]` sets each gate to `ask`, `auto` or `off` (default `ask`), and `devkit workflow answer` records
the user's decision. A gate is satisfied by an accepted decision record of the current segment, by `--given <gate>`
for one invocation, or by the `auto` policy.

The integration gate is asked after the final change report, so a record of it is written after the change is
committed: in a session it costs one more file and one more commit after the user's OK, and on a PR it records the PR
ready state a second time. In use the integration record of `SPEC-subagent-procedure-in-contract` left the worktree
dirty, so `devkit worktree finish` could not run until a commit holding only that file was made and pushed.

Denying merge and deletion authority to every policy value keeps repeated business confirmations necessary even when
the repository opted into `auto` (`SPEC-policy-authorized-integration`). Human-only acceptance rules create duplicate
consent requests and conflate internal worker sequencing with user decisions; direction acceptance and starting
Development also need to remain independently schedulable. A decision boundary identifies which effects are
authorized; it does not require a human interruption in every execution. Implementation choices inside agreed intent
belong to the agent, but the implication for helper commands and routine failures needs to be explicit; treating every
validation finding or failed command as a new human decision undermines autonomous work and makes users coordinate
execution details.

Proposal acceptance, handoff and integration execution must be completable through devkit's CLI without lifecycle
MCP. The Host can present the exact scope in conversation, and the CLI can revalidate source, report, policy,
readiness and cleanup identity before mutation, but it cannot authenticate a conversational answer. Host filesystem
permission remains a separate control and does not establish business approval.

The Host also handles recurring preparation, handoff, integration execution and recovery while maintaining user
discussion. Existing guarded CLI execution can be delegated without changing where business decisions are made.
`MAT-resource-manager-planning-evidence` found 12/12 safe core decisions from both requested model configurations and
matching live read-only state reports. It did not measure lifecycle mutation reliability, token cost or conversation
availability. The user selected the role name `git-operator` and the existing `lean` preset. Terra medium was not part
of the probe; that choice is not inferred from the Sol results.

---

## 2. Decision Drivers

- Gate decisions are recorded or explicitly asserted, never inferred, and a policy can delegate them explicitly.
  (ADR-delivery-decision-boundaries)
- devkit stays SDD-agnostic: its defaults are not tuned for one methodology. (ADR-delivery-decision-boundaries)
- Stage definitions shared by several workflows stay identical (`devkit workflow validate`).
  (ADR-delivery-decision-boundaries)
- Approving integration must not create work that needs another commit after the change is final.
  (ADR-delivery-decision-boundaries)
- One fact, one record: a PR's ready state and the session's explicit OK already carry the integration decision.
  (ADR-delivery-decision-boundaries)
- One explicit shared setting supplies local gate and execution authority without repeated business confirmation.
  (ADR-delivery-decision-boundaries)
- Preserve readiness, exact cleanup scope, state checks and host permissions. (ADR-delivery-decision-boundaries)
- Reuse the existing executor and recovery contract; avoid a second integration engine or permission setting.
  (ADR-delivery-decision-boundaries)
- Keep publication and cloud mutation outside local authority. (ADR-delivery-decision-boundaries)
- Retain the three main scope decisions while allowing deliberate policy delegation. (ADR-delivery-decision-boundaries)
- Permit an accepted proposal to wait in Backlog, or accept and start it in one user decision.
  (ADR-delivery-decision-boundaries)
- Preserve exact source, report, readiness, host permission and recovery guards under automatic execution.
  (ADR-delivery-decision-boundaries)
- Human attention belongs at defined approval and review points and at problems that need human judgment or
  authority. (ADR-delivery-decision-boundaries)
- Agents need actionable results and actual partial state to choose and execute follow-up work.
  (ADR-delivery-decision-boundaries)
- Required checks, reviews, delegated boundaries and host permissions remain effective.
  (ADR-delivery-decision-boundaries)
- A Host must complete the scoped lifecycle when lifecycle MCP is unavailable. (ADR-host-cli-lifecycle-authority)
- `ask` and `auto` retain separate, explicit authority rules. (ADR-host-cli-lifecycle-authority)
- Execution revalidates source, report, policy, readiness and cleanup scope immediately before mutation.
  (ADR-host-cli-lifecycle-authority)
- Local merge, pull-request policy, required checks and publication limits remain effective.
  (ADR-host-cli-lifecycle-authority)
- Partial results identify completed effects and the failing step without creating a durable recovery service.
  (ADR-host-cli-lifecycle-authority)
- Shared artifact access and proposal report publication retain their existing boundaries.
  (ADR-host-cli-lifecycle-authority)
- Reduce the Host's operational instructions and intermediate output across multiple units.
  (ADR-reusable-lifecycle-resource-manager)
- Preserve exact approval scope, CLI guardrails, writer ownership and partial-result recovery.
  (ADR-reusable-lifecycle-resource-manager)
- Reuse native subagent continuation and existing model/config mechanisms. (ADR-reusable-lifecycle-resource-manager)
- Keep the implementation to agent assets, guidance and proportionate contract checks.
  (ADR-reusable-lifecycle-resource-manager)
- Avoid treating a small instructed replay as proof of lightweight-model execution parity.
  (ADR-reusable-lifecycle-resource-manager)

---

## 3. Considered Options

### Gates and integration consent

- **devkit approval gates instead of human exit checks** (selected in `ADR-approval-gates-intent-direction-integration`):
  policy per gate, recorded decisions, `[WAITING: human gate:<gate>]` from `devkit workflow next`; devkit's default
  `ask` differs from a default `auto` for direction.
- **Keep human exit checks** (rejected in `ADR-approval-gates-intent-direction-integration`): no gate policy, no
  decision records; `--given` would assert approvals.
- **Change devkit's default for direction to `auto`** (rejected in `ADR-approval-gates-intent-direction-integration`):
  a methodology default inside the SDD-agnostic foundation.
- **Record the intent and direction gates, assert the integration gate** (selected in
  `ADR-integration-approval-asserted`): no file and no commit after the final change; earlier gates keep a durable
  record at no extra cost; the authority for integration stays visible in the integration report and the merge. The
  integration OK is not in the unit's history; every `next` after it must repeat the `--given` flag.
- **Record every gate** (rejected in `ADR-integration-approval-asserted`): every approval is in the unit's
  `decisions/`, the form devkit recommends for hosts, but an extra commit for every session integration, and a second
  record of the PR ready state.
- **Ask integration before the final commit** (rejected in `ADR-integration-approval-asserted`): the order breaks
  whenever the user commits first or approves on a PR; the final report's head is not the approved head.

### Autonomy and policy delegation

- **Autonomous execution within approved scope** (selected in `ADR-autonomy-between-approval-gates`): use existing
  decision points, let agents resolve routine findings and failures, and design helper tools to support that work;
  requires clear result reporting and escalation boundaries.
- **Additional confirmations for execution details** (rejected in `ADR-autonomy-between-approval-gates`): adds human
  coordination without necessarily improving the evidence at existing gates.
- **An executing CLI on the shared service** (excluded in `ADR-policy-authorized-local-integration`): requires
  explicit owning-workspace/environment binding and restart recovery; current explicit manual CLI authority remains
  separate.
- **Change only the workflow gate or agent wording** (rejected in `ADR-policy-authorized-local-integration`):
  insufficient because the executor accepted `ask` only.
- **Always ask at every boundary** (rejected in `ADR-policy-delegated-decision-boundaries`): repeats authorization
  even when the owning project delegates it.
- **Remove decision boundaries** (rejected in `ADR-policy-delegated-decision-boundaries`): loses the distinction
  between accepted direction and scheduled Development.
- **Independent boundaries with `ask` or `auto` policy** (selected in `ADR-policy-delegated-decision-boundaries`).

### Lifecycle execution route

- **Keep native lifecycle confirmation as the only `ask` execution path** (rejected in
  `ADR-host-cli-lifecycle-authority`): keeps the approval binding and process-local recovery model, but requires a
  connected MCP service for acceptance, handoff and integration, so it does not meet the Host CLI requirement.
- **Let the Host obtain conversational approval and execute through CLI** (selected in `answer-01`,
  `ADR-host-cli-lifecycle-authority`): removes the lifecycle MCP requirement and uses host instructions to present the
  exact scope before execution. The CLI revalidates the operation but does not authenticate the conversational
  decision, which makes the Host responsible for carrying the user's answer correctly.
- **Persist a CLI approval credential or recovery journal** (rejected in `ADR-host-cli-lifecycle-authority`): could
  bind a later command to an earlier decision, but introduces durable authorization and recovery state that the
  proposal excludes, and creates a second approval runtime.

### Lifecycle executor

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Keep lifecycle execution in Host (rejected in `ADR-reusable-lifecycle-resource-manager`) | No new delegation boundary | Leaves recurring operational context in user conversation |
| Spawn a fresh agent for each operation (rejected in `ADR-reusable-lifecycle-resource-manager`) | Fresh job context | Repeats startup and operating-reference loading |
| Reuse one manager, compact default (rejected in `ADR-reusable-lifecycle-resource-manager`) | Lightweight family for bounded work | Full mutation/recovery parity and net savings are unmeasured |
| Reuse one manager, standard default (rejected in `ADR-reusable-lifecycle-resource-manager`) | Earlier provisional mid-tier baseline | Does not encode the selected Terra medium configuration |
| Reuse git-operator, lean default (selected in `ADR-reusable-lifecycle-resource-manager`) | Selected name with explicit Sonnet/Terra medium and native Flash fallback | Terra execution and total costs remain unmeasured |

---

## 4. Decision Outcome

### Approval gates and decision boundaries

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
  approval. (ADR-policy-delegated-decision-boundaries)
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
  `ask` remains the default. (ADR-policy-authorized-local-integration)
- **Limits of authority**: no policy value grants new commit or publication authority, and local delegation grants no
  host permission bypass. Auto PR execution is refused, required PR policy still blocks local merge, and cloud remains
  read-only. No host sandbox, trust or tool policy is changed. (ADR-policy-authorized-local-integration;
  ADR-policy-delegated-decision-boundaries)
- **Integration request and resume**: the immutable request binds policy and Git/cleanup identities. The current
  initial-call descendant-target rule is preserved. Prospective auto-to-ask revocation refuses before the merge; external revocation stops remaining work. After process loss, inspect and prepare a new
  request only for provable remaining scope; no approval or journal file restores authority. Cleanup whose evidence is
  lost is reported as incomplete. (ADR-policy-authorized-local-integration)
- **Internal work**: the Host decides sequential or parallel internal tasks, reviews and fixes within the authorized
  scope. Splitting workers creates no extra user approval requirement. Changes to authorized goals, scope or
  constraints require fresh authority. Completion checks and partial-effect recovery remain mandatory under both `ask`
  and `auto`. (ADR-policy-delegated-decision-boundaries)

### Autonomy between decision points

- **Autonomy between decision points**: human intervention is concentrated at the workflow's defined approval and human
  review points. Within agreed intent and existing authority, agents SHOULD choose implementation details, execute
  commands, inspect failures, correct defects, revalidate and retry autonomously. A routine negative result alone does
  not require user input. Automated checks and agent reviews remain execution work; they do not by themselves create a
  human review point. (ADR-autonomy-between-approval-gates) → `CAP-DLV-project-policy` rule 10 (SHOULD)
- **Helper commands**: helper commands and validation procedures MUST NOT introduce a human approval or acknowledgment
  solely to process routine findings. (ADR-autonomy-between-approval-gates)
  → `CAP-DLV-project-policy` rule 10 (MUST NOT)
- Helper commands SHOULD report completed work, failures or unknown outcomes, stable codes and deterministic next
  actions so the responsible agent can continue. (ADR-autonomy-between-approval-gates)
  → `CAP-DLV-project-policy` rule 10 (SHOULD)
- A required check may still prevent an invalid transition; the agent resolves its cause within scope rather than
  asking the user to manage each step. This principle does not require an automatic retry engine or background
  recovery service. (ADR-autonomy-between-approval-gates)
- **Escalation**: agents escalate when a defined human decision is due, agreed goal/scope/contract must change,
  necessary authority is missing, an existing explicit stop rule applies, or the responsible agent cannot resolve the
  problem within the agreement. In local orchestration, a worker reports to the Host/main agent; that agent resolves
  matters within its authority and brings only necessary decisions to the user. Preserve and report actual partial
  state. (ADR-autonomy-between-approval-gates) → `CAP-DLV-project-policy` rule 10 (MUST)
- **Autonomy limits**: autonomy grants no new commit, merge, publication or deletion authority and does not bypass an
  approval refusal, sandbox restriction, required check/review, bounded review-loop stop or delegated write boundary;
  the gate decisions above and effective `CAP-DLV-project-policy` remain in force. Reuse authorization already given
  for its approved scope; do not ask again for the same authorized action merely because a helper step or recoverable
  failure intervened. An action outside that scope still requires its own authority.
  (ADR-autonomy-between-approval-gates)

### Conversational authority and CLI execution

- **`ask` through conversation**: under `ask`, the Host obtains the user's conversational decision after presenting
  the exact execution scope; the CLI then executes it. The CLI revalidates scope but accepts no approval token or proof
  of user identity. The user selected this option in `answer-01` because the CLI path must work without lifecycle MCP.
  The plan-accept command records acceptance separately. (ADR-host-cli-lifecycle-authority)
- **`auto` through retained policy**: under `auto`, the CLI reads effective policy from the retained base and applies
  the same readiness and identity checks. Caller arguments, local overlays and host command permission do not grant
  policy authority. Pull-request policy and remote publication limits remain unchanged.
  (ADR-host-cli-lifecycle-authority)
- **Results and recovery**: the CLI returns completed effects, the failed step and stable actionable errors. It stores
  no approval session or recovery journal. After an unknown result, Git, worktree and PR state are inspected, and only
  the remaining operation whose scope can be revalidated is invoked. (ADR-host-cli-lifecycle-authority)
- **Replaced integration interface**: this decision replaced, in `ADR-local-and-pull-request-integration`, its
  process-local lifecycle request, native confirmation and resume interface; that ADR's merge construction, readiness,
  policy binding, pull-request route limits, landing validation, integration locking and exact cleanup guards remain
  in force. (ADR-host-cli-lifecycle-authority)

### Reusable git-operator

- **One reusable manager**: use one lazily created, reusable `git-operator` per Host conversation and repository,
  with source `level: lean`. The name and preset are the user's explicit choices. Preserve existing project
  overrides. The preset already exists under `ADR-subagent-levels`; this decision changes no distribution engine
  or level mappings. The original Luna/Sol probe does not validate Terra medium or establish a cost advantage.
  (ADR-reusable-lifecycle-resource-manager)
- The manager owns mechanical preparation/setup, already-authorized handoff/integration execution, exact merged
  resource cleanup and inspection after partial results through existing procedures.
  (ADR-reusable-lifecycle-resource-manager)
- The Host owns user decisions, unit scheduling, result acceptance and semantic conflict decisions.
  (ADR-reusable-lifecycle-resource-manager)
- Source-authoring fixes, semantic reconciliation and resolution of merge conflicts remain with the implementer or
  Host. The manager can report that source preparation is required; it does not invent production edits.
  (ADR-reusable-lifecycle-resource-manager)
- Each job supplies current identities and effect authority. Remembered state never expands that authority.
  (ADR-reusable-lifecycle-resource-manager)
- Preserve original CLI status/exit/effects separately from role status. Use completed only for all verified
  requested effects/checks, needs_input for a Host-dependent remainder, and failed for execution failure. Always
  carry completed_effects and remaining_effects; zero-exit partial cleanup cannot imply completion.
  (ADR-reusable-lifecycle-resource-manager)
- After context loss, rebuild from CLI/Git state and current Host input. Do not persist an approval store or a
  git-operator service. (ADR-reusable-lifecycle-resource-manager)
- Serialize conflicting jobs within the conversation and require quiescent writers before cleanup. Do not claim
  repository-wide mutual exclusion. (ADR-reusable-lifecycle-resource-manager)
- Lean selects Sonnet medium on Claude Code and `gpt-6.1-terra` medium on Codex. Antigravity selects Flash with effort
  omitted because the supported native per-role schema cannot express it. Lean guarantees neither Flash high effort
  nor cross-provider quality equivalence; use no prompt-based effort emulation.
  (ADR-reusable-lifecycle-resource-manager)
- **Replaced worker and level clauses**: this decision replaced, in `ADR-orchestration-workers`, its Host-only
  lifecycle invocation clauses; that ADR's unrelated authority, worker and recovery decisions remain in force. It also
  replaced, in `ADR-subagent-levels`, the clause that only the scout gets a source preset while other roles inherit:
  `git-operator` now has `level: lean`; that ADR's preset mappings and unrelated distribution policy remain in force.
  (ADR-reusable-lifecycle-resource-manager)

---

## 5. Consequences

- **Positive**:
  - Integrating after an OK in a session needs no further commit; `devkit worktree finish` runs on the approved head.
    (ADR-integration-approval-asserted)
  - Auto removes devkit business confirmation for eligible local integration.
    (ADR-policy-authorized-local-integration)
  - Policy introspection exposes all three boundaries.
    (ADR-policy-delegated-decision-boundaries)
  - Agents complete routine execution and recovery without repeated human confirmations; helper-tool design favors
    concise actionable evidence over incidental human gates. (ADR-autonomy-between-approval-gates)
  - Accepted lifecycle operations complete without lifecycle MCP registration. (ADR-host-cli-lifecycle-authority)
  - The Host needs dispatch, approval and exception guidance; operation-specific CLI steps and logs reside in the
    manager's context. Normal integration keeps its existing combined cleanup, without a redundant manager cleanup
    job. (ADR-reusable-lifecycle-resource-manager)
- **Negative / Risks**:
  - Without configuration every gate waits for the user. (ADR-integration-approval-asserted)
  - `--given dev-integration` is an assertion an agent could make without an OK; the rule that an approval is never
    inferred carries that gate alone, and the integration report names the user's OK as the authority.
    (ADR-integration-approval-asserted)
  - Host refusal remains authoritative and cannot be worked around by switching execution routes. No extra settings,
    transport profile or durable recovery journal are added. (ADR-policy-authorized-local-integration)
  - Agents must distinguish safe recovery within authority from a changed scope or unresolved outcome; unknown
    outcomes remain unknown until inspected and cannot justify destructive follow-up work.
    (ADR-autonomy-between-approval-gates)
  - An agent can invoke a CLI command after an incorrect interpretation of conversation; the CLI cannot detect that
    mistake. The Host must show the operation and exact scope before asking. (ADR-host-cli-lifecycle-authority)
  - A process restart loses in-memory execution progress. Recovery depends on observable Git, worktree, proposal and
    PR state. (ADR-host-cli-lifecycle-authority)
  - The role may increase total tokens. Reuse grows its own context and one Luna follow-up in the probe failed without
    a diagnostic before a changed-input retry completed. No reliability or cost ranking follows from that event. Only
    the Codex read-only invocation path was live exercised; other host and mutation coverage stays explicit.
    (ADR-reusable-lifecycle-resource-manager)
  - `MAT-git-operator-development-evidence` records selected Terra medium native read-only continuation and
    separately labels partial-result replay and isolated CLI mutation fixtures. Terra-driven lifecycle mutation and
    other live hosts remain unexercised. Preserve the earlier Luna/Sol outputs as historical evidence; do not transfer
    Sol results to Terra. Require no new model router or automatic escalation to use lean.
    (ADR-reusable-lifecycle-resource-manager)
- **Follow-ups**:
  - Existing required checks and explicit review stops remain; autonomy adds no new gate, exception stage or approval
    mechanism. The detailed principle remains in this ADR; Planning discovers applicable decisions through the
    existing ADR search step without adding per-decision references to the constitution.
    (ADR-autonomy-between-approval-gates)
  - Development must preserve independent `plan-accept`, `proposal-handoff` and `dev-integration` policy boundaries.
    (ADR-host-cli-lifecycle-authority)

---

## 6. Confirmation

- Development verifies actual merge/cleanup on both Codex CLI and Claude Code,
  recording permission prompts separately; ask-mode tests and host evidence establish reusable pieces, not auto
  behavior. (ADR-policy-authorized-local-integration)
- Tests cover mixed policies, declines, stale state, source-only auto and revocation.
  (ADR-policy-delegated-decision-boundaries)
- Development verifies that `ask` requires the Host instruction path and that CLI arguments cannot claim approval;
  `auto` derives authority only from the retained base policy. Integration tests cover stale source/report, changed
  policy, readiness refusal, local and pull-request policy, and post-merge cleanup recovery. Review confirms the
  conflicting native-confirmation clauses of the earlier boundary decision and of
  `ADR-local-and-pull-request-integration` are superseded while the unrelated decision boundaries remain.
  `ADR-mcp-runtime-and-shared-artifacts` remains in force for shared storage and report publication.
  (ADR-host-cli-lifecycle-authority)
- Development adds role-contract and projection checks under `packages/devkit-spec/tests/integration/bundles/spec/`.
  (ADR-reusable-lifecycle-resource-manager)
- Review compares caller and role instructions for approval retention, exact job scope, partial/unknown recovery,
  output bounds and lack of production-authoring authority. (ADR-reusable-lifecycle-resource-manager)
- Development exercises repeated jobs and isolated lifecycle fixtures with source/worktree/ref guards.
  (ADR-reusable-lifecycle-resource-manager)
- Review only: expected conversation availability and total-cost improvement remain unmeasured in Planning.
  (ADR-reusable-lifecycle-resource-manager)
- Otherwise review only.
