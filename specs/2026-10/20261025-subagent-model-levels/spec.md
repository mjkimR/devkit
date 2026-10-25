---
id: SPEC-subagent-model-levels
title: Host-neutral subagent model levels and project overrides
summary: "Resolves opt-in subagent model levels for three hosts during distribution, with shared project overrides and inherited defaults."
status: completed
created: 2026-10-25
related_capabilities: [CAP-DIST-agent-projections, CAP-DIST-sync-and-transactions, CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-subagent-model-levels] Host-neutral subagent model levels and project overrides

## 1. Problem Statement & Motivation

Subagent role contracts accept native model settings but cannot select portable model levels or project-wide
mapping overrides. Implement `ADR-subagent-level-projection` and the settled design retained in
`docs/materials/2026-10/20261025-subagent-model-levels/configuration-design.md`.

## 2. User Stories

- **US-1**: As a bundle author, I select an optional subagent level without duplicating host settings.
- **US-2**: As a project owner, I override level selection and native mappings without replacing role prompts.
- **US-3**: As a caller, I receive deterministic offline validation and native projections that inherit by default.

## 3. Non-Goals

**Scope Excluded**: Runtime launching, model availability or credential probes, automatic benchmarking, additional
hosts, checkout-local subagent policy, custom levels, raw per-role model settings, conversation-history controls,
changes to role permissions, and tying model selection to delivery activity-effort.

## 4. Acceptance Criteria

### [AC-01] Inherited shipped defaults and native escape hatch

- **Given** unconfigured projects and shipped spec roles, or another common contract with explicit native settings.
- **When** roles are projected for each supported host.
- **Then** shipped roles emit no model/effort override or x-model-profile; authored native settings remain unchanged
  unless an explicit project selection replaces them.

### [AC-02] Neutral source levels and built-in host mappings

- **Given** a common contract with level inherit, light, standard or deep.
- **When** rendering each host.
- **Then** inherit emits neither field; light/standard/deep use Claude haiku/low, sonnet/medium, opus/high;
  Codex gpt-6-luna/low, gpt-6.1-sol/medium, gpt-6-astra/high; Antigravity flash, pro, pro without effort.

### [AC-03] Partial mapping overrides and explicit field reset

- **Given** shared subagents.levels mappings with model/effort fields omitted, overridden or set to inherit.
- **When** a selected level resolves.
- **Then** omitted fields retain built-ins; inherit omits that field; supplied values replace built-ins. Other
  levels/hosts remain unchanged. Changing model alone retains default effort subject to exact known constraints.

### [AC-04] Selection precedence and shared-only configuration

- **Given** source levels, an optional project default and bundle-qualified role overrides.
- **When** resolving policy.
- **Then** role override wins over explicit project default, source level and implicit inheritance, in that order.
  Explicit inherit clears lower-precedence model and effort. Commented templates activate no defaults.
  Checkout-local subagents settings fail with CONFIG_LOCAL_KEY_FORBIDDEN.

### [AC-05] Deterministic invalid-input preflight

- **Given** invalid levels/keys/types, malformed role identities, unknown installed bundles, selected missing roles,
  conflicting source level/native settings, unsupported tiers/effort or exact known incompatible Codex pairs.
- **When** validating sources or planning sync.
- **Then** source errors are BUNDLE_INVALID; project errors are CONFIG_INVALID with INPUT_ERROR before writes.
  Antigravity model accepts flash/pro/inherit only. Effort accepts Claude low/medium/high/xhigh/max,
  Codex none/low/medium/high/xhigh/max and field reset inherit; Antigravity accepts reset inherit only.
  Exact Sol/Astra reject none. Opaque Claude/Codex IDs and provider-dependent aliases are not availability checks.

### [AC-06] Sync lifecycle and receipts

- **Given** mapping changes and repeat sync, dry-run or status calls.
- **When** computing desired output.
- **Then** the same policy determines projection bytes and receipt hashes; repeated sync is idempotent; returning
  to inheritance removes stale owned fields; foreign files and unrelated configuration remain unchanged.

### [AC-07] Common contracts, variants and dormant entries

- **Given** ordinary or templated common contracts, native variants, unsupported host blocks and dormant config.
- **When** building inventory.
- **Then** common forms resolve identically; unsupported hosts emit no file; variants remain verbatim and ignore
  global defaults. Role overrides targeting variants in selected bundles fail even outside a preset. Installed
  unselected bundles and excluded common assets retain dormant role settings; malformed mappings always fail.
  Bundle plan uses built-in/source policy without project reads; role permissions and prompts are preserved.
