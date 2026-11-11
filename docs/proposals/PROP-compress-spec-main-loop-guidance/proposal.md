---
id: PROP-compress-spec-main-loop-guidance
title: Compress the spec guidance of the main development loop
summary: Shortens the spec guidance every development run reads (constitution, spec skill, sdd-spec-feature, worker contract and core references) conservatively, keeping each rule at one owner, after the peripheral pass shows which compression patterns hold.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/delivery/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-compress-spec-main-loop-guidance] Compress the spec guidance of the main development loop

## 1. Background & Hypothesis

A context-size check on 2026-11-11 measured the spec guidance an agent reads:
- Always loaded, about 3.4K tokens: root guide, skill and agent descriptions.
- `get-context` for every installed bundle, about 4K tokens.
- The documents of one development-worker pass, about 74KB (about 18K tokens).
- The Host orchestration set, about 68KB (about 17K tokens).

The main-loop set (about 105KB) is read on every development run and reread after compaction. Every file is within
the official Claude limits (`SKILL.md` under 500 lines; root guide under 200 lines). The risk is diluted attention
and the reread cost, not overflow. The guidance and CLI review-refactor run removed only duplicated and obsolete
text; it did not rewrite needed content shorter.

Hypothesis: rewriting the main-loop documents for density, with each rule kept at one owner, cuts their size
noticeably without changing agent behavior.

## 2. Technical Spike Questions

- **Q1**: Which compression patterns held in the peripheral pass (same date, the spec bundle's peripheral
  references, side skills and playbooks), and which feedback did they draw?
- **Q2**: What is the exact main-loop set, and in what order should it be done (smallest blast radius first)?
- **Q3**: Which pinned guidance tests guard main-loop rules? Where they break, do they show a lost rule, or only
  that the wording moved?

## 3. Proposed Design & Impact

- Scope: the spec constitution, the `spec` skill, `sdd-spec-feature`, the development-worker contract,
  envelope/worker-records/completion references, specify/plan/tasks/review/sync, delegate/orchestrate/integrate,
  and isolated-execution.
- Conservative mode:
  - one document per commit, so each can be reverted alone;
  - a retained-constraint map for every removed or merged sentence;
  - no new or relaxed rules;
  - a pinned test changes only after its rule is confirmed kept.
- No pre-built behavior evaluation: problems surface as feedback and the affected commit is reverted or repaired.
  Package versions stay unchanged.
- Report sizes before and after for each document.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr compress-spec-main-loop-guidance "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept compress-spec-main-loop-guidance --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff compress-spec-main-loop-guidance.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
