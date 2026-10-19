---
id: PROP-role-reasoning-effort-presets
title: Per-role reasoning effort presets
summary: "Presets a host reasoning effort in each spec role contract's host block (Claude Code effort, Codex model_reasoning_effort) so subagents run at a fixed effort per role without naming models."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: capabilities/delivery/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-role-reasoning-effort-presets] Per-role reasoning effort presets

- **Origin**: split from `PROP-high-effort-review-loop`. Passing a reasoning effort per call when `activity-effort`
  is `high` works only on Claude Code: Antigravity's host block has no effort key, and on Codex the review roles are
  `emulated`, so there is often no separate call to pass it to.
- **Decided in Backlog**: preset the effort statically per role in the contract's host block, never tied to
  `activity-effort`; name no model; leave Antigravity unset.
- **Related**: `CAP-DLV-delivery-workflows` (§4.6 role contracts, model selection non-goal),
  `CAP-DIST-agent-projections` (host key allowlist), `PROP-high-effort-review-loop`.

## 1. Background & Hypothesis

### 1.1 Problem

- Every spec role contract carries an abstract `x-model-profile` (`light-medium`, `general-high`, `high-reasoning`)
  that nothing reads, so each subagent runs at whatever reasoning effort the host defaults to.
- Naming models in contracts would need an update on every model release, and Codex needs concrete model names.
- The host key allowlists already accept a reasoning effort: `effort` for Claude Code and `model_reasoning_effort`
  for Codex (`devkit/distribution/bundles/subagents.py`). No contract uses them.

### 1.2 Hypothesis

Setting a model-independent reasoning effort per role, derived from its `x-model-profile`, makes the profile take
effect on the hosts that support it, with no maintenance when models change.

## 2. Technical Spike Questions

- **Q1. Values per profile.** Only `low`, `medium` and `high` are used: both hosts accept them on current models,
  higher values depend on the model. Recommended: `scout` and `reconcile-reviewer` (`light-medium`) → `medium`;
  `code-reviewer` (`general-high`) and `challenger` (`high-reasoning`) → `high`; `planning-worker` and
  `development-worker` unset, so they run at the session's effort like the Host whose work they take over.
  Alternative: the workers also `high`, following their `general-high` profile. Open for the user.
- **Q2. Host semantics. Answered** (`materials/host-effort-semantics.md`): Claude Code's agent `effort` and Codex's
  agent `model_reasoning_effort` are documented, optional and accept these values. On Claude Code a per-call
  `effort` overrides the preset and `CLAUDE_CODE_EFFORT_LEVEL` overrides both; on Codex the file value wins over a
  spawn value. Without a preset a subagent runs at the session's or the model's default, which is `medium` on the
  Claude 5.5 family.
- **Q3. Emulated Codex roles.** A role the main session runs itself uses the session's effort. Recommended: one
  sentence in `CAP-DLV-delivery-workflows` §4.6 that a preset applies only when the projected agent is spawned.
  Open for the user.
- **Q4. Profile and preset drift.** Recommended: a test in `packages/devkit-spec/tests/test_role_contracts.py`
  asserting each contract's preset matches its `x-model-profile` under the Q1 mapping. Open for the user.

## 3. Proposed Design & Impact

- Add the preset to the `claude-code` and `codex` host blocks of the `devkit-spec` role contracts Q1 selects
  (`codex` only where its status is not `unsupported`). Antigravity stays unset.
- `CAP-DLV-delivery-workflows`: the model-selection non-goal keeps model choice with the runtime and states that role
  contracts preset a reasoning effort per role; the §4.6 role table gains the preset. `activity-effort` stays
  independent of it.
- No change to devkit's projection code or allowlists.
- **Scope Excluded**: model names in contracts; effort passed per call or tied to `activity-effort`; Antigravity.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions are recorded as PADRs in `decisions/`; research goes in `materials/`.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff role-reasoning-effort-presets`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
