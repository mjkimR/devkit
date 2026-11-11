---
id: PROP-retire-legacy-integration-provider-key
title: Reject the legacy [integration] provider key
summary: Removes the code path that accepts and ignores a legacy [integration] provider key, so the retired readiness-provider selection leaves no reader, diagnostic or documentation behind.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/integration/
priority: low                         # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/integration/
    - capabilities/delivery/
    - usecases/delivery/
    - docs/development/reference/
    - packages/devkit/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-retire-legacy-integration-provider-key] Reject the legacy [integration] provider key

## 1. Background & Hypothesis

`[integration]` now accepts only an ignored legacy `provider` key (`devkit_agt/features/integration/services/providers.py`,
added 2026-11-04). The guidance sentences about it were removed in the guidance run (G1-11, G3-10), and
`devkit config template --print` documents no `[integration]` table. The reader, its error text and CAP text remain
for a key no consumer needs. Source: `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` G3-10 (code part, deferred because the code surface was not selected).

## 2. Technical Spike Questions

- **Q1**: Does any consumer repository still carry `[integration] provider`? **Yes, one**: `resource-indexer`
  sets `provider = "spec"`; it pins devkit to rev `76bafbbb`, so it breaks only when it moves its pin
  (`materials/legacy-key-inventory.md`). How to treat it is the open user decision (see Planning decisions).
- **Q2**: Should `[integration]` stay in the reserved-table list? **Yes** (settled in Planning): removing it makes
  devkit-dist reject the table on every configuration read instead of only in `devkit integration`, and it changes
  devkit-dist for a key it never reads. The table stays a reserved namespace that currently accepts no keys.

## 3. Proposed Design & Impact

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

### Planning decisions

- Q2: keep `integration` in devkit-dist `RESERVED_TABLES`; devkit-dist and `docs/development/reference/distribution.md`
  do not change.
- Pending user decision (q1): treatment of the one consumer still carrying the key.

### Non-Goals

- No change to the `ready_provider` test fixtures or the exported `Readiness`/`Evidence` models: the fixtures guard
  the §4 content boundary and read no configuration.
- No edit of any consumer repository; no deprecation-warning period unless the user chooses it.
- No new feature edge.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr retire-legacy-integration-provider-key "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept retire-legacy-integration-provider-key --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff retire-legacy-integration-provider-key.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
