---
id: SPEC-codex-native-workers
title: Codex native workers with command-scoped approvals
summary: Enable Codex Planning and Development workers through native subagents with explicit worktree paths, command-scoped approvals and validated committed results.
status: planned
created: 2026-10-19
supersedes: PROP-worktree-host-compatibility
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-codex-native-workers] Codex native workers with command-scoped approvals

## 1. Problem Statement & Motivation

Handed off from proposal PROP-codex-native-workers on 2026-10-19.
- **Preserved Materials**: `docs/materials/2026-10/20261019-codex-native-workers`

### 1. Background & Hypothesis

`SPEC-summary-length-guard` completed a real Development turn through a native Codex subagent with nested code
and reconcile reviewers, normal stage commits and a committed return validated by the Host. The role contract was
emulated; sibling-worktree and shared Git mutations used individually approved commands. This proposal's Planning
uses the same native mechanism and a nested challenger. `MAT-codex-native-worker-evidence` records the observed
permissions and limits; `MAT-codex-native-worker-design` compares the alternatives and maps implementation scope.

Native invocation can support both workers without process workers when the host offers nested subagents and
command-scoped approvals. It supplies neither per-worker path confinement nor a persistent permission grant.
`ADR-codex-native-worker-execution` defines the proposed contract. Claude Code behavior stays unchanged and
Antigravity stays `unverified`.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Codex native workers with command-scoped approvals so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1, settled**: Declare both worker `hosts.codex.status` values `emulated`, with `sandbox_mode: workspace-write`.
  Prefer a projected named role; a generic native subagent can read the effective managed/overridden contract when
  the named role is unavailable and project instruction loading is permitted. State contract emulation even with
  native spawning. A trust restriction stops delegation; role absence alone does not diagnose missing trust.
- **Q2, settled**: Every command names the absolute worktree as cwd, every Git command uses `git -C <worktree>`, and
  file paths identify that worktree. Request a narrowly scoped approval for each necessary mutation outside default
  access. Approval belongs to that command only. Preserve actual partial state after refusal; never bypass refusal
  by switching tools, relocating work or changing host settings. Report an uncommitted failed return if the emergency
  record or commit is also denied, so the Host can block and recover rather than accept an invented committed result.
- **Q3, execution evidence**: This medium Planning turn is a real native Codex invocation following the Planning
  contract explicitly as an emulated role. It must finish its nested challenger, own records, normal gated commits and
  clean return; the Host validates the committed range before presenting `plan-accept`. The integrated Development
  evidence remains the reference for Development execution. Neither run verifies named-role loading on a new host.
- **Q4, settled**: Keep actual access checks, nested-role availability, normal devkit sibling worktrees and one-shot
  lifecycle. No persistent-grant preflight, process launcher, generic probe framework or bounded-turn feature is needed.
  The old bounded-turn requirement is retired; no equivalent new requirement remains.

### 3. Proposed Design & Impact

The change is instruction and contract work in `devkit-spec`; the existing distribution renderer already emits
`emulated` Codex TOML and omits `unsupported` roles. No schema, allowlist or host configuration changes are needed.

- Update both worker contracts, `spec-delegate` and its host/payload/worker references, `spec-orchestrate` and worker
  record instructions together. Codex projected workers use `workspace-write`, inherit session reasoning effort and
  keep native settings unchanged for the other hosts. The Codex approval mechanism remains host-owned, outside
  projected role settings.
- Describe named-role availability separately from project trust. First restore a missing/stale projection with
  normal `devkit status`/`devkit sync` where authorized. A session that cannot load that role may use a generic native
  subagent reading the effective contract. This fallback never circumvents an explicit trust or approval restriction.
  If required spawning, nested roles or approvals are unavailable, do not start a worker: the Host runs in `direct`
  when allowed; `required` isolation stops with `needs_input` under existing delegation policy.
- Preserve last-accepted-head validation, allowed path checks, unchanged base checkout, one worker per worktree and
  one worker envelope per turn. A failed emergency record/commit is an explicit unsuccessful return and prevents
  acceptance. Host recovery records belong to a subsequent Host run; they do not impersonate the worker's record.
- Reconcile `CAP-DLV-delivery-workflows`, synchronize bundle assets/receipt and extend role contract tests to prove
  Codex projections, fallback/trust conditions, approval/refusal instructions and unchanged other-host metadata.
  Use deterministic contract tests for denied approval and failed emergency commit; no deliberate unsafe denial is needed.

**Scope Excluded**: source implementation in Planning; Claude Code behavior changes; Antigravity live validation;
process workers or `codex exec`; MCP brokers; permission-profile generation; automatic trust/settings edits;
host-native worktrees, worktree relocation or shared-Git confinement; generic broker/probe frameworks; bounded-turn
features. Review-loop policy and Planning branch freshness are independent tracked feedback.

The prior process-worker proposal has been superseded and retired by Backlog. Its evidence remains in Git and its
four open feedback records were preserved; it is no current prerequisite for this direction.

### 4. Lifecycle & Retirement Criteria

Planning and recommended Development effort remain `medium`: the direction is reversible instruction/contract work,
with a mandatory nested challenger here and independent code/reconcile verification during Development. No unresolved
user question is required within the approved direction. The user alone decides `plan-accept` after Host validation.

Development must demonstrate these scenarios in its spec and verification:

1. Both real worker contracts render valid Codex TOML carrying `emulated` boundary warnings, `workspace-write`, their
   complete procedure and no fixed model, reasoning-effort override or approval-policy setting; Claude Code and
   Antigravity host metadata preserve their existing values. Existing renderer tests remain authoritative.
2. An available projected role receives only the payload. An unavailable role uses an explicitly emulated effective
   contract only when the host permits it; an explicit trust restriction cannot take that fallback. Missing nested
   spawning or necessary approval capability selects existing direct/needs-input behavior before a worker starts.
3. Absolute cwd/Git instructions apply to mutation, verification and nested-role payloads. Each necessary escalated
   command requests its own approval, including shared Git or registry writes, without a broad persistent prefix.
   A successful probe establishes no later access; optional safe diagnostics do not replace actual operation results.
4. Refused or unavailable approval stops that operation. The worker records the cause, tried operations and recovery
   when possible; when a record/normal or emergency commit cannot run, it returns `failed` with the actual last SHA,
   dirty paths, failed record/commit and reason. The Host cannot accept it as a clean committed worker result.
   `--no-verify` remains limited to a gate-refused emergency commit and cannot cure a sandbox/approval denial.
5. The caller still validates ancestry through final HEAD, strict allowed paths, clean worktree, unchanged base and
   required checks. Native Planning plus integrated Development evidence establish tested execution only for the
   observed runtime; named-role loading, denied approvals and broader version/host coverage remain explicit limits.

Development runs lint, types, relevant role/projection tests, bundle budget and governance checks, then syncs and
checks installation state. The full suite runs once on the reviewed head and consumer smoke runs before integration.
No additional live worker experiment or fresh-host named-role validation is required to claim the bounded `emulated`
status. On acceptance, hand off on the Development branch with `devkit spec proposal handoff codex-native-workers`.
Rejection and later cleanup preserve evidence and open feedback through normal retirement.

