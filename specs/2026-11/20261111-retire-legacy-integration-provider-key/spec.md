---
id: SPEC-retire-legacy-integration-provider-key
title: Reject the legacy [integration] provider key
summary: Removes the code path that accepts and ignores a legacy [integration] provider key, so the retired readiness-provider selection leaves no reader, diagnostic or documentation behind.
status: planned
created: 2026-11-11
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-retire-legacy-integration-provider-key] Reject the legacy [integration] provider key

## 1. Problem Statement & Motivation

Handed off from proposal PROP-retire-legacy-integration-provider-key on 2026-11-11.
- **Preserved Materials**: `docs/materials/2026-11/20261111-retire-legacy-integration-provider-key`

### 1. Background & Hypothesis

`[integration]` now accepts only an ignored legacy `provider` key (`devkit_agt/features/integration/services/providers.py`,
added 2026-11-04). The guidance sentences about it were removed in the guidance run (G1-11, G3-10), and
`devkit config template --print` documents no `[integration]` table. The reader, its error text and CAP text remain
for a key no consumer needs. Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` G3-10 (code part, deferred because the code surface was not selected).

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Reject the legacy [integration] provider key so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Does any consumer repository still carry `[integration] provider`? **Yes, one**: `resource-indexer`
  sets `provider = "spec"`; it pins devkit to rev `76bafbbb`, so it breaks only when it moves its pin
  (`docs/materials/2026-11/20261111-retire-legacy-integration-provider-key/legacy-key-inventory.md`). Settled by the user: reject now; `resource-indexer` is a pilot consumer
  that accepts the breakage and deletes the key when it next moves its pin.
- **Q2**: Should `[integration]` stay in the reserved-table list? **Yes** (settled in Planning): removing it makes
  devkit-dist reject the table on every configuration read instead of only in `devkit integration`, and it changes
  devkit-dist for a key it never reads. The table stays a reserved namespace that currently accepts no keys.

### 3. Proposed Design & Impact

- `effective()` in `devkit_agt/features/integration/services/providers.py` accepts `[integration]` only when absent or
  empty: any key, `provider` included, raises `INTEGRATION_CONFIG_INVALID`. The message names the key; for
  `provider` the fix says the readiness-provider selection is retired and the key is deleted. The `policy()` docstring
  drops the legacy sentence. The policy digest is unchanged (it already excluded `provider`).
- Living Spec: `CAP-INT-mcp-services` §5 states that `[integration]` MAY be absent or empty and every key, including
  the retired `provider`, raises `INTEGRATION_CONFIG_INVALID`; `CAP-DLV-project-policy` §3 drops the legacy
  sentence; `CAP-DLV-sdd-baseline-adoption` step 7 and `UC-adopt-sdd-from-adaptive-development` "Provider-free
  activation" drop the ignored legacy value (activation still needs no provider setting).
- Quick references: `docs/development/reference/integration.md` and the integration row of
  `packages/devkit/README.md` follow the CAP text.
- Tests: fixtures stop writing `provider = "fixture"`; a test proves `provider` is refused with the retirement fix,
  and the unknown-key test keeps its actionable fix.

#### Planning decisions

- Q2: keep `integration` in devkit-dist `RESERVED_TABLES`; devkit-dist and `docs/development/reference/distribution.md`
  do not change.
- Q1 (user): reject the legacy `provider` key now, with no deprecation period; the `INTEGRATION_CONFIG_INVALID` fix
  names the retired key and says to delete it. `resource-indexer` is a pilot consumer that accepts breakage: no
  compatibility handling and no consumer coordination.

#### Non-Goals

- No change to the `ready_provider` test fixtures or the exported `Readiness`/`Evidence` models: the fixtures guard
  the §4 content boundary and read no configuration.
- No edit of any consumer repository, no deprecation-warning period or new notice code, and no compatibility
  handling for `resource-indexer`.
- No new feature edge.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr retire-legacy-integration-provider-key "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept retire-legacy-integration-provider-key --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff retire-legacy-integration-provider-key.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->

