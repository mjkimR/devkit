---
id: PROP-role-reasoning-effort-presets
title: Per-role reasoning effort presets
summary: "Presets a host reasoning effort in each spec role contract's host block (Claude Code effort, Codex model_reasoning_effort) so subagents run at a fixed effort per role without naming models."
status: accepted                      # draft | reviewing | accepted | rejected
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

- **Origin**: split from `SPEC-high-effort-review-loop`. Passing a reasoning effort per call when `activity-effort`
  is `high` works only on Claude Code: Antigravity's host block has no effort key, and on Codex the review roles are
  `emulated`, so there is often no separate call to pass it to.
- **Decided in Backlog**: preset the effort statically per role in the contract's host block, never tied to
  `activity-effort`; name no model; leave Antigravity unset.
- **Related**: `CAP-DLV-delivery-workflows` (§4.6 role contracts, model selection non-goal),
  `CAP-DIST-agent-projections` (host key allowlist), `SPEC-high-effort-review-loop`.

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

- **Q1. Values per role. Decided** (`answer-01`, `PADR-role-effort-presets`): only `low`, `medium` and `high` are
  used. `scout` and `reconcile-reviewer` → `medium`; `code-reviewer` and `challenger` → `high`; `planning-worker`
  and `development-worker` set no preset and run at the session's effort, like the Host whose work they take over.
- **Q2. Host semantics. Answered** (`materials/host-effort-semantics.md`): Claude Code's agent `effort` and Codex's
  agent `model_reasoning_effort` are documented, optional and accept these values. On Claude Code a per-call
  `effort` overrides the preset and `CLAUDE_CODE_EFFORT_LEVEL` overrides both; on Codex the file value wins over a
  spawn value. Without a preset a subagent runs at the session's or the model's default, which is `medium` on the
  Claude 5.5 family.
- **Q3. Emulated Codex roles. Decided** (`answer-01`): `CAP-DLV-delivery-workflows` §4.6 states in one sentence that
  a role the main session runs itself (`emulated` or substituted) uses the session's effort; the preset applies only
  to a spawned projected agent.
- **Q4. Profile and preset drift. Decided** (`answer-01`): `packages/devkit-spec/tests/test_role_contracts.py`
  asserts the Q1 mapping for every role contract.

## 3. Proposed Design & Impact

- Role contracts (`packages/devkit-spec/src/devkit_spec/bundle/subagents/`): `scout.md` and `reconcile-reviewer.md`
  set `effort: medium` in `claude-code` and `model_reasoning_effort: medium` in `codex`; `code-reviewer.md` and
  `challenger.md` set `high` in both. Every reviewer's `codex` block is `emulated`, so all four get the Codex key.
  `planning-worker.md` and `development-worker.md` stay unset (their `codex` block is `unsupported` anyway).
  Antigravity stays unset. The `challenger` host comment "Choose a high-reasoning model at invocation time" is
  replaced by one that names the preset and leaves the model to the runtime.
- `CAP-DLV-delivery-workflows`: the model-selection non-goal (§2) keeps model choice with the runtime and states that
  role contracts preset a reasoning effort per role, independent of `activity-effort`. §4.6 lists the preset keys
  among the host-block keys, the role table gains a "Reasoning effort" column (`medium`, `high`, or "session" for the
  workers), and one sentence states that a role the main session runs itself (Codex `emulated` or a main-session
  substitute) uses the session's effort: the preset applies only to a spawned projected agent.
- Test (`packages/devkit-spec/tests/test_role_contracts.py`): one table of role → `x-model-profile` and expected
  preset, asserted against every contract's frontmatter (`effort` under `claude-code`, `model_reasoning_effort`
  under a `codex` block that is not `unsupported`, nothing under `antigravity`); a contract missing from the table,
  or a table entry with no contract, fails.
- No change to devkit's projection code or allowlists; both keys are already allowed
  (`devkit/distribution/bundles/subagents.py`).
- **Scope Excluded**: model names in contracts; effort passed per call or tied to `activity-effort`; Antigravity;
  values above `high`.
- **Decisions**: `decisions/PADR-role-effort-presets.md`.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions are recorded as PADRs in `decisions/`; research goes in `materials/`.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff role-reasoning-effort-presets`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
