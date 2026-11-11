---
id: PROP-retire-legacy-integration-provider-key
title: Reject the legacy [integration] provider key
summary: Removes the code path that accepts and ignores a legacy [integration] provider key, so the retired readiness-provider selection leaves no reader, diagnostic or documentation behind.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/integration/
priority: low                         # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/integration/
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

- **Q1**: Does any consumer repository still carry `[integration] provider` (check the known consumers' config)?
- **Q2**: Should `[integration]` stay in the reserved-table list as a namespace reservation?

## 3. Proposed Design & Impact

- Drop the legacy acceptance so the key is an unknown setting.
- Remove CAP-INT-mcp-services §5 "Legacy configuration" and the CAP-DLV-project-policy sentence.
- Keep the reserved-table entry if Q2 says so. Tests change with it.

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
