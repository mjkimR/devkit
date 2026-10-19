---
id: SPEC-codex-native-workers
title: Codex native workers with command-scoped approvals
summary: "Enable native Codex Planning and Development invocation with emulated worker contracts, explicit worktree paths, scoped approvals and truthful committed or partial results."
status: in-progress
created: 2026-10-19
supersedes: PROP-worktree-host-compatibility
related_capabilities: [CAP-DLV-delivery-workflows]
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-codex-native-workers] Codex native workers with command-scoped approvals

## 1. Problem Statement & Motivation

Native Codex subagents have completed real Planning and Development turns, but both source contracts still mark
Codex unsupported. `ADR-codex-native-worker-execution` accepts native invocation with emulated contract boundaries.
`MAT-codex-native-worker-design` and `MAT-codex-native-worker-evidence` carry the approved design and verified runs.
The Host continues to validate committed results; native invocation supplies no per-worker path enforcement.

## 2. User Stories

- **US-1**: As an agent coordinating delivery, I want Codex workers to use native subagents and scoped approvals so
  that Planning and Development can finish in normal devkit worktrees with reviewable results.
- **US-2**: As the Host, I want accurate permission failures and partial state so that I can block and recover a
  failed run without accepting an invented clean commit.

## 3. Non-Goals

1. **Scope Excluded**: Process workers, `codex exec`, MCP brokers, permission-profile generation, generic probing
   frameworks, host settings/trust edits, worktree relocation and bounded-turn features.
2. **Scope Excluded**: Renderer/schema changes, Claude Code behavior changes, Antigravity validation, fresh-host
   named-role validation and deliberate live approval-denial experiments.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Actual worker projections
- **Given** both real worker source contracts and the existing renderer
- **When** Codex projections are rendered
- **Then** each is valid TOML with status `emulated`, `sandbox_mode: workspace-write`, the boundary warning and full
  procedure; no model, effort or approval-policy override is set; Claude Code and Antigravity metadata stay unchanged.

### [AC-02] Role availability and trust-aware fallback
- **Given** an available projected role, or a missing role with an effective managed/override contract
- **When** the caller chooses native invocation
- **Then** the named role receives only the payload; a generic role may read the absolute effective contract only
  when project-instruction loading is permitted, and the call states emulation; role absence alone does not prove
  missing trust; explicit trust restrictions stop fallback. Missing spawning, nested roles or required approval
  capability selects existing direct/needs_input behavior before starting a worker.

### [AC-03] Explicit paths and operation-specific approval
- **Given** a native worker whose default cwd or sandbox may exclude the assigned worktree or shared Git
- **When** it runs commands or delegates nested read scopes
- **Then** commands set absolute worktree cwd, Git uses `git -C <worktree>`, and nested paths are absolute; each
  necessary out-of-sandbox write, registry, Git or verification operation requests its own exact scoped approval,
  without a persistent prefix or any promise that preflight success grants later access.

### [AC-04] Truthful refusal and emergency preservation
- **Given** unavailable/refused approval or failure to write the emergency record/commit
- **When** the operation cannot proceed
- **Then** that operation stops without a tool/path/process/settings bypass; still-permitted failure preservation
  is attempted; otherwise the return is `failed` with actual last SHA, dirty paths, cause, tried commands, recovery
  and absent/uncommitted records. Only ordinary commit-gate refusal permits emergency `--no-verify`.

### [AC-05] Caller validation and lifecycle
- **Given** a successful or partial worker return
- **When** the Host validates it
- **Then** cumulative ancestry through final HEAD, strict allowed paths, clean worktree, unchanged base and checks
  remain required; failed dirty/uncommitted returns are blocked and subsequent Host recovery owns its records.
  One-shot turns, nested roles, stage commits and exactly one worker envelope per committed run remain unchanged.

## 5. Assumptions & Evidence Limits

The accepted ADR settles design choices; the inspected source renderer already supports `emulated` and
`workspace-write`, so no runtime change is needed. Instruction tests verify branches, not platform enforcement.
Existing live evidence covers generic native invocation in the observed runtime, not named-role loading,
approval denials, failed emergency commits or every host/version. Development is medium effort; the Host runs the
full repository suite once on the returned reviewed head before integration.
