---
id: SPEC-role-reasoning-effort-presets
title: Per-role reasoning effort presets
summary: Presets a host reasoning effort in each spec role contract's host block (Claude Code effort, Codex model_reasoning_effort) so subagents run at a fixed effort per role without naming models.
status: planned
created: 2026-10-19
related_capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-DIST-agent-projections
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-role-reasoning-effort-presets] Per-role reasoning effort presets

## 1. Problem Statement & Motivation

Handed off from proposal PROP-role-reasoning-effort-presets on 2026-10-19; the decision is
`ADR-role-effort-presets`.

- **Preserved Materials**: `docs/materials/2026-10/20261019-role-reasoning-effort-presets` (`host-effort-semantics.md`:
  the hosts' documented effort semantics).
- **Origin**: split from `SPEC-high-effort-review-loop`. Passing a reasoning effort per call when `activity-effort`
  is `high` works only on Claude Code: Antigravity's host block has no effort key, and on Codex the review roles are
  `emulated`, so there is often no separate call to pass it to.
- **Problem**: every spec role contract carries an abstract `x-model-profile` (`light-medium`, `general-high`,
  `high-reasoning`) that nothing reads, so each projected subagent runs at the host's default reasoning effort
  (`medium` on the Claude 5.5 family). Naming models in contracts would need an update on every model release.
- **Available mechanism**: the host key allowlists of `CAP-DIST-agent-projections` already accept a reasoning effort,
  `effort` for Claude Code and `model_reasoning_effort` for Codex; no contract uses them.
- **Expected outcome**: the review and research roles run at a fixed, model-independent reasoning effort on Claude
  Code and Codex; the two workers keep running at the session's effort; a test keeps profile and preset in step.

## 2. User Stories

- **US-1**: As a Host agent delegating to a review or research role, I want the role's projected agent to carry a
  reasoning effort that matches its model profile, so that a `code-reviewer` or `challenger` reasons at `high` and a
  `scout` or `reconcile-reviewer` at `medium` without any model name to maintain.
- **US-2**: As a user who picked a session effort, I want the `planning-worker` and `development-worker` to run at
  that effort, so that a worker taking over the Host's work does not override my choice.

## 3. Non-Goals

1. **Scope Excluded**: model names in role contracts (`model` keys in any host block).
   - **Rationale**: they would need an update on every model release; model choice stays with the runtime.
2. **Scope Excluded**: a reasoning effort passed per call or derived from `activity-effort`.
   - **Rationale**: it works only on Claude Code; on Codex the agent file wins over a spawn value and an `emulated`
     role has no separate call (`ADR-role-effort-presets`).
3. **Scope Excluded**: an Antigravity effort setting. Its host block has no effort key.
   - **When to Reconsider**: Antigravity documents a per-agent reasoning effort key.
4. **Scope Excluded**: values above `high` (`xhigh`, `max`, `ultra`).
   - **When to Reconsider**: both hosts accept the value on the models in use (`ADR-role-effort-presets` §5).
5. **Scope Excluded**: a preset for `planning-worker` or `development-worker`.
6. **Scope Excluded**: changes to devkit's projection code or host key allowlists; both keys are already allowed.

## 4. Acceptance Criteria & Behavioral Contracts

The mapping every scenario below refers to (`ADR-role-effort-presets`):

| Role | `x-model-profile` | `claude-code` `effort` | `codex` `model_reasoning_effort` | `antigravity` |
| --- | --- | --- | --- | --- |
| `scout` | `light-medium` | `medium` | `medium` | unset |
| `reconcile-reviewer` | `light-medium` | `medium` | `medium` | unset |
| `code-reviewer` | `general-high` | `high` | `high` | unset |
| `challenger` | `high-reasoning` | `high` | `high` | unset |
| `planning-worker` | `general-high` | unset | unset (`unsupported`) | unset |
| `development-worker` | `general-high` | unset | unset (`unsupported`) | unset |

### [AC-01] Reviewer and research roles preset their effort in the Claude Code and Codex blocks
- **Given** the role contracts in `packages/devkit-spec/src/devkit_spec/bundle/subagents/`
- **When** each contract's YAML frontmatter is parsed
- **Then** `hosts.claude-code.effort` and `hosts.codex.model_reasoning_effort` of `scout` and `reconcile-reviewer`
  equal `medium`, those of `code-reviewer` and `challenger` equal `high`, and no host block of any of the four
  carries a `model` key

### [AC-02] Workers and Antigravity carry no preset
- **Given** the same contracts
- **When** their frontmatter is parsed
- **Then** neither `planning-worker` nor `development-worker` has an `effort` key under `claude-code` or a
  `model_reasoning_effort` key under `codex`, and no contract's `antigravity` block has a key containing `effort`

### [AC-03] The challenger's host comment names the preset instead of an invocation-time model choice
- **Given** `challenger.md`
- **When** its frontmatter text is read
- **Then** it does not contain `Choose a high-reasoning model at invocation time`, and the comment above its
  `claude-code` block states that the reasoning effort is preset and the model is left to the runtime

### [AC-04] A drift test pins the mapping for every role contract
- **Given** `packages/devkit-spec/tests/test_role_contracts.py` with one table of role → `x-model-profile` and
  expected preset
- **When** `just test devkit-spec` runs
- **Then** the test passes on the contracts above, and it fails when a contract's profile or preset differs from its
  table entry, when a contract file has no table entry, or when a table entry has no contract file

### [AC-05] The presets reach the projected agent files
- **Given** the changed contracts in this repository
- **When** `devkit sync` runs
- **Then** `.claude/agents/code-reviewer.md` and `.claude/agents/challenger.md` carry `effort: high`,
  `.claude/agents/scout.md` and `.claude/agents/reconcile-reviewer.md` carry `effort: medium`,
  `.codex/agents/<role>.toml` of the same four roles carries `model_reasoning_effort` with the same value,
  `.claude/agents/development-worker.md` and `.claude/agents/planning-worker.md` carry no `effort` key, and
  `devkit sync --check` exits 0 afterwards

### [AC-06] The Living Spec states the presets and their reach
- **Given** `CAP-DLV-delivery-workflows`
- **When** its §2 non-goals and §4.6 are read
- **Then** the model-selection non-goal keeps model choice with the runtime and states that role contracts preset a
  reasoning effort per role, independent of `activity-effort`; §4.6 names `effort` and `model_reasoning_effort` as
  the preset keys, its role table has a "Reasoning effort" column (`medium`, `high`, or "session" for the two
  workers), and one sentence states that a role the main session runs itself (Codex `emulated` or a main-session
  substitute) uses the session's effort

## 5. Assumptions

- The proposal named `decisions/PADR-role-effort-presets.md`; the handoff promoted it to `ADR-role-effort-presets`,
  which this spec cites instead.
- The proposal's premises hold on the current base (after the package split): the allowlists still include `effort`
  and `model_reasoning_effort` (now in `packages/devkit-dist/src/devkit/distribution/bundles/subagents.py`), every
  reviewer's `codex` block is `emulated` and both workers' `codex` blocks are `unsupported`.
- `CAP-DIST-agent-projections` already lists both keys in its role contract format and needs no change unless the
  reconcile finds otherwise.
- The drift test reads only contract frontmatter; projection rendering of allowlisted keys is already covered by
  devkit's distribution tests and is confirmed here by the `devkit sync` run of AC-05.
