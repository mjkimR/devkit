---
id: SPEC-policy-authorized-integration
title: Authorize automatic integration through repository policy
summary: Make dev-integration auto authorize verified local merge and scoped branch/worktree cleanup without repeated devkit approval, while respecting host permission boundaries.
status: in-progress
created: 2026-10-21
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-policy-authorized-integration] Authorize automatic integration through repository policy

## 1. Problem Statement & Motivation

Handed off from proposal PROP-policy-authorized-integration on 2026-10-21.
- **Preserved Materials**: `docs/materials/2026-10/20261021-policy-authorized-integration`

### 1. Background & Hypothesis

Repeated integration confirmations add little value in a personal workflow where verified changes are normally
merged and later defects receive feedback and corrective changes. The preferred direction is an explicit repository
policy in which `dev-integration = "auto"` authorizes the complete local integration operation, including scoped
worktree and branch cleanup, without another conversational or native confirmation for every task.

`ADR-integration-approval-asserted` currently distinguishes passing a workflow gate from authority to merge or delete.
An `auto` gate therefore does not currently provide this requested behavior. The intended contract extends `auto`
to execution authority for local merge and scoped cleanup; Planning must define the implementation and verify host
feasibility before implementation. This draft does not change current policy or authorize runtime execution.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Authorize automatic integration through repository policy so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: new executing CLI, durable execution journal, background watcher, remote publication, cloud mutation, host permission changes, force cleanup, verification bypass, additional host support and changing repository runtime policy.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Local auto
- **Given** shared base auto, local execution and passing checks.
- **When** the Host invokes integration_integrate.
- **Then** merge and exact cleanup execute without confirmation; authority is policy; both merge methods and retained branches work.

### [AC-02] Authority origin
- **Given** ask or missing policy, or only source/caller auto claims.
- **When** integration is requested.
- **Then** native acceptance remains mandatory; prepare and local governance overlays grant no execution authority.

### [AC-03] Readiness and state
- **Given** dirty, locked or replaced worktrees, changed identities, unresolved evidence or inconsistent receipts.
- **When** execution or resume validates the request.
- **Then** unsafe effects refuse; an initial descendant target is accepted only after unchanged policy and readiness checks; retained resume rejects later targets.

### [AC-04] Publication and environment
- **Given** auto PR, required PR local policy, cloud owner or read-only profile.
- **When** execution or resume is requested.
- **Then** execution refuses before remote writes; local execution performs no fetch, push or PR operation.

### [AC-05] Partial results
- **Given** a denial after merge or during cleanup.
- **When** status or same-process resume is invoked.
- **Then** completed and remaining steps are reported without repeated merge or confirmation; policy revocation stops remaining effects; restart restores no authority and lost cleanup evidence stays incomplete.

### [AC-06] Live host and transport
- **Given** disposable repositories and permitted MCP tools and filesystem access.
- **When** implemented auto is exercised on Codex CLI, Claude Code and SDK transport without forms.
- **Then** evidence records host versions, tool permissions, absent devkit elicitation, actual refs and cleanup and no remote effects; unavailable or denied host evidence remains unverified.

### [AC-07] Contract and guidance
- **Given** the implemented policy dispatch.
- **When** Living Spec and source instructions are reconciled.
- **Then** the successor ADR, integration, policy, workflow and worktree contracts and guidance agree; intent and direction remain human, publication separate, local governance overrides forbidden and runtime policy unchanged.

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### Source feedback

- `FB-auto-integration-dispatch`: receive the complete automatic integration and cleanup authority question.
  The feedback is terminal at promotion; progress and decisions belong to this proposal.


`SPEC-standalone-devkit-mcp` owns the reusable MCP runtime, project registration and default interactive approval
route, using `SPEC-local-config-execution-environment`. This proposal retains the separate authority decision for
unattended merge and cleanup, including whether policy-authorized execution is allowed in cloud. Package presence,
default MCP routing and a noninteractive environment do not themselves grant that authority. Reuse the extracted
runtime if the MCP execution route is selected; do not duplicate its packaging or registration work.

### 2. Planning Findings and Selected Route

