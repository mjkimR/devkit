---
id: PROP-language-setting-coverage
title: Extend language settings to MCP approval content
summary: "Evaluate a shared language preference beyond response-style, including which MCP approval content devkit can localize and which UI elements remain controlled by Codex CLI or Claude Code."
status: draft
created_at: 2026-10-20
target_area: host/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/
    - docs/capabilities/host/
    - docs/capabilities/integration/
  excludes:
    - packages/devkit-advisory/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-language-setting-coverage] Extend language settings to MCP approval content

## 1. Background & Hypothesis

Language preference currently targets response-style guidance. Other user-facing content, especially native MCP
approval forms, may remain in a different language. A consistent preference could cover devkit-authored approval
messages and form labels, but the actual rendering boundary depends on the host client. The feasibility of a fully
localized approval screen is not established.

This is a follow-up to `SPEC-local-config-execution-environment` and `PROP-standalone-devkit-mcp`, not an expansion
of their implementation scope. Reuse their effective configuration and MCP runtime contracts when available.
The broad existing `packages/` boundary accommodates the future MCP package location; Planning must narrow it to
actual configuration, language rendering, approval content and response-style owners before Development.

## 2. Technical Spike Questions

- **Q1: Language ownership.** Decide whether a shared preference replaces or feeds the response-style-specific
  setting, how per-consumer overrides work, and which user-facing surfaces have a concrete need. Define supported
  language identifiers, absent/unsupported preference behavior and local-config precedence without creating a
  speculative product-wide localization framework.
- **Q2: Protocol and rendering.** Inspect the actual MCP elicitation request and current official Codex CLI and
  Claude Code documentation/implementations. Identify which message, field title, description, enum-label and
  validation elements are supplied by devkit and which buttons, chrome or errors belong to the client. Determine
  whether each client displays the supplied text unchanged, transforms it or omits fields.
- **Q3: Evidence.** Capture minimal representative approval forms in both supported CLIs where available, using
  harmless non-mutating examples. Record exact client/runtime versions and separate SDK/protocol evidence from
  actual visible UI evidence. An unavailable live client remains an explicit verification gap, not proof that
  localization works. Do not infer screen behavior from the JSON schema alone.
- **Q4: Approval integrity.** Keep source/target identifiers, paths, command arguments, stable codes and schema
  values unchanged while translating human-readable descriptions. Preserve the exact scope, consequences and
  available choices; determine deterministic translation ownership and fallback behavior.
- **Q5: Bounded extension.** Start with integration and handoff approval content. Inventory other language-sensitive
  surfaces but include them only with a concrete consumer and acceptance checks. Repository documentation language
  and machine-readable agent output contracts are separate from user-interface language.

## 3. Proposed Design & Impact

Planning should recommend the smallest supported extension of the language preference. Prefer localizing the
content devkit actually owns; clearly disclose client-owned UI that remains outside its control. Consider how a
shared preference reaches the extracted MCP runtime and domain-provided confirmation content without moving
integration or handoff business logic into the transport package.

Expected acceptance evidence for a selected design:

- The selected language reaches devkit-owned integration and handoff approval messages and the supported form
  labels. User-facing output preserves all decision-relevant scope and consequences.
- Native buttons, window chrome and host errors are documented according to observed ownership and client behavior;
  no claim of whole-screen localization is made when only supplied content changes.
- Missing or unsupported language follows a deterministic fallback, and existing response-style preferences remain
  coherent with the chosen shared-setting contract.
- Approval/schema values, identifiers and stable machine codes remain exact. Decline, cancel and missing native
  capability preserve their current authorization behavior independent of language.
- Tests verify translated content and language routing; actual-host evidence separately verifies visible rendering
  for the supported Codex CLI and Claude Code versions, or records the remaining gap before claiming support.

Scope excluded: modifying host-owned UI or trust settings, VS Code/SDK/desktop host support, translating repository
specifications, changing approval authority, broad automatic translation services and unrelated localization work.
Supporting SDK checks may be used as protocol evidence but do not add SDK-host product support.

## 4. Lifecycle & Retirement Criteria

Keep this as a queued draft until selected for Planning. First verify the two CLI clients' rendering boundaries;
then decide feasible coverage and implementation effort using the configuration and MCP package designs.
If only supplied approval content can be localized, present that bounded outcome explicitly for acceptance.
Draft registration neither starts this research nor authorizes implementation or changes to existing host settings.
