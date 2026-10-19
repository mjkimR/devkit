---
id: PROP-codex-native-workers
title: Codex native workers with command-scoped approvals
summary: "Enable Codex Planning and Development workers through native subagents with explicit worktree paths, command-scoped approvals and validated committed results."
status: draft
created_at: 2026-10-19
target_area: delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - delivery/
    - packages/devkit-spec/src/devkit_spec/bundle/subagents/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worker-records.md
    - packages/devkit-spec/tests/
    - .devkit/installation.json
  excludes:
    - docs/decisions/
task_kind: feature
supersedes: PROP-worktree-host-compatibility
workflow: sdd-proposal
---

# [PROP-codex-native-workers] Codex native workers with command-scoped approvals

## 1. Background & Hypothesis

The worker contracts label Codex `unsupported` and the superseded ~~`PROP-worktree-host-compatibility`~~ chose a
separate `codex exec` worker. `SPEC-summary-length-guard` instead completed a real Development turn through a
native Codex subagent, with stage commits, nested code and reconcile reviewers, a committed return, Host range
validation and local integration. The worker role was explicitly emulated and its write operations used individual
host-approved permission requests. Evidence: `MAT-codex-native-worker-evidence`,
`FB-native-worker-command-scoped-approvals` and `FB-verification-sync-requires-network`.

Hypothesis: native Codex subagents can execute both worker roles when the host exposes the required tools and
permits their scoped approval requests. A successful approval covers that operation; it establishes neither a
persistent grant nor per-worker path confinement. Claude Code behavior stays as it is; Antigravity stays unverified.

## 2. Technical Spike Questions

- **Q1**: Which support status and invocation instructions distinguish the native spawn mechanism, projected role
  loading and an explicitly emulated contract? What is the role-unavailable fallback without bypassing project trust?
- **Q2**: How does the caller supply absolute worktree/Git paths and scoped approval requests? How does the worker
  preserve its result after refusal, including when an emergency commit cannot run? A probe grants no later authority.
- **Q3**: Can a native Planning worker complete this medium Planning turn with a nested challenger, normal commit
  gate, own records and clean committed return? Reuse the integrated Development evidence.
- **Q4**: Which existing access preconditions remain useful, and which process-launch or bounded-turn requirements
  become unnecessary when the existing one-shot native lifecycle suffices?

## 3. Proposed Design & Impact

- Use native Codex subagents for both workers. Prefer a projected role when available; label a generic subagent
  following the worktree's managed contract as emulated. Use absolute paths and explicit command working directories.
- Describe host-owned, command-scoped approval for sibling-worktree, Git administrative and scope-registry writes.
  Do not promise permanent access after an approved probe. A refused operation preserves the actual result and
  returns a problem; changing tools to evade a refusal is excluded.
- Preserve sibling worktrees created by `devkit worktree start`, committed one-shot results, nested support roles,
  existing gates and Host cumulative range validation.
- Update both worker contracts, the Codex host reference, orchestration instructions, relevant worker records,
  `CAP-DLV-delivery-workflows`, contract/projection tests and synchronized installation receipt.
- **Scope Excluded**: Claude Code behavior changes, Antigravity live validation, process workers, MCP brokers,
  permission-profile generation, host setting changes, worktree relocation and shared-Git confinement. Review-loop
  policy and Planning branch freshness feedback remain independent work.

Retirement is a Host Backlog operation: preserve the old proposal's four open feedback records and source Git
revision, repair incoming references, then retire the process-worker direction through supersede. No live dependency
may be converted to a historical mention merely to permit deletion.

## 4. Lifecycle & Retirement Criteria

- Planning and Development effort: `medium`. Compare unsupported fallback, native scoped approvals and a process
  worker; a nested challenger reviews the native recommendation.
- Planning acceptance requires the validated native Planning return, existing Development evidence and explicit
  approval/refusal limits. The user decides `plan-accept`.
- Development acceptance requires consistent worker contracts/projections, meaningful contract tests for role
  fallback and approval/refusal instructions, unchanged other-host behavior, current capability text, bundle budget
  checks and successful sync.
- Run lint, types, affected tests and governance checks; run the full suite once on the reviewed head and consumer
  smoke before integration. General host/version coverage and persistent grants are not claimed.
- On acceptance: hand off with `devkit spec proposal handoff codex-native-workers` on its Development branch.
  Verified Development and user-authorized integration permit normal proposal cleanup.
- On rejection: mark rejected with the user's reason and preserve evidence/feedback through normal retirement.