The proposed implementation is policy dispatch in the existing `integration_integrate` MCP tool and its shared
`IntegrationService`, without a new command, background daemon or second opt-in. `ask` continues to require native
confirmation; `auto` plus the local route derives execution authority from the retained base checkout's shared
configuration. `integration_prepare` remains a preflight and grants no authority. The main-session Host calls the
tool after reporting verified work; gate passage alone does not launch anything, and support workers do not merge.

| Option | Reuse and cost | Decision |
| --- | --- | --- |
| Existing MCP tool with service policy dispatch | Reuses exact request, identity checks, locking, merge builder, scoped cleanup and retained progress; needs no form in auto mode | Selected |
| New executing CLI command using the same service | Also needs an owning-workspace environment guard, process-restart recovery and agent routing; current CLI only prepares | Excluded from this implementation |
| Change only the gate or invoke worktree finish directly | Does not add checked policy authority to the executor or share its retained recovery contract | Rejected |

The current engine already supports local merge, branch/worktree cleanup and partial recovery. Six existing engine
regressions passed in Planning, including no-network merge, branch retention, permission-failure recovery, exact
extension cleanup and uncertain-merge inspection. They use the existing ask authority with a test confirmation
callback; they do not establish implemented auto dispatch or a live unattended host run. Detailed evidence and
host limitations are retained in `docs/materials/2026-10/20261021-policy-authorized-integration/feasibility.md`.

`ADR-policy-authorized-local-integration` proposes a successor to `ADR-integration-approval-asserted`. Existing
intent and direction decisions remain human decisions; only `dev-integration = "auto"` gains the declared local
execution authority. Acceptance of this proposal does not change this repository's current ask setting.

### 3. Proposed Design & Impact

#### Authority and scope

- The executor reads `[workflow.approvals] dev-integration` from the retained base checkout's shared
  `.devkit/config.toml`. Missing means `ask`; local overlays, caller claims, tool permission and `--given` do not
  supply policy authority. A source branch that merely changes ask to auto cannot authorize its own merge.
  Establish and commit the shared auto policy on the base through an independently authorized change before use;
  an uncommitted edit to tracked base configuration fails the existing clean-base check.
- For `auto` and `route=local`, prepare the same immutable request and bind source SHA, target SHA, base policy
  digest, prospective result policy, readiness/provider identities and exact cleanup targets. Record result
  `authority: policy` and its existing request evidence. Do not synthesize a human approval or `ui_action: accept`.
- Execution advances the local base using the configured merge method, removes only the task's clean linked
  worktree and deletes only its merged local branch when `[worktree] delete_branch = true`. The existing scoped
  post-finish extensions remain covered by the request. No force deletion, unrelated cleanup or discard is granted.
- `ask` retains its native form and `authority: mcp-elicitation`. Auto on `route=pull-request` is refused before
  remote operations; local authority never implies push, PR merge or remote branch deletion. Required PR policy
  still blocks local integration. No remote-authority setting is introduced.
- Retain the current local execution environment restriction: cloud profiles stay read-only and a cloud owning
  workspace cannot execute or resume auto integration. This implementation does not change MCP runtime profiles,
  host trust, filesystem/network permissions or `devkit-advisory`.

#### Execution, changed inputs and recovery

- Dispatch inside the service before calling the confirmation callback; auto therefore works without a negotiated
  elicitation form when the host allows the MCP call. Reuse the existing execution engine and locks rather than
  invoking the public finish command as a separate authority path.
- Preserve source immutability, dirty/locked worktree checks, provider readiness, unresolved finding/problem/question
  checks, receipt checks and exact cleanup validation. Policy is rechecked under the execution contract before
  mutation and cleanup; changed policy or identities invalidate the request. An already completed operation is
  reported rather than repeated.
- During the initial call, accept only a descendant of the prepared target and only when a clean build, unchanged
  prospective integration policy and provider recheck on the result succeed. A moved target after the build stops
  before advancing the base. CI rules run on the result; tests and code review ran on the source, as disclosed today.
- Within the same server process, `integration_status` and `integration_resume` retain step progress and the request's
  original authority kind. Resume revalidates policy and remaining scope and never broadens it; a later target needs
  a new integrate call. An auto request requires the policy to remain auto even when its merge has completed; it
  cannot borrow ask confirmation. A request whose prospective result changes auto to ask is refused before mutation.
