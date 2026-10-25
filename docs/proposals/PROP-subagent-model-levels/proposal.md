---
id: PROP-subagent-model-levels
title: Host-neutral subagent model levels and project overrides
summary: "Adds opt-in subagent levels that map model families and reasoning effort to Claude Code, Codex and Antigravity, with inheritance by default and project configuration overrides."
status: draft
created_at: 2026-10-25
target_area: capabilities/distribution/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/src/devkit_dist/features/project/
    - packages/devkit-dist/tests/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/tests/
    - docs/capabilities/distribution/
    - docs/capabilities/delivery/
    - docs/decisions/
    - docs/glossary.md
  excludes:
    - packages/devkit-core/
    - packages/devkit-mcp/
    - packages/devkit-advisory/
    - packages/devkit-cli/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-subagent-model-levels] Host-neutral subagent model levels and project overrides

## 1. Background & Hypothesis

`CAP-DIST-agent-projections` permits host-native model and effort fields in common role contracts.
The renderer forwards those fields without interpreting a neutral model selection policy. The spec bundle
assigns effort presets to read-only roles but does not select model families. Its `x-model-profile` values
are uninterpreted metadata under `CAP-DLV-delivery-workflows`.

The desired default is inheritance from the calling session. An explicit subagent level selects a model family
and supported effort for the host. Projects override the mapping in `.devkit/config.toml` without replacing
role prompts or editing generated files.

Hypothesis: a level resolver in devkit-dist can support `claude-code`, `codex` and `antigravity` while preserving
deterministic projection and the existing sync ownership boundary.

## 2. Technical Spike Questions

- **Q1 — Host semantics:** Verify omission, global subagent defaults, per-invocation overrides and model-only
  overrides against official documentation and runnable checks where available. Distinguish model/effort
  inheritance from conversation-history inheritance.
- **Q2 — Default mappings:** Select supported family aliases or concrete identifiers and effort values for every
  host and level. Verify alias stability and valid model/effort pairs. Do not invent host-native family aliases.
- **Q3 — Configuration:** Settle the schema, partial overrides, explicit resets, configuration layering, unknown
  keys and conflicts with native model/effort fields. Inspect configuration readers and templates together.
- **Q4 — Existing roles:** Define replacement of `x-model-profile` and effort presets. Identify the effort-preset
  decision in `ADR-orchestration-workers` that needs superseding without replacing unrelated worker decisions.
- **Q5 — Native variants:** Decide whether level policy applies only to common contracts and how attempted native
  variant overrides are reported. Preserve verbatim native variants unless Planning establishes a required extension.

## 3. Proposed Design & Impact

### Neutral subagent levels

Candidate level names and semantics:

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

### Host mappings

Ship a deterministic built-in mapping for every non-inherit level on all three hosts:

| Host | Model field | Effort field |
| --- | --- | --- |
| `claude-code` | `model`, using a supported family alias or identifier | `effort` |
| `codex` | `model`, using a supported identifier or alias | `model_reasoning_effort` |
| `antigravity` | `model`, using a supported tier | Omit unless a native field is documented and supported |

Multiple levels may map to the same tier when a host offers fewer tiers. Built-in mappings explicitly represent
unavailable effort. Do not emulate effort through prompt instructions. An explicit project request for an
unsupported field produces a stable diagnostic instead of being silently discarded.
Planning selects exact default model identifiers and effort values using Q2 evidence.

### Project overrides

Add a distribution-owned section in `.devkit/config.toml`. This schema is illustrative; Planning settles names:

```toml
[subagents]
default_level = "inherit"

[subagents.levels.deep.codex]
model = "<supported-model-identifier>"
effort = "high"

[subagents.roles."spec:scout"]
level = "light"
```

Proposed selection precedence: project role override, explicitly configured project default, role contract level,
then implicit `inherit`. Explicit project default `inherit` resets opted-in bundle levels.
For the selected level, project mapping fields override built-in mapping fields. Define omission and explicit
reset separately so partial overrides cannot accidentally retain unwanted model or effort settings.
Use bundle-qualified asset identities for role overrides. Validate effective settings before sync writes files.
Preserve unrelated configuration, role prompts, tools, permissions, isolation and host selection.

### Existing role transition and documentation

Remove hard-coded effort presets from shipped spec roles so their default becomes inherited model and effort.
Do not silently convert old metadata into mandatory non-inherit levels. Replace or remove `x-model-profile` so
there is one actionable selection mechanism. Settle conflicts between native model/effort fields and levels.
Update source role contracts, configuration examples and role-contract tests together.

Reconcile `CAP-DIST-agent-projections`, `CAP-DIST-sync-and-transactions`, the affected manifest contract and
`CAP-DLV-delivery-workflows`. Record replacement of the role-effort decision in an ADR during Development.

### Acceptance checks for Development

- **AC-1 — Default inheritance:** Given an unconfigured project and shipped roles, when sync renders each host's
  role files, then no model or effort override is emitted, including for roles that previously pinned effort.
- **AC-2 — Explicit levels:** Given every non-inherit level, when rendered for each host, then native fields equal
  the documented built-in mapping. Unsupported effort is represented explicitly and no fabricated field is emitted.
- **AC-3 — Mapping overrides:** Given partial project overrides, when sync runs, then overrides and retained
  defaults follow documented merge/reset rules. Other levels and hosts remain unaffected.
- **AC-4 — Selection precedence:** Given contract levels, project defaults and role overrides, when resolved, then
  documented precedence holds. Explicit `inherit` clears lower-precedence choices. Role keys distinguish bundles.
- **AC-5 — Invalid settings:** Given unknown levels, malformed mappings, ambiguous declarations or unsupported
  explicit settings, when validated, then stable codes and deterministic actions identify the problem before
  projection or receipt writes. Define offline model validation limits without probing provider credentials.
- **AC-6 — Sync lifecycle:** Given mapping changes and repeated sync, when rendering completes, then output and
  receipt digests reflect effective settings and repeated sync is idempotent. Returning to inheritance removes
  stale fields while preserving foreign files and unrelated configuration.
- **AC-7 — Asset forms:** Given common contracts, templated contracts and native variants, when level policy is
  applied or rejected, then each follows its documented support boundary. Level selection preserves role prompts
  and permission settings, and remains independent of `activity-effort`.

Scope excluded: runtime subagent launching, task-text model routing, automatic benchmarking, pricing or model
availability discovery, credentials, additional hosts, conversation-history inheritance controls and changes to
role permissions or delivery verification policy. Host-global model settings remain outside distribution ownership.

## 4. Lifecycle & Retirement Criteria

Keep this proposal draft until selected for Planning. Creation records the direction; it does not accept the
exact schema, default identifiers or a Development handoff.

Planning completes when the three-host capability matrix, default mappings, schema, precedence/reset rules,
native-variant boundary and existing-role transition have explicit answers. Record lasting decisions in proposal
decisions before acceptance. Development completes when AC-1 through AC-7 pass, the Living Spec and source bundle
agree, and required lint, type, affected-test and governance checks pass.
Follow the acceptance and handoff lifecycle in `CAP-DLV-proposal-incubation`.
