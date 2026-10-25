---
id: SPEC-five-subagent-levels
title: Five neutral subagent levels and compact scout default
summary: "Defines five model-family presets with inherited effort between bounded extremes, preserves default inheritance and selects compact for the SDD scout."
status: completed
created: 2026-10-25
related_capabilities:
  - CAP-DIST-agent-projections
  - CAP-DIST-sync-and-transactions
  - CAP-DLV-delivery-workflows
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-five-subagent-levels] Five neutral subagent levels and compact scout default

## 1. Problem Statement & Motivation

The neutral levels in `CAP-DIST-agent-projections` combine model-family and effort changes. The desired presets
separate a small model at low effort from the same model with inherited effort, and a large model with inherited
effort from the same model at high effort. The default remains native inheritance. The SDD scout is the only
shipped role that selects a model level.

## 2. User Stories

- **US-1**: As a project agent, I choose a named preset without confusing its name with native effort tokens.
- **US-2**: As a bundle consumer, I get a compact scout while other SDD roles inherit session settings.
- **US-3**: As a project owner, I override the preset mapping and explicitly reset fields through shared config.

## 3. Non-Goals

1. **Scope Excluded**: Runtime launchers, prompt-based model/effort emulation and host-global settings.
2. **Scope Excluded**: Automatic aliases or migrations for the removed neutral name light.
3. **Scope Excluded**: Applying additional model settings to other SDD roles; they are recommendations only.
4. **Scope Excluded**: Provider availability, credential probes and live native subagent execution.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Five presets and default inheritance
- **Given** a common role and no explicit model policy
- **When** its settings are resolved
- **Then** devkit preserves native inheritance and accepts only inherit, minimal, compact, standard, deep and maximal
  as neutral selection values; the obsolete light name fails with CONFIG_INVALID or BUNDLE_INVALID at its owner.

### [AC-02] Claude Code and Codex mappings
- **Given** each explicit non-inherit preset on Claude Code or Codex
- **When** native role files are rendered
- **Then** model and effort equal the following table, and inherited effort emits no effort field.

| Preset | Claude Code model / effort | Codex model / effort |
| --- | --- | --- |
| minimal | haiku / low | gpt-6-luna / low |
| compact | haiku / inherited | gpt-6-luna / inherited |
| standard | sonnet / inherited | gpt-6.1-sol / inherited |
| deep | opus / inherited | gpt-6-astra / inherited |
| maximal | opus / high | gpt-6-astra / high |

### [AC-03] Compact scout and otherwise inherited shipped roles
- **Given** the shipped spec bundle without project overrides
- **When** its six roles are rendered
- **Then** only scout declares level compact, selecting Haiku, Luna or Flash with effort omitted; other roles
  contain no neutral level or fixed model/effort fields. Role prompts, tools, permissions and Git boundaries stay.

### [AC-04] Shared override and reset semantics
- **Given** role overrides, an explicit project default, source presets and partial host mappings
- **When** configuration is resolved and synchronized
- **Then** precedence and omission/reset behavior remain as defined by CAP-DIST-sync-and-transactions, including
  project inherit overriding scout's compact preset; template refresh adds comments without activating a default.

### [AC-05] Projection lifecycle and preflight
- **Given** valid or invalid preset changes
- **When** status, dry-run, bundle plan or sync is called
- **Then** valid projections have deterministic receipt hashes and repeated sync is idempotent; invalid policy
  fails before file writes, and native variants, dormant selections and unsupported host blocks keep their contracts.

### [AC-06] Native Antigravity inheritance fallback
- **Given** a built-in preset on Antigravity
- **When** its native settings are rendered
- **Then** compact emits model flash with effort omitted; minimal, standard, deep and maximal emit neither model
  nor effort. The entire unsupported combination inherits, without Argon/Pro substitution, fabricated effort or
  warning spam. Explicit project mappings retain strict existing native model/effort validation.

## 5. Native Capability Evidence and Scope Decision

The user selects whole-combination inheritance for built-in Antigravity presets that cannot be expressed natively.
The official custom-subagent schema and inspected agy 1.4.7 validator accept native tiers rather than Argon/session
slugs; no role effort field is established. This fallback does not relax invalid explicit project configuration.

- https://www.antigravity.google/docs/subagents/#frontmatter-configuration-yaml
- https://www.antigravity.google/docs/cli/headless/#select-a-model-effort-or-agent

No provider call or native subagent execution is part of the evidence. User correction settles the scope directly;
there are no unanswered business questions.