- After server restart there is no restored authority from a request ID or file. Inspect Git and cleanup state,
  then prepare a fresh policy-authorized request covering only inspectable remaining scope. If source/worktree
  deletion removed evidence needed to derive extension cleanup, report that cleanup as incomplete and require
  deliberate recovery; do not infer completion or introduce a durable journal in this change.
- A host permission denial stops the affected operation, preserves progress and reports what remains. Never switch
  from a refused shell operation to MCP (or another route) to evade that refusal. A previously selected MCP route
  uses only its own host-granted server access and tool permissions.

#### Host feasibility and verification boundary

Removing devkit's confirmation callback is implementable without bypassing a host permission check: the transport
asks for elicitation only when the service invokes the callback. Host MCP-tool authorization and server OS access
remain prerequisites. This proves a viable design, not a guarantee of zero prompts for every installation. Existing
Claude terminal evidence demonstrates ask-mode merge and cleanup only. Live auto operation in both Codex CLI and
Claude Code is still unverified and is required evidence during Development; a denied or unavailable host is reported
with its remaining boundary, never counted as unattended success.

#### Acceptance evidence for Development

- **AC1 — Local auto:** Given shared base auto, local environment and passing completion checks, one integration call
  merges and cleans the task worktree and selected branch without invoking the confirmation callback; the result
  reports policy authority and actual effects. Test both merge methods and `delete_branch = false`.
- **AC2 — Ask and authority origin:** Ask and missing policy still require native acceptance. Source-only auto,
  caller claims, prepared requests and forbidden local governance keys never grant execution authority.
- **AC3 — Readiness and state:** Dirty/locked/replaced worktrees, changed source/policy/provider/cleanup scope,
  unresolved findings/problems/questions, receipt inconsistency and conflicting target movement prevent unsafe
  effects. Test initial-call descendant advance and resume onto a later target separately.
- **AC4 — Publication and environment:** Auto PR requests and required-PR local requests refuse before remote writes;
  local auto performs no fetch/push/PR operation. Cloud owning-workspace and read-only-profile execution/resume refuse,
  including after runtime environment changes.
- **AC5 — Partial results:** Inject denial after merge and during cleanup; status names completed and remaining steps,
  and same-process resume neither repeats merge nor requests business confirmation. Policy revocation blocks remaining
  work. Restart loses retained authority; recovery inspects remaining state without claiming unobserved completion.
- **AC6 — Host smoke:** In disposable repositories, exercise the implemented auto tool on Codex CLI and Claude Code
  with an explicitly allowed MCP tool and server filesystem access. Record host versions, tool permission behavior,
  absence of devkit elicitation, resulting refs/worktree state and no remote effects. Distinguish any host permission
  prompt/refusal from a devkit confirmation. Also test SDK transport with no form capability.
- **AC7 — Contract and guidance:** Promote the successor ADR and update `CAP-INT-mcp-services`,
  `CAP-DLV-project-policy`, `CAP-DLV-delivery-workflows`, `CAP-WT-task-worktrees`, quick reference and the source
  constitution/workflows/integration/completion/worktree/git-policy instructions consistently. Keep plan-intent and
  plan-accept human, publication separate, local governance overrides forbidden and current runtime policy unchanged
  unless separately requested.

Development runs lint/type checks and `just test-affected`, preserving its full fallback. Add service/MCP tests and
spec readiness tests for the cases above, then synchronize source bundle projections through devkit rather than
editing managed assets. No production source changes or new auto behavior are delivered by Planning.

Scope excluded: a new executing CLI, durable execution journal, background watcher, automatic remote publication,
cloud mutation, changing host permissions or trust, force cleanup, bypassing required verification, VS Code/SDK/desktop
host support and changing this repository's current ask policy as part of this proposal.

### 4. Lifecycle & Retirement Criteria

Planning recommends the existing MCP tool with shared-service policy dispatch and `dev_effort: medium`. Acceptance
requires the user's `plan-accept` on this design, including the MCP dependency and the live-host verification gap.
Development must prove AC1–AC7; if either supported host cannot satisfy unattended execution under its granted
permissions, present the exact remaining boundary before claiming the feature complete. Acceptance alone changes no
runtime policy and authorizes neither publication nor automatic integration of this Planning branch.


## Assumptions

The accepted proposal boundaries and interfaces remain present on the handoff base. The existing retained executor, policy digest and owning-workspace guard are reused; no alternative execution route is introduced.
