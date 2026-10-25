---
id: SPEC-subagent-model-levels
title: Host-neutral subagent model levels and project overrides
summary: Adds opt-in subagent levels that map model families and reasoning effort to Claude Code, Codex and Antigravity, with inheritance by default and project configuration overrides.
status: planned
created: 2026-10-25
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-subagent-model-levels] Host-neutral subagent model levels and project overrides

## 1. Problem Statement & Motivation

Handed off from proposal PROP-subagent-model-levels on 2026-10-25.
- **Preserved Materials**: `docs/materials/2026-10/20261025-subagent-model-levels`

### 1. Background & Hypothesis

`CAP-DIST-agent-projections` permits host-native model and effort fields in common role contracts.
The renderer forwards those fields without interpreting a neutral model selection policy. The spec bundle
assigns effort presets to read-only roles but does not select model families. Its `x-model-profile` values
are uninterpreted metadata under `CAP-DLV-delivery-workflows`.

The desired default is inheritance from the calling session. An explicit subagent level selects a model family
and supported effort for the host. Projects override the mapping in `.devkit/config.toml` without replacing
role prompts or editing generated files.

Hypothesis: a level resolver in devkit-dist can support `claude-code`, `codex` and `antigravity` while preserving
deterministic projection and the existing sync ownership boundary.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Host-neutral subagent model levels and project overrides so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Planning Findings and Decisions

The proposed direction is specified by `ADR-subagent-level-projection`, with implementation details in
`docs/materials/2026-10/20261025-subagent-model-levels/configuration-design.md` and official-source evidence in `docs/materials/2026-10/20261025-subagent-model-levels/host-mappings.md`.

- Model inheritance means omitting devkit overrides; host defaults, environment and invocation settings can still
  affect runtime selection. Antigravity's omitted effort does not establish exact parent-effort inheritance.
- Use four fixed levels, `inherit`, `light`, `standard`, `deep`, independent of delivery `activity-effort`.
- Shared project configuration overrides role selection and host mapping fields. No checkout-local policy.
- Preserve native variants verbatim. Apply global level policy only to common contracts and reject explicit
  role overrides on native variants in selected bundles.
- Remove spec role effort pins and `x-model-profile`. Supersede only the relevant portions of
  `ADR-orchestration-workers`, preserving unrelated orchestration policy.
- Offline validation checks schemas and known native effort constraints, not account availability or arbitrary
  model identifiers. Host runtime remains responsible for actual alias resolution and compatibility.

### 3. Proposed Design & Impact

#### Neutral subagent levels

Proposed level names and semantics:

| Level | Intent | Projection |
| --- | --- | --- |
| `inherit` | Follow native session inheritance; the default | Emit no devkit model or effort override |
| `light` | Fast, lower-cost bounded tasks | Host lightweight family and supported effort |
| `standard` | General implementation and analysis | Host general-purpose family and supported effort |
| `deep` | Difficult reasoning and review | Host selected reasoning family and supported effort |

Omitting the level selects `inherit`. Explicit `inherit` clears lower-precedence devkit model/effort choices.
Do not inspect and freeze the parent's model at sync time. Host-global subagent defaults or forced settings can
change runtime behavior; document those limits instead of promising exact parent values in every environment.
The level is independent of delivery `activity-effort`, which controls procedure and verification depth.

#### Host mappings

Ship a deterministic built-in mapping for every non-inherit level on all three hosts:

| Host | Model field | Effort field |
| --- | --- | --- |
| `claude-code` | `model`, using a supported family alias or identifier | `effort` |
| `codex` | `model`, using a supported identifier or alias | `model_reasoning_effort` |
| `antigravity` | `model`, using a supported tier | Omit unless a native field is documented and supported |

Multiple levels may map to the same tier when a host offers fewer tiers. Built-in mappings explicitly represent
unavailable effort. Do not emulate effort through prompt instructions. An explicit project request for an
unsupported field produces a stable diagnostic instead of being silently discarded.
Proposed built-in defaults:

| Level | Claude Code | Codex | Antigravity |
| --- | --- | --- | --- |
| `inherit` | omit model/effort | omit model/effort | omit model/effort |
| `light` | `haiku` / `low` | `gpt-6-luna` / `low` | `flash` / no effort |
| `standard` | `sonnet` / `medium` | `gpt-6.1-sol` / `medium` | `pro` / no effort |
| `deep` | `opus` / `high` | `gpt-6-astra` / `high` | `pro` / no effort |

These are ascending resource presets, not benchmarked quality equivalences. Claude aliases differ by provider;
Haiku 5.5 requires Claude Code v2.1.293. Native model availability is not checked by sync.
The host evidence material records official references and runtime limitations.

#### Project overrides

Add a distribution-owned `[subagents]` section in `.devkit/config.toml`:

```toml
[subagents]
default_level = "inherit"

[subagents.levels.deep.codex]
effort = "high" # Model retains the built-in gpt-6-astra mapping.

[subagents.roles."spec:scout"]
level = "light"
```

