---
id: ADR-role-effort-presets
title: Static reasoning effort presets for reviewer roles
summary: 'Role contracts preset a model-independent reasoning effort in their Claude Code and Codex host blocks: medium for scout and reconcile-reviewer, high for code-reviewer and challenger, none for the two workers, which run at the session''s effort; a test pins the mapping.'
proposal: SPEC-role-reasoning-effort-presets
status: accepted
created_at: 2026-10-19
---

# [ADR-role-effort-presets] Static reasoning effort presets for reviewer roles

- **Status**: Accepted
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

Every spec role contract carries an abstract `x-model-profile` that nothing reads, so each projected subagent runs at
the host's default reasoning effort (`medium` on the Claude 5.5 family). Naming models would need an update on every
model release. Claude Code (`effort`) and Codex (`model_reasoning_effort`) both accept a per-agent effort in the
host blocks devkit already projects; Antigravity has no such key (`materials/host-effort-semantics.md`).

## 2. Decision Drivers

- No maintenance when models change: name no model, use only `low`, `medium` and `high`, which both hosts accept on
  current models.
- A worker takes over the Host's own work, so it should run at the effort the user chose for the session.
- `activity-effort` decides how thorough a review is; the reasoning effort must stay independent of it, because
  Codex lets the agent file override a spawn value and an `emulated` role has no separate call at all.

## 3. Considered Options

- **Reviewers only** (chosen): `scout` and `reconcile-reviewer` (`light-medium`) `medium`; `code-reviewer`
  (`general-high`) and `challenger` (`high-reasoning`) `high`; `planning-worker` and `development-worker` unset.
- **By profile**: as above, plus both workers `high` after their `general-high` profile. Rejected: it overrides the
  session effort the user picked for the work the worker takes over.
- **Per call, tied to `activity-effort`**: rejected in Backlog; it works only on Claude Code.

## 4. Decision Outcome

- The `claude-code` block sets `effort` and the `codex` block sets `model_reasoning_effort` to the role's value; a
  `codex` block whose status is `unsupported` gets none. Antigravity stays unset. The workers set no preset.
- The preset applies only when the projected agent is spawned. A role the main session runs itself (Codex
  `emulated`, or a main-session substitute) uses the session's effort; `CAP-DLV-delivery-workflows` §4.6 states this
  in one sentence.
- `packages/devkit-spec/tests/test_role_contracts.py` pins the mapping for every role contract: each role's
  `x-model-profile` and its expected preset per host, so a changed profile, a changed preset or a new contract
  without an entry fails the test.

## 5. Consequences

- Reviewers run at a fixed effort on Claude Code and Codex with no model names to maintain; on Claude Code a
  per-call `effort` or `CLAUDE_CODE_EFFORT_LEVEL` still overrides the preset, on Codex the preset wins over a spawn
  value.
- The model-selection non-goal of `CAP-DLV-delivery-workflows` narrows: model choice stays with the runtime, while
  role contracts preset a reasoning effort per role.
- Raising a reviewer above `high` later is a contract edit plus the test table, once both hosts accept the value on
  the models in use.
