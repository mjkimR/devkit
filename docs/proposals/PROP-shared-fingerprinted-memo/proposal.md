---
id: PROP-shared-fingerprinted-memo
title: One fingerprinted memo store for docs parse and rule facts
summary: Joins the devkit-docs parse memo and the devkit-agt rule facts memo on one fingerprinted, path-safe memo helper, so envelope validation and path safety live once.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/governance/
priority: low                         # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-shared-fingerprinted-memo] One fingerprinted memo store for docs parse and rule facts

## 1. Background & Hypothesis

Two fingerprinted memos (the docs parse memo and the agt rule facts cache) each implement path safety and envelope
validation. Every hardening must be repeated in both. Source: `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md` X-9 (deferred: larger change; revisit with the
facts cache).

## 2. Technical Spike Questions

- **Q1**: Which layer can own the helper without a new forbidden edge (devkit-core is the candidate)?
- **Q2**: Do the two memos' invalidation and schema rules differ in ways a shared helper must keep apart?

## 3. Proposed Design & Impact

- Extract the shared memo envelope (fingerprint, schema version, path safety, malformed-entry handling) into one helper.
- Keep each memo's content and invalidation rules local. Use differential tests over both corpora.
- Behavior-preserving refactor, routed as a refactor work item once accepted.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr shared-fingerprinted-memo "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept shared-fingerprinted-memo --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff shared-fingerprinted-memo.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