Selection precedence: project role override, explicitly configured project default, role contract level,
then implicit `inherit`. Explicit project default `inherit` resets opted-in bundle levels.
For the selected level, project mapping fields override built-in mapping fields. Define omission and explicit
reset separately: omission retains the built-in field; string `inherit` removes that field. Empty strings and
unknown keys fail validation. No custom levels or per-role raw model overrides. On Antigravity only effort
`inherit` is permitted; any explicit effort value fails validation. The config template comments out every key.
Antigravity model mappings accept only `flash`, `pro`, `inherit`. Claude Code and Codex retain opaque native
model identifiers. Effort values are explicitly enumerated in the configuration material; unknown effort strings
fail preflight. Model-specific restrictions apply only to documented exact Codex identifiers, never to
provider-dependent Claude aliases. See the configuration material for role-key validation and dormant entries.
Use bundle-qualified asset identities for role overrides. Validate effective settings before sync writes files.
Preserve unrelated configuration, role prompts, tools, permissions, isolation and host selection.

#### Existing role transition and documentation

Remove hard-coded effort presets from shipped spec roles so their default becomes inherited model and effort.
Do not silently convert old metadata into mandatory non-inherit levels. Replace or remove `x-model-profile` so
there is one actionable selection mechanism. A contract's explicit `level` plus native model/effort is
`BUNDLE_INVALID`. Without a neutral selection, explicit native fields remain supported. An explicit project
selection replaces those fields; project `inherit` clears them. A role override on a native variant in a selected
bundle is `CONFIG_INVALID`; global defaults skip native variants. Invalid shared settings use `CONFIG_INVALID`
and an `INPUT_ERROR` directive. Local subagent settings use `CONFIG_LOCAL_KEY_FORBIDDEN`.
Update source role contracts, configuration examples and role-contract tests together.

Reconcile `CAP-DIST-agent-projections`, `CAP-DIST-sync-and-transactions`, the affected manifest contract and
`CAP-DLV-delivery-workflows`. Record replacement of the role-effort decision in an ADR during Development.

#### Acceptance checks for Development

- **AC-1 — Default inheritance:** Given an unconfigured project and shipped roles, when sync renders each host's
  role files, then no model or effort override is emitted, including for roles that previously pinned effort.
  Explicit native fields on other authored contracts remain explicit overrides until a project level replaces them.
- **AC-2 — Explicit levels:** Given every non-inherit level, when rendered for each host, then native fields equal
  the documented built-in mapping. Unsupported effort is represented explicitly and no fabricated field is emitted.
- **AC-3 — Mapping overrides:** Given partial project overrides, when sync runs, then overrides and retained
  defaults follow documented merge/reset rules. Other levels and hosts remain unaffected.
- **AC-4 — Selection precedence:** Given contract levels, project defaults and role overrides, when resolved, then
  documented precedence holds. Explicit `inherit` clears lower-precedence choices. Role keys distinguish bundles.
  Omission retains mapping fields while field-level `inherit` removes them; commented templates do not opt in.
- **AC-5 — Invalid settings:** Given unknown levels, malformed mappings, ambiguous declarations or unsupported
  explicit settings, when validated, then stable codes and deterministic actions identify the problem before
  projection or receipt writes. Include invalid Antigravity model tiers, unknown effort tokens, exact Codex
  model/effort restrictions and provider-dependent Claude aliases. Do not probe provider credentials.
- **AC-6 — Sync lifecycle:** Given mapping changes and repeated sync, when rendering completes, then output and
  receipt digests reflect effective settings and repeated sync is idempotent. Returning to inheritance removes
  stale fields while preserving foreign files and unrelated configuration.
- **AC-7 — Asset forms:** Given common contracts, templated contracts and native variants, when level policy is
  applied or rejected, then common and templated contracts resolve identically; variants remain verbatim and
  reject applicable role-specific overrides. Unsupported host blocks still produce no file. Level selection
  preserves role prompts
  and permission settings, and remains independent of `activity-effort`.

Scope excluded: runtime subagent launching, task-text model routing, automatic benchmarking, pricing or model
availability discovery, credentials, additional hosts, conversation-history inheritance controls and changes to
role permissions or delivery verification policy. Host-global model settings remain outside distribution ownership.

### 4. Lifecycle & Retirement Criteria

Planning is in review on `plan-subagent-model-levels`. The proposed direction, mappings and schema require
`plan-accept`; Development requires the separate proposal handoff authorization. No runtime code changes are
part of Planning. Recommended Development effort remains `medium` because the change is reversible and has no
external schema consumers.

Planning completion evidence is the Scout, Challenger and closing reverify envelopes, validated proposal/PADR
boundaries, fresh feedback coverage and one worker record for this run. Keep runtime evidence gaps visible.
Development completes when AC-1 through AC-7 pass, the Living Spec and source bundle agree, and required lint,
type, affected-test and governance checks pass. Follow `CAP-DLV-proposal-incubation` for acceptance and handoff.

